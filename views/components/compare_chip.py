"""CompareChip — chip hiển thị 1 trường đang được chọn để so sánh, có dấu
"x" để bỏ trường đó (wireframe trang 4 "So sánh"). Widget chỉ phát callback
on_remove, không tự đọc/ghi compare_service bên trong - nơi gọi (ComparePage)
quyết định làm gì, giống cách CompareBar chỉ đọc không tự giữ state riêng.
"""

import ttkbootstrap as tb


class CompareChip(tb.Frame):
    """Chip pill: tên trường + dấu x, bấm x thì gọi on_remove()."""

    def __init__(self, parent, text, on_remove=None, **kwargs):
        super().__init__(parent, bootstyle="secondary", padding=(10, 6), **kwargs)
        self._on_remove = on_remove

        tb.Label(
            self, text=text, bootstyle="inverse-secondary",
            font=("Segoe UI", 9, "bold")
        ).pack(side="left")

        # dung Label + bind click giong pattern name_lbl o home_page.py, khong
        # bay them custom ttk style rieng cho 1 nut x nho
        close_btn = tb.Label(
            self, text=" ✕", bootstyle="inverse-secondary", cursor="hand2",
            font=("Segoe UI", 9, "bold")
        )
        close_btn.pack(side="left", padx=(6, 0))
        close_btn.bind("<Button-1>", self._handle_remove)

    def _handle_remove(self, _event=None):
        if self._on_remove:
            self._on_remove()
