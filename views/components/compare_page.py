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
truớc, "Trực quan hoá" (2 chart) ngay dưới, 2 chart nằm NGANG hàng, MỖI
chart 1 khung viền vuông riêng chia đều 50/50 (2 Figure độc lập, không
còn 1 Figure 2-subplot chung như bản đầu - tách ra để mỗi chart tự
tight_layout(), không bị lệch margin khi tên trường ở chart kia quá dài).
Mỗi trường có 1 màu cố định (chấm màu trước tên trong bảng,
dùng lại đúng màu đó cho cột/bar cua truong trong chart hoc phi) - lay tu
bang mau categorical co dinh MAU_THEO_THU_TU, KHONG tu bia mau/doi thu tu
theo filter (xem dataviz skill: "color follows the entity, never rank").
Van giu dung 2 chart cu, khong doi field/logic tinh toan:
  1. Học phí/năm (tuition_vnd, quy về TRIỆU VND) - bar NGANG (tên trường
     dài, bar đứng phải xoay nhãn khó đọc).
  2. Yêu cầu ngoại ngữ (ielts_min + toefl_min) - grouped bar, đáy vuông và
     bo hai góc trên. Giữ trục X cùng hai trục Y cố định: IELTS 0-9 bên trái,
     TOEFL 0-120 bên phải; giá trị gốc nằm phía trên từng cột.

