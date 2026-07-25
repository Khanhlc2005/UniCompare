"""CompareBar — thanh "X/5 đã chọn" để so sánh (wireframe 2 gọi là
StickyCompareBar): nền navy đặc, chữ trắng, nút teal bo tròn — đúng mockup
University_Browser_Wireframes-print.pdf trang 3. Đọc số lượng thẳng từ
compare_service, không tự giữ state riêng trong widget.

Issue 2.9: tự ẩn/hiện theo số lượng đang chọn (mockup không có ví dụ 0
trường nên tự quyết định ưu tiên ẩn thanh thay vì hiện "0/5"). Vì vậy
CompareBar tự pack() chính nó thay vì để nơi gọi tự pack() từ bên ngoài như
trước — truyền các tham số pack qua `pack_opts` lúc khởi tạo, gọi refresh()
lại mỗi khi state ở compare_service có thể đã đổi.
"""

import ttkbootstrap as tb

from services import compare_service


class CompareBar(tb.Frame):
    """Thanh hiện số trường đang chọn để so sánh + nút đi sang màn So sánh.
    Tự ẩn (pack_forget) khi chưa chọn trường nào — gọi refresh() sau mỗi
    lần thay đổi ở compare_service (thêm/bớt trường) để cập nhật."""

    def __init__(self, parent, on_compare=None, pack_opts=None, **kwargs):
        super().__init__(parent, bootstyle="primary", padding=12, **kwargs)
        self._on_compare = on_compare
        self._pack_opts = pack_opts or {"fill": "x"}

        self._label = tb.Label(self, text="", bootstyle="inverse-primary", font=("Segoe UI", 10, "bold"))
        self._label.pack(side="left")

        tb.Button(
            self, text="So sánh ngay →", bootstyle="success",
            command=lambda: self._on_compare() if self._on_compare else None
        ).pack(side="right")

        self.refresh()

    def refresh(self):
        """Đọc lại số lượng từ compare_service — gọi lại khi list thay đổi
        ở bất kỳ màn nào dùng chung component này. 0 trường thì ẩn thanh
        (pack_forget) thay vì hiện "0/5" vì mockup không có ví dụ này."""
        count = len(compare_service.get_compare_ids())
        if count == 0:
            self.pack_forget()
            return
        self._label.configure(text=f"{count}/{compare_service.MAX_COMPARE} đã chọn để so sánh")
        if not self.winfo_ismapped():
            self.pack(**self._pack_opts)
