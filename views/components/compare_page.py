"""Trang So sánh (Compare) — Issue 1.8 + 2.8.

Kế thừa ttk.Frame(master, controller) đúng Frame contract (ARCHITECTURE.md
mục 5.1). `refresh()` được AppShell gọi mỗi lần frame được tkraise() lên,
đọc lại compare_service để đồng bộ khi vừa thêm/bớt trường ở Watchlist/
Search/Detail rồi quay lại đây - không tự giữ list trường riêng trong View.

Issue 2.8: highlight ô giá trị tốt nhất mỗi tiêu chí (bootstyle="success",
logic xác định "tốt nhất" nằm ở compare_service.xac_dinh_tot_nhat - View chỉ
đọc kết quả để tô màu, không tự so sánh) + nút x trên chip bỏ trường (đã có
sẵn từ Issue 1.8 qua CompareChip.on_remove, giữ nguyên). CHƯA làm chart
matplotlib (Issue 2.7/3.3 của Huy), CHƯA làm StickyCompareBar (Issue 2.9).
"""

import ttkbootstrap as tb

from services import compare_service
from views.components.scrollable_frame import ScrollableFrame
from views.components.compare_chip import CompareChip


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
    """Trang So sánh — chip trường đã chọn + bảng dữ liệu theo cột."""

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
        self._build_table(data)

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

    def _build_table(self, data):
        table = tb.Frame(self._scroll.body, bootstyle="light", padding=16)
        table.pack(fill="both", expand=True, padx=28, pady=(0, 24))

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

    def _remove(self, uni_id):
        # toggle_compare voi id da co trong list se bo id do ra (Issue 1.6)
        compare_service.toggle_compare(uni_id)
        self._render()
