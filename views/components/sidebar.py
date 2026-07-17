"""Sidebar điều hướng cho UniCompare — dùng ttk/ttkbootstrap (ARCHITECTURE.md
mục 5.3), thay cho bản vẽ tay bằng tk.Canvas trước đó.
"""

import ttkbootstrap as tb

MENU_ITEMS = [
    ("home", "🏠  Trang chủ"),
    ("favorite", "⭐  Quan tâm"),
    ("search", "🔍  Tìm kiếm"),
    ("compare", "📊  So sánh"),
    ("chatbot", "🤖  Chatbot"),
]


class Sidebar(tb.Frame):
    """Sidebar bên trái — click menu gọi `on_navigate(key)`."""

    def __init__(self, parent, on_navigate=None, **kwargs):
        super().__init__(parent, bootstyle="dark", width=220, **kwargs)
        self.pack_propagate(False)
        self._on_navigate = on_navigate
        self._buttons = {}

        tb.Label(
            self, text="UniCompare", bootstyle="inverse-dark",
            font=("Segoe UI", 14, "bold")
        ).pack(fill="x", padx=18, pady=(24, 0))
        tb.Label(
            self, text="ACADEMIC INSIGHTS", bootstyle="inverse-dark",
            font=("Segoe UI", 8)
        ).pack(fill="x", padx=18, pady=(0, 16))
        tb.Separator(self, bootstyle="secondary").pack(fill="x", padx=16, pady=(0, 12))

        for key, label in MENU_ITEMS:
            btn = tb.Button(
                self, text=label, bootstyle="dark",
                command=lambda k=key: self._handle_click(k)
            )
            btn.pack(fill="x", padx=12, pady=3)
            self._buttons[key] = btn

        self.set_active("home")

    def _handle_click(self, key):
        if self._on_navigate:
            self._on_navigate(key)

    def set_active(self, key):
        """Highlight menu dang mo - bo qua neu key khong nam trong sidebar
        (VD man Detail mo tu card, khong co trong menu)."""
        if key not in self._buttons:
            return
        for k, btn in self._buttons.items():
            btn.configure(bootstyle="primary" if k == key else "dark")
