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

Issue 3.3 (chốt §5.2.1 — thay wireframe 6): tab "Biểu đồ" cạnh tab "Bảng"
(ttk.Notebook). ĐÃ BỎ dropdown chọn tiêu chí - luôn hiện CỐ ĐỊNH 2 chart
xếp dọc, cùng áp lên toàn bộ danh sách 2-5 trường đang so sánh:
  1. Học phí/năm (tuition_vnd, quy về TRIỆU VND) - bar NGANG (tên trường
     dài, bar đứng phải xoay nhãn khó đọc).
  2. Yêu cầu ngoại ngữ (ielts_min + toefl_min) - grouped bar, 2 trục y
     (ax.twinx()): IELTS trục trái cố định set_ylim(0, 9), TOEFL trục phải
     cố định set_ylim(0, 120) - KHÔNG để matplotlib tự scale.

"""

import ttkbootstrap as tb

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from services import compare_service
from views.components.scrollable_frame import ScrollableFrame
from views.components.compare_chip import CompareChip

# he so quy doi tuition_vnd (VND nguyen, vi du 91_000_000) ve don vi TRIEU
# hien tren truc x cua chart hoc phi (dai thuc te ~91 den ~1.490 trieu)
TRIEU_VND = 1_000_000

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
    """Trang So sánh — chip trường đã chọn + tab Bảng/Biểu đồ."""

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

        data = self._get_compare_data()

        if len(data) < 2:
            self._build_empty_state(
                "Chọn ít nhất 2 trường để so sánh.\n"
                "Vào Quan tâm hoặc Tìm kiếm để tick \"So sánh\"."
            )
            return

        self._build_chip_row(data)

        notebook = tb.Notebook(self._scroll.body)
        notebook.pack(fill="both", expand=True, padx=28, pady=(0, 24))

        tab_bang = tb.Frame(notebook)
        tab_bieu_do = tb.Frame(notebook)
        notebook.add(tab_bang, text="Bảng")
        notebook.add(tab_bieu_do, text="Biểu đồ")

        self._build_table(tab_bang, data)
        self._build_chart_tab(tab_bieu_do, data)

    def _build_empty_state(self, message):
        empty = tb.Frame(self._scroll.body, bootstyle="light", padding=40)
        empty.pack(fill="x", padx=28, pady=20)
        tb.Label(empty, text="📊", font=("Segoe UI", 32)).pack()
        tb.Label(
            empty, text=message, foreground=self._colors.secondary, justify="center"
        ).pack(pady=(10, 0))

    def _build_chip_row(self, data):
        row = tb.Frame(self._scroll.body)
        row.pack(fill="x", padx=28, pady=(0, 16))
        for uni in data:
            chip = CompareChip(
                row, text=uni.get("name", ""),
                on_remove=lambda uid=uni["id"]: self._remove(uid)
            )
            chip.pack(side="left", padx=(0, 8), pady=4)

    def _build_table(self, parent, data):
        table = tb.Frame(parent, bootstyle="light", padding=16)
        table.pack(fill="both", expand=True, padx=16, pady=16)

        # cot dau la ten tieu chi, cac cot sau la tung truong dang chon
        for col in range(len(data) + 1):
            table.columnconfigure(col, weight=1, uniform="compare")

        tb.Label(
            table, text="Tiêu chí", font=("Segoe UI", 10, "bold"),
            foreground=self._colors.secondary
        ).grid(row=0, column=0, sticky="w", padx=8, pady=8)

        for col_idx, uni in enumerate(data, start=1):
            tb.Label(
                table, text=uni.get("name", ""), font=("Segoe UI", 10, "bold"),
                foreground=self._colors.primary, wraplength=180, justify="left"
            ).grid(row=0, column=col_idx, sticky="w", padx=8, pady=8)

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

    # ─── tab Biểu đồ (Issue 3.3, chốt §5.2.1) ─────────────────────
    def _build_chart_tab(self, parent, data):
        chart_frame = tb.Frame(parent, padding=16)
        chart_frame.pack(fill="both", expand=True)

        # 1 Figure duy nhat, 2 subplot xep doc (khong dung matplotlib.pyplot
        # de tranh pyplot giu figure trong state global toan cuc khi nhung
        # vao Tkinter - rui ro leak bo nho khi mo/dong nhieu lan). Chi 1
        # FigureCanvasTkAgg, 1 lan draw_idle() o cuoi ham (khong tao 2
        # canvas rieng cho 2 chart).
        fig = Figure(figsize=(7, 7.6), dpi=100)
        ax_hoc_phi, ax_ngoai_ngu = fig.subplots(2, 1)

        self._ve_chart_hoc_phi(ax_hoc_phi, data)
        self._ve_chart_ngoai_ngu(ax_ngoai_ngu, data)

        fig.tight_layout(h_pad=3.5)

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw_idle()

    def _ve_chart_hoc_phi(self, ax, data):
        """Chart 1 (§5.2.1): học phí/năm - tuition_vnd quy đổi triệu VND,
        bar NGANG vì tên trường dài. Trường thiếu tuition_vnd bị loại khỏi
        chart, tuyệt đối không vẽ cột 0."""
        cap = [(uni.get("name", ""), uni.get("tuition_vnd")) for uni in data]
        ten = [n for n, v in cap if isinstance(v, (int, float))]
        trieu = [v / TRIEU_VND for n, v in cap if isinstance(v, (int, float))]
        thieu = [n for n, v in cap if not isinstance(v, (int, float))]

        if trieu:
            ax.barh(ten, trieu, color="#2F5DFF")
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

        ax.bar(
            [xi - rong / 2 for xi in x], diem_ielts, width=rong,
            color="#2F5DFF", label="IELTS",
        )
        ax_toefl.bar(
            [xi + rong / 2 for xi in x], diem_toefl, width=rong,
            color="#00A896", label="TOEFL",
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
