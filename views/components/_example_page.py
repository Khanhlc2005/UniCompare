"""Ví dụ: Cách tạo View mới trong UniCompare, đúng Frame contract đã chốt
(ARCHITECTURE.md mục 5.1). File này là MẪU THAM KHẢO — sau khi hiểu cách
hoạt động, hãy xóa file này và tạo file riêng cho màn của bạn.

══════════════════════════════════════════════════════
4 BƯỚC ĐỂ THÊM VIEW MỚI:
══════════════════════════════════════════════════════

1. Tạo file views/components/<ten_view>.py
2. Viết class kế thừa thẳng ttk.Frame, constructor (self, master, controller)
   — không cần base class/interface nào khác.
3. Viết refresh(self, **kwargs) — AppShell gọi hàm này mỗi lần frame được
   đưa lên (tkraise), để dữ liệu luôn mới.
4. Đăng ký trong views/app_shell.py, dict FRAME_CLASSES:
       "search": SearchPage
══════════════════════════════════════════════════════
"""

import ttkbootstrap as tb

from views.components.scrollable_frame import ScrollableFrame


class SearchPage(tb.Frame):
    """Ví dụ mẫu — Huy sẽ thay nội dung thật ở Issue 1.5."""

    def __init__(self, master, controller):
        super().__init__(master)
        self._controller = controller

        self._scroll = ScrollableFrame(self)
        self._scroll.pack(fill="both", expand=True)

        tb.Label(
            self._scroll.body, text="Tìm kiếm trường đại học",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=28, pady=(20, 12))

        entry = tb.Entry(self._scroll.body)
        entry.pack(fill="x", padx=28, pady=(0, 16))

        tb.Label(
            self._scroll.body, text="Kết quả sẽ hiển thị ở đây...",
            bootstyle="secondary"
        ).pack(anchor="w", padx=28)

    def refresh(self, **kwargs):
        """Gọi khi frame được tkraise() lên — đọc lại dữ liệu nếu cần."""
        pass
