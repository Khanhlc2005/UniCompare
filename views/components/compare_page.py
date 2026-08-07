"""Trang So sánh (Compare) — Issue 1.8 + 2.8 + 3.3.

Kế thừa ttk.Frame(master, controller) đúng Frame contract (ARCHITECTURE.md
mục 5.1). `refresh()` được AppShell gọi mỗi lần frame được tkraise() lên,
đọc lại compare_service để đồng bộ khi vừa thêm/bớt trường ở Watchlist/
Search/Detail rồi quay lại đây - không tự giữ list trường riêng trong View.

Issue 2.8: highlight ô giá trị tốt nhất mỗi tiêu chí (bootstyle="success",
logic xác định "tốt nhất" nằm ở compare_service.xac_dinh_tot_nhat - View chỉ
đọc kết quả để tô màu, không tự so sánh) + nút x trên chip bỏ trường (đã có
sẵn từ Issue 1.8 qua CompareChip.on_remove, giữ nguyên). CHƯA làm
StickyCompareBar (Issue 2.9).

Issue 3.3 (chốt §5.2.1, đợt polish sau đổi lại bố cục theo mock-up mới):
KHÔNG còn tách tab "Bảng"/"Biểu đồ" nữa - gộp chung 1 trang: bảng tiêu chí
truớc, "Trực quan hoá" (2 chart) ngay dưới, 2 chart nằm NGANG hàng (trước
xếp dọc). Mỗi trường có 1 màu cố định (chấm màu trước tên trong bảng,
dùng lại đúng màu đó cho cột/bar cua truong trong chart hoc phi) - lay tu
bang mau categorical co dinh MAU_THEO_THU_TU, KHONG tu bia mau/doi thu tu
theo filter (xem dataviz skill: "color follows the entity, never rank").
Van giu dung 2 chart cu, khong doi field/logic tinh toan:
  1. Học phí/năm (tuition_vnd, quy về TRIỆU VND) - bar NGANG (tên trường
     dài, bar đứng phải xoay nhãn khó đọc).
  2. Yêu cầu ngoại ngữ (ielts_min + toefl_min) - grouped bar, 2 trục y
     (ax.twinx()): IELTS trục trái cố định set_ylim(0, 9), TOEFL trục phải
     cố định set_ylim(0, 120) - KHÔNG để matplotlib tự scale.

"""

import ttkbootstrap as tb
from pymongo.errors import PyMongoError

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from repositories.mongo_repo import MongoRepositoryError
from services import compare_service
from views.components.scrollable_frame import ScrollableFrame
from views.components.compare_chip import CompareChip
from views.components.state_banner import StateBanner

# he so quy doi tuition_vnd (VND nguyen, vi du 91_000_000) ve don vi TRIEU
# hien tren truc x cua chart hoc phi (dai thuc te ~91 den ~1.490 trieu)
TRIEU_VND = 1_000_000

# mau categorical co dinh theo THU TU truong duoc chon (khong theo rank/gia
# tri) - lay 5 slot dau cua bang mau da validate CVD-safe (dataviz skill,
# references/palette.md), du cho MAX_COMPARE=5
MAU_THEO_THU_TU = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]

# tieu chi hien trong bang - key phai khop CAC_TIEU_CHI_SO trong
# compare_service.py de tra cuu ket qua highlight. "ranking" chi co o schema
# chuan/seed_data.json, fake_repo hien chua co field nay nen se hien N/A cho
# toi khi doi sang mongo_repo (Issue 2.3) - khong crash, chi khong highlight.
CRITERIA = [
    ("country", "Quốc gia"),
    ("ranking", "Xếp hạng"),
    ("tuition", "Học phí/năm"),
    ("gpa", "GPA yêu cầu"),
    ("ielts", "IELTS yêu cầu"),
]


def _doc_gia_tri_hien_thi(uni, field):
    # "country" khong phai tieu chi so nen khong qua doc_gia_tri_tieu_chi
    # (ham do chi doc field so, tra None cho string)
    if field == "country":
        return uni.get("country")
    return compare_service.doc_gia_tri_tieu_chi(uni, field)


