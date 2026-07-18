"""Trang So sánh (Compare) — Issue 1.8.

Kế thừa ttk.Frame(master, controller) đúng Frame contract (ARCHITECTURE.md
mục 5.1). `refresh()` được AppShell gọi mỗi lần frame được tkraise() lên,
đọc lại compare_service để đồng bộ khi vừa thêm/bớt trường ở Watchlist/
Search/Detail rồi quay lại đây - không tự giữ list trường riêng trong View.

Chỉ làm khung theo AC 1.8 (PLAN.md): chip trường (bỏ được) + bảng dữ liệu
render đúng cột khi chọn 2-5 trường. CHƯA làm chart matplotlib (Issue
2.7/3.3 của Huy), CHƯA highlight giá trị tốt nhất mỗi tiêu chí (Issue 2.8
tuần sau) - để nguyên placeholder cho các Issue đó.
"""

import ttkbootstrap as tb

from services import compare_service
from views.components.scrollable_frame import ScrollableFrame
from views.components.compare_chip import CompareChip


# tieu chi hien trong bang - dung dung field cua fake_repo hien tai
# (gpa/ielts/tuition), KHONG phai schema ARCHITECTURE.md (xem CLAUDE.md,
# mismatch da biet, chua doi o Issue nay)
CRITERIA = [
    ("country", "Quốc gia"),
    ("gpa", "GPA yêu cầu"),
    ("ielts", "IELTS yêu cầu"),
    ("tuition", "Học phí/năm"),
]


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

        for row_idx, (field, label) in enumerate(CRITERIA, start=1):
            tb.Label(
                table, text=label, foreground=self._colors.secondary
            ).grid(row=row_idx, column=0, sticky="w", padx=8, pady=8)

            for col_idx, uni in enumerate(data, start=1):
                value = uni.get(field, "N/A")
                if field == "tuition" and isinstance(value, (int, float)):
                    value = f"${value:,}"
                tb.Label(table, text=str(value)).grid(
                    row=row_idx, column=col_idx, sticky="w", padx=8, pady=8
                )

    def _remove(self, uni_id):
        # toggle_compare voi id da co trong list se bo id do ra (Issue 1.6)
        compare_service.toggle_compare(uni_id)
        self._render()
