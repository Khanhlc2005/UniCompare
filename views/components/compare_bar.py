"""CompareBar — thanh "X/5 đã chọn" để so sánh (wireframe 2 gọi là
StickyCompareBar): nền navy đặc, chữ trắng, nút teal bo tròn — đúng mockup
University_Browser_Wireframes-print.pdf trang 3. Đọc số lượng thẳng từ
compare_service, không tự giữ state riêng trong widget.
"""

import ttkbootstrap as tb

from services import compare_service


class CompareBar(tb.Frame):
    """Thanh hiện số trường đang chọn để so sánh + nút đi sang màn So sánh."""

    def __init__(self, parent, on_compare=None, **kwargs):
        super().__init__(parent, bootstyle="primary", padding=12, **kwargs)
        self._on_compare = on_compare

        self._label = tb.Label(self, text="", bootstyle="inverse-primary", font=("Segoe UI", 10, "bold"))
        self._label.pack(side="left")

        tb.Button(
            self, text="So sánh ngay →", bootstyle="success",
            command=lambda: self._on_compare() if self._on_compare else None
        ).pack(side="right")

        self.refresh()

    def refresh(self):
        """Đọc lại số lượng từ compare_service, gọi lại khi list thay đổi."""
        count = len(compare_service.get_compare_ids())
        self._label.configure(text=f"{count}/{compare_service.MAX_COMPARE} đã chọn để so sánh")