class ComparePage(tb.Frame):
    """Trang So sánh — chip trường đã chọn + bảng tiêu chí + 2 chart (nằm chung 1 trang)."""

    def __init__(self, master, controller):
        super().__init__(master)
        self._controller = controller
        self._colors = tb.Style().colors

        self._scroll = ScrollableFrame(self)
        self._scroll.pack(fill="both", expand=True)

    def refresh(self, **kwargs):
        """AppShell goi moi lan man nay duoc dua len - doc lai state moi nhat."""
        self._render()

    def _get_compare_data(self):
        data = []
        for uid in compare_service.get_compare_ids():
            uni = self._controller.repo.get_by_id(uid)
            if uni:
                data.append(uni)
        return data

    def _render(self):
        for w in self._scroll.body.winfo_children():
            w.destroy()

        tb.Label(
            self._scroll.body, text="So sánh", bootstyle="primary",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=28, pady=(20, 12))

        try:
            data = self._get_compare_data()
        except (MongoRepositoryError, PyMongoError) as exc:
            StateBanner.mongo_error(self._scroll.body, exc).pack(
                fill="x", padx=28, pady=20
            )
            return

        if len(data) < 2:
            self._build_empty_state(
                "Chọn ít nhất 2 trường để so sánh.\n"
                "Vào Quan tâm hoặc Tìm kiếm để tick \"So sánh\"."
            )
            return

        # moi truong 1 mau co dinh theo thu tu chon (khong doi khi filter/
        # sap xep khac) - dung chung giua bang va chart hoc phi ben duoi
        mau_theo_truong = {
            uni["id"]: MAU_THEO_THU_TU[i % len(MAU_THEO_THU_TU)]
            for i, uni in enumerate(data)
        }

        self._build_chip_row(data)
        self._build_table(self._scroll.body, data, mau_theo_truong)
        self._build_chart_section(self._scroll.body, data, mau_theo_truong)

    def _build_empty_state(self, message):
        StateBanner(self._scroll.body, message, icon="📊").pack(
            fill="x", padx=28, pady=20
        )

    def _build_chip_row(self, data):
        row = tb.Frame(self._scroll.body)
        row.pack(fill="x", padx=28, pady=(0, 16))
        for uni in data:
            chip = CompareChip(
                row, text=uni.get("name", ""),
                on_remove=lambda uid=uni["id"]: self._remove(uid)
            )
            chip.pack(side="left", padx=(0, 8), pady=4)

    def _build_table(self, parent, data, mau_theo_truong):
        table = tb.Frame(parent, bootstyle="light", padding=16)
        table.pack(fill="x", padx=28, pady=(0, 16))

        # cot dau la ten tieu chi, cac cot sau la tung truong dang chon
        for col in range(len(data) + 1):
            table.columnconfigure(col, weight=1, uniform="compare")

        tb.Label(
            table, text="Tiêu chí", font=("Segoe UI", 10, "bold"),
            foreground=self._colors.secondary
        ).grid(row=0, column=0, sticky="w", padx=8, pady=8)

        for col_idx, uni in enumerate(data, start=1):
            header = tb.Frame(table)
            header.grid(row=0, column=col_idx, sticky="w", padx=8, pady=8)
            # cham mau rieng cua truong - dung lai dung mau nay cho bar hoc
            # phi cua truong trong chart ben duoi, khong doi mau theo filter
            tb.Label(
                header, text="●", foreground=mau_theo_truong[uni["id"]],
                font=("Segoe UI", 10, "bold")
            ).pack(side="left", padx=(0, 4))
            tb.Label(
                header, text=uni.get("name", ""), font=("Segoe UI", 10, "bold"),
                foreground=self._colors.primary, wraplength=170, justify="left"
            ).pack(side="left")

        # logic xac dinh "tot nhat" nam o service layer (Issue 2.8), View chi
        # doc ket qua ve to mau, khong tu so sanh gia tri trong file nay
        tot_nhat = compare_service.xac_dinh_tot_nhat(data)

        for row_idx, (field, label) in enumerate(CRITERIA, start=1):
            tb.Label(
                table, text=label, foreground=self._colors.secondary
            ).grid(row=row_idx, column=0, sticky="w", padx=8, pady=8)

            id_tot_nhat = tot_nhat.get(field, set())

            for col_idx, uni in enumerate(data, start=1):
                value = _doc_gia_tri_hien_thi(uni, field)
                if value is None:
                    value = "N/A"
                elif field == "tuition":
                    value = f"${value:,.0f}"
                elif field == "ranking":
                    value = f"#{value:g}"

                la_tot_nhat = uni["id"] in id_tot_nhat
                tb.Label(
                    table, text=str(value),
                    bootstyle="success" if la_tot_nhat else "default",
                    font=("Segoe UI", 10, "bold") if la_tot_nhat else ("Segoe UI", 10),
                ).grid(row=row_idx, column=col_idx, sticky="w", padx=8, pady=8)

    # ─── Trực quan hoá (Issue 3.3, chốt §5.2.1 - gộp chung trang, 2 chart
    # nam ngang thay vi tach tab/xep doc nhu ban truoc) ────────────
    def _build_chart_section(self, parent, data, mau_theo_truong):
        tb.Label(
            parent, text="TRỰC QUAN HOÁ", bootstyle="secondary",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=28, pady=(4, 8))

        chart_frame = tb.Frame(parent, bootstyle="light", padding=16)
        chart_frame.pack(fill="both", expand=True, padx=28, pady=(0, 24))

        # 1 Figure duy nhat (khong dung matplotlib.pyplot de tranh giu
        # figure trong state global toan cuc khi nhung vao Tkinter - rui ro
        # leak bo nho khi mo/dong nhieu lan). 2 subplot nam NGANG (1 hang, 2
        # cot) thay vi xep doc nhu truoc, khop bo cuc "2 the canh nhau".
        fig = Figure(figsize=(13, 4.4), dpi=100)
        ax_hoc_phi, ax_ngoai_ngu = fig.subplots(1, 2)

        self._ve_chart_hoc_phi(ax_hoc_phi, data, mau_theo_truong)
        self._ve_chart_ngoai_ngu(ax_ngoai_ngu, data)

        fig.tight_layout(w_pad=4)

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw_idle()
        return canvas

    def _ve_chart_hoc_phi(self, ax, data, mau_theo_truong):
        """Chart 1 (§5.2.1): học phí/năm - tuition_vnd quy đổi triệu VND,
        bar NGANG vì tên trường dài. Trường thiếu tuition_vnd bị loại khỏi
        chart, tuyệt đối không vẽ cột 0. Moi bar 1 mau rieng theo truong,
        dung chung mau_theo_truong voi cham mau trong bang o tren."""
        cap = [
            (uni.get("name", ""), uni.get("tuition_vnd"), mau_theo_truong[uni["id"]])
            for uni in data
        ]
        ten = [n for n, v, _ in cap if isinstance(v, (int, float))]
        trieu = [v / TRIEU_VND for n, v, _ in cap if isinstance(v, (int, float))]
        mau = [m for n, v, m in cap if isinstance(v, (int, float))]
        thieu = [n for n, v, _ in cap if not isinstance(v, (int, float))]

        if trieu:
            ax.barh(ten, trieu, color=mau)
            ax.invert_yaxis()
            ax.set_xlabel("Triệu VND")
        else:
            ax.text(
                0.5, 0.5, "Không có dữ liệu học phí",
                ha="center", va="center", transform=ax.transAxes,
                color="#8A8A8A", fontsize=10,
            )
            ax.set_xticks([])
            ax.set_yticks([])
        ax.set_title("Học phí/năm (VND)")
        ax.tick_params(axis="y", labelsize=9)

        if thieu:
            ax.text(
                0.0, -0.18, f"N/A: {', '.join(thieu)}",
                transform=ax.transAxes, fontsize=8, color="#B00020",
            )

    def _ve_chart_ngoai_ngu(self, ax, data):
        """Chart 2 (§5.2.1): grouped bar IELTS (ielts_min) + TOEFL
        (toefl_min), 2 trục y cố định (ax.twinx()) - IELTS trục trái
        set_ylim(0, 9), TOEFL trục phải set_ylim(0, 120), KHÔNG để
        matplotlib tự scale. Trường thiếu 1 trong 2 field bị loại khỏi
        RIÊNG chart này (tuyệt đối không vẽ cột 0 cho field thiếu), ghi
        chú tên ở dòng N/A."""
        hop_le, thieu = [], []
        for uni in data:
            ielts = uni.get("ielts_min")
            toefl = uni.get("toefl_min")
            ten_truong = uni.get("name", "")
            if isinstance(ielts, (int, float)) and isinstance(toefl, (int, float)):
                hop_le.append((ten_truong, ielts, toefl))
            else:
                thieu.append(ten_truong)

        ax.set_title("Yêu cầu ngoại ngữ (IELTS / TOEFL)")

        if not hop_le:
            ax.text(
                0.5, 0.5, "Không có dữ liệu ngoại ngữ",
                ha="center", va="center", transform=ax.transAxes,
                color="#8A8A8A", fontsize=10,
            )
            ax.set_xticks([])
            ax.set_yticks([])
            if thieu:
                ax.text(
                    0.0, -0.18, f"N/A: {', '.join(thieu)}",
                    transform=ax.transAxes, fontsize=8, color="#B00020",
                )
            return

        ten = [n for n, _, _ in hop_le]
        diem_ielts = [i for _, i, _ in hop_le]
        diem_toefl = [t for _, _, t in hop_le]
        x = list(range(len(ten)))
        rong = 0.35

        ax_toefl = ax.twinx()

        # mau slot 1/3 cua bang mau categorical (khac voi mau_theo_truong o
        # chart hoc phi - o day mau phan biet IELTS/TOEFL, khong phai truong)
        ax.bar(
            [xi - rong / 2 for xi in x], diem_ielts, width=rong,
            color="#2a78d6", label="IELTS",
        )
        ax_toefl.bar(
            [xi + rong / 2 for xi in x], diem_toefl, width=rong,
            color="#1baf7a", label="TOEFL",
        )

        # truc co dinh, khong de matplotlib tu scale (§5.2.1)
        ax.set_ylim(0, 9)
        ax_toefl.set_ylim(0, 120)
        ax.set_ylabel("IELTS")
        ax_toefl.set_ylabel("TOEFL")

        ax.set_xticks(x)
        ax.set_xticklabels(ten, rotation=15, ha="right", fontsize=9)

        duong, nhan = ax.get_legend_handles_labels()
        duong2, nhan2 = ax_toefl.get_legend_handles_labels()
        ax.legend(duong + duong2, nhan + nhan2, loc="upper right", fontsize=8)

        if thieu:
            ax.text(
                0.0, -0.32, f"N/A: {', '.join(thieu)}",
                transform=ax.transAxes, fontsize=8, color="#B00020",
            )

    def _remove(self, uni_id):
        # toggle_compare voi id da co trong list se bo id do ra (Issue 1.6)
        compare_service.toggle_compare(uni_id)
        self._render()