"""

import textwrap
import tkinter as tk

import ttkbootstrap as tb
from pymongo.errors import PyMongoError

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Rectangle

from repositories.mongo_repo import MongoRepositoryError
from services import compare_service, university_service
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

# The data table and charts intentionally share these values so Compare reads as
# one coherent surface rather than a table followed by unrelated chart cards.
COMPARE_CARD_BG = "#FFFFFF"
COMPARE_CARD_BORDER = "#D9DEE8"
CHART_TEXT = "#17236F"
CHART_MUTED = "#5E6A7D"
CHART_TRACK = "#DDE2E8"

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
            uni = university_service.get_by_id(self._controller.repo, uid)
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
        card = self._create_bordered_frame(parent)
        card.pack(fill="x", padx=28, pady=(0, 16))

        table = tk.Frame(card, bg=COMPARE_CARD_BG)
        table.pack(fill="both", expand=True, padx=16, pady=16)

        # cot dau la ten tieu chi, cac cot sau la tung truong dang chon
        for col in range(len(data) + 1):
            table.columnconfigure(col, weight=1, uniform="compare")

        tk.Label(
            table, text="Tiêu chí", font=("Segoe UI", 10, "bold"),
            fg=CHART_MUTED, bg=COMPARE_CARD_BG,
        ).grid(row=0, column=0, sticky="w", padx=8, pady=8)

        for col_idx, uni in enumerate(data, start=1):
            header = tk.Frame(table, bg=COMPARE_CARD_BG)
            header.grid(row=0, column=col_idx, sticky="w", padx=8, pady=8)
            # cham mau rieng cua truong - dung lai dung mau nay cho bar hoc
            # phi cua truong trong chart ben duoi, khong doi mau theo filter
            tk.Label(
                header, text="●", fg=mau_theo_truong[uni["id"]],
                bg=COMPARE_CARD_BG, font=("Segoe UI", 10, "bold")
            ).pack(side="left", padx=(0, 4))
            tk.Label(
                header, text=uni.get("name", ""), font=("Segoe UI", 10, "bold"),
                fg=CHART_TEXT, bg=COMPARE_CARD_BG, wraplength=170, justify="left"
            ).pack(side="left")

        # logic xac dinh "tot nhat" nam o service layer (Issue 2.8), View chi
        # doc ket qua ve to mau, khong tu so sanh gia tri trong file nay
        tot_nhat = compare_service.xac_dinh_tot_nhat(data)

        for row_idx, (field, label) in enumerate(CRITERIA, start=1):
            tk.Label(
                table, text=label, fg=CHART_MUTED, bg=COMPARE_CARD_BG,
            ).grid(row=row_idx, column=0, sticky="w", padx=8, pady=8)

            id_tot_nhat = tot_nhat.get(field, set())

            for col_idx, uni in enumerate(data, start=1):
                value = _doc_gia_tri_hien_thi(uni, field)
                if value is None:
                    value = "N/A"
                elif field == "tuition":
                    # moi truong co the dung don vi tien te khac nhau (VND/
                    # CNY/JPY/...), khong duoc hard-code $ (xem uni["currency"])
                    currency = uni.get("currency", "USD")
                    value = f"{value:,.0f} {currency}"
                elif field == "ranking":
                    value = f"#{value:g}"

                la_tot_nhat = uni["id"] in id_tot_nhat
                tk.Label(
                    table, text=str(value), bg=COMPARE_CARD_BG,
                    fg="#008C8C" if la_tot_nhat else "#202A3A",
                    font=("Segoe UI", 10, "bold") if la_tot_nhat else ("Segoe UI", 10),
                ).grid(row=row_idx, column=col_idx, sticky="w", padx=8, pady=8)

    # ─── Trực quan hoá (Issue 3.3, chốt §5.2.1 - gộp chung trang, 2 chart
    # nam ngang thay vi tach tab/xep doc nhu ban truoc) ────────────
    @staticmethod
    def _create_bordered_frame(parent):
        return tk.Frame(
            parent, bg=COMPARE_CARD_BG, bd=0,
            highlightbackground=COMPARE_CARD_BORDER,
            highlightcolor=COMPARE_CARD_BORDER,
            highlightthickness=1,
        )

    def _build_chart_section(self, parent, data, mau_theo_truong):
        tb.Label(
            parent, text="TRỰC QUAN HOÁ", bootstyle="secondary",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=28, pady=(4, 8))

        # 2 khung rieng, chia deu 50/50 (columnconfigure weight bang nhau)
        # thay vi 1 khung to chua chung 1 Figure 2-subplot nhu truoc - moi
        # chart co Figure/tight_layout rieng nen khong con canh tranh margin
        # voi nhau (ly do gay lech bo cuc khi ten truong dai o ban truoc)
        charts_row = tb.Frame(parent)
        charts_row.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        charts_row.columnconfigure(0, weight=1, uniform="chart_col")
        charts_row.columnconfigure(1, weight=1, uniform="chart_col")
        charts_row.rowconfigure(0, weight=1, minsize=380)

        card_hoc_phi = self._create_bordered_frame(charts_row)
        card_hoc_phi.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        card_ngoai_ngu = self._create_bordered_frame(charts_row)
        card_ngoai_ngu.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # khong dung matplotlib.pyplot de tranh giu figure trong state
        # global toan cuc khi nhung vao Tkinter - rui ro leak bo nho khi
        # mo/dong nhieu lan (ap dung cho ca 2 Figure duoi day)
        fig_hoc_phi = Figure(figsize=(6.2, 4.2), dpi=100, facecolor=COMPARE_CARD_BG)
        ax_hoc_phi = fig_hoc_phi.add_subplot(111)
        self._ve_chart_hoc_phi(ax_hoc_phi, data, mau_theo_truong)
        fig_hoc_phi.subplots_adjust(left=0.08, right=0.94, top=0.92, bottom=0.10)

        canvas_hoc_phi = FigureCanvasTkAgg(fig_hoc_phi, master=card_hoc_phi)
        canvas_hoc_phi.get_tk_widget().configure(highlightthickness=0, bg=COMPARE_CARD_BG)
        canvas_hoc_phi.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=14)
        canvas_hoc_phi.draw_idle()

        fig_ngoai_ngu = Figure(figsize=(6.2, 4.2), dpi=100, facecolor=COMPARE_CARD_BG)
        ax_ngoai_ngu = fig_ngoai_ngu.add_subplot(111)
        self._ve_chart_ngoai_ngu(ax_ngoai_ngu, data)
        # Keep the axes compact around the bars and reserve a dedicated strip
        # on the right for the legend. Lower top leaves room for the title.
        fig_ngoai_ngu.subplots_adjust(
            left=0.10, right=0.74, top=0.80, bottom=0.18
        )

        canvas_ngoai_ngu = FigureCanvasTkAgg(fig_ngoai_ngu, master=card_ngoai_ngu)
        canvas_ngoai_ngu.get_tk_widget().configure(highlightthickness=0, bg=COMPARE_CARD_BG)
        canvas_ngoai_ngu.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=14)
        canvas_ngoai_ngu.draw_idle()

    @staticmethod
    def _prepare_chart_axes(ax):
        """Give embedded charts the same quiet, card-like visual language."""
        ax.set_facecolor(COMPARE_CARD_BG)
        ax.set_axis_off()

    @staticmethod
    def _add_rounded_bar(ax, x, y, width, height, color, orientation):
        """Draw a pill bar with round caps measured in screen points.

        A FancyBboxPatch radius expressed in data units distorts when x and y
        use different scales. A thick line keeps the radius stable on resize.
        """
        if orientation == "horizontal":
            ax.plot(
                [x, x + width], [y + height / 2, y + height / 2],
                color=color, linewidth=11, solid_capstyle="round",
                zorder=2,
            )
        else:
            ax.plot(
                [x + width / 2, x + width / 2], [y, y + height],
                color=color, linewidth=17, solid_capstyle="round",
                zorder=2,
            )

    @staticmethod
    def _short_chart_label(name):
        return textwrap.fill(name, width=12, max_lines=2, placeholder="...")

    @staticmethod
    def _single_line_chart_label(name):
        return textwrap.shorten(name, width=30, placeholder="...")

    @staticmethod
    def _add_top_rounded_column(ax, x, bottom, width, height, color):
        """Draw a column with a square base and only its top corners rounded."""
        if height <= 0:
            return
        radius_x = min(width * 0.32, width / 2)
        axis_span = abs(ax.get_ylim()[1] - ax.get_ylim()[0]) or 1
        radius_y = min(height * 0.12, axis_span * 0.025)
        top = bottom + height
        right = x + width
        vertices = [
            (x, bottom),
            (right, bottom),
            (right, top - radius_y),
            (right, top),
            (right - radius_x, top),
            (x + radius_x, top),
            (x, top),
            (x, top - radius_y),
            (x, bottom),
            (x, bottom),
        ]
        codes = [
            Path.MOVETO,
            Path.LINETO,
            Path.LINETO,
            Path.CURVE3,
            Path.CURVE3,
            Path.LINETO,
            Path.CURVE3,
            Path.CURVE3,
            Path.LINETO,
            Path.CLOSEPOLY,
        ]
        ax.add_patch(PathPatch(
            Path(vertices, codes), facecolor=color, edgecolor="none", zorder=3
        ))

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

        self._prepare_chart_axes(ax)
        ax.text(
            0.0, 0.98, "Học phí ước tính (Triệu VND)",
            transform=ax.transAxes, ha="left", va="top", color=CHART_TEXT,
            fontsize=10, fontweight="bold",
        )

        if not trieu:
            ax.text(
                0.5, 0.5, "Không có dữ liệu học phí",
                ha="center", va="center", transform=ax.transAxes,
                color="#8A8A8A", fontsize=10,
            )
            return

        maximum = max(trieu)
        track_width = maximum * 1.08 if maximum else 1
        value_x = track_width * 1.035
        ax.set_xlim(-track_width * 0.015, track_width * 1.25)
        ax.set_ylim(len(trieu) + 0.15, -1.15)

        for index, (name, value, color) in enumerate(zip(ten, trieu, mau)):
            row_y = index + 0.35
            ax.text(
                0, row_y - 0.27, self._single_line_chart_label(name),
                ha="left", va="bottom", color=CHART_MUTED, fontsize=8,
            )
            self._add_rounded_bar(
                ax, 0, row_y, track_width, 0.16, CHART_TRACK, "horizontal"
            )
            self._add_rounded_bar(
                ax, 0, row_y, value, 0.16, color, "horizontal"
            )
            ax.text(
                value_x, row_y + 0.08, f"{value:,.1f}", ha="left", va="center",
                color="#4B5565", fontsize=8, fontweight="bold",
            )

        if thieu:
            ax.text(
                0.0, 0.01, f"N/A: {', '.join(thieu)}",
                transform=ax.transAxes, fontsize=7, color="#B00020",
            )

    def _ve_chart_ngoai_ngu(self, ax, data):
        """Chart 2 (§5.2.1): grouped bar IELTS (ielts_min) + TOEFL.
        Giữ trục X và hai trục Y cố định IELTS 0-9/TOEFL 0-120; cột có đáy
        vuông, bo hai góc trên và giá trị nằm phía trên. Trường thiếu một
        trong hai field bị loại riêng khỏi chart và được ghi chú N/A."""
        hop_le, thieu = [], []
        for uni in data:
            ielts = uni.get("ielts_min")
            toefl = uni.get("toefl_min")
            ten_truong = uni.get("name", "")
            if isinstance(ielts, (int, float)) and isinstance(toefl, (int, float)):
                hop_le.append((ten_truong, ielts, toefl))
            else:
                thieu.append(ten_truong)

        if not hop_le:
            self._prepare_chart_axes(ax)
            ax.text(
                0.0, 0.98, "Yêu cầu ngoại ngữ", transform=ax.transAxes,
                ha="left", va="top", color=CHART_TEXT,
                fontsize=10, fontweight="bold",
            )
            ax.text(
                0.5, 0.5, "Không có dữ liệu ngoại ngữ",
                ha="center", va="center", transform=ax.transAxes,
                color="#8A8A8A", fontsize=10,
            )
            if thieu:
                ax.text(
                    0.0, 0.01, f"N/A: {', '.join(thieu)}",
                    transform=ax.transAxes, fontsize=7, color="#B00020",
                )
            return

        ten = [n for n, _, _ in hop_le]
        diem_ielts = [i for _, i, _ in hop_le]
        diem_toefl = [t for _, _, t in hop_le]
        group_count = len(ten)
        ax.set_facecolor(COMPARE_CARD_BG)
        ax_toefl = ax.twinx()
        ax_toefl.set_facecolor("none")

        # The axes stop just outside the first/last bar groups. The legend uses
        # figure coordinates in the separate strip reserved by subplots_adjust.
        ax.set_xlim(-0.55, group_count - 0.45)
        ax.set_ylim(0, 9)
        ax_toefl.set_ylim(0, 120)
        ax.set_title(
            "Yêu cầu ngoại ngữ", loc="left", pad=12,
            color=CHART_TEXT, fontsize=10, fontweight="bold",
        )
        ax.set_ylabel("IELTS", color="#2A78D6", fontsize=8)
        ax_toefl.set_ylabel("TOEFL", color="#008C8C", fontsize=8)
        ax.set_yticks([0, 3, 6, 9])
        ax_toefl.set_yticks([0, 40, 80, 120])
        ax.tick_params(axis="y", colors="#2A78D6", labelsize=7, length=3)
        ax_toefl.tick_params(axis="y", colors="#008C8C", labelsize=7, length=3)
        ax.tick_params(axis="x", colors=CHART_TEXT, labelsize=7, length=3)
        ax.grid(axis="y", color="#E7EAF0", linewidth=0.7, zorder=0)
        ax.spines["top"].set_visible(False)
        ax_toefl.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax_toefl.spines["left"].set_visible(False)
        for spine in (ax.spines["left"], ax.spines["bottom"]):
            spine.set_color("#B8C0CC")
            spine.set_linewidth(0.8)
        ax_toefl.spines["right"].set_color("#B8C0CC")
        ax_toefl.spines["right"].set_linewidth(0.8)

        ax.set_xticks(list(range(group_count)))
        ax.set_xticklabels(
            [self._short_chart_label(name) for name in ten],
            color=CHART_TEXT, fontsize=7, fontweight="bold",
        )

        figure = ax.figure
        legend_x = 0.86
        for legend_y, label, color in (
            (0.62, "IELTS", "#2A78D6"),
            (0.53, "TOEFL", "#008C8C"),
        ):
            figure.add_artist(Rectangle(
                (legend_x, legend_y), 0.025, 0.025,
                transform=figure.transFigure, facecolor=color, edgecolor="none",
                clip_on=False,
            ))
            figure.text(
                legend_x + 0.04, legend_y + 0.0125, label,
                transform=figure.transFigure, va="center", fontsize=8,
                color="#202A3A", ha="left",
            )

        column_width = 0.242  # 10% wider than the previous 0.22
        for index, (name, ielts, toefl) in enumerate(zip(ten, diem_ielts, diem_toefl)):
            self._add_top_rounded_column(
                ax, index - column_width, 0, column_width,
                min(ielts, 9), "#2A78D6"
            )
            self._add_top_rounded_column(
                ax_toefl, index, 0, column_width,
                min(toefl, 120), "#008C8C"
            )
            ax.text(
                index - column_width / 2, min(ielts, 9) + 0.35, f"{ielts:g}",
                ha="center", va="bottom", color=CHART_MUTED, fontsize=7,
                clip_on=False,
            )
            ax_toefl.text(
                index + column_width / 2, min(toefl, 120) + 4.5, f"{toefl:g}",
                ha="center", va="bottom", color=CHART_MUTED, fontsize=7,
                clip_on=False,
            )

        if thieu:
            ax.text(
                0.0, 0.01, f"N/A: {', '.join(thieu)}",
                transform=ax.transAxes, fontsize=7, color="#B00020",
            )

    def _remove(self, uni_id):
        # toggle_compare voi id da co trong list se bo id do ra (Issue 1.6)
        compare_service.toggle_compare(uni_id)
        self._render()
