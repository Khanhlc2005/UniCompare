"""Sidebar Navigation cho UniCompare.

Sidebar bên trái với nền navy đậm, chứa:
- Logo và branding
- Menu điều hướng (Trang chủ, Quan tâm, Tìm kiếm, So sánh, Chatbot)
- User profile ở góc dưới
"""

import tkinter as tk
from views.components.rounded_widgets import CircleAvatar


# ─── Hằng số giao diện ────────────────────────────────────────
SIDEBAR_BG = "#1E2A78"
SIDEBAR_WIDTH = 250
ACTIVE_BG = "#2E3FA8"
HOVER_BG = "#283690"
TEXT_COLOR = "#FFFFFF"
TEXT_DIM = "#A0A8D0"
ACCENT_GREEN = "#4CAF50"

# Unicode icons thay thế cho icon images
ICONS = {
    "home": "🏠",
    "favorite": "⭐",
    "search": "🔍",
    "compare": "📊",
    "chatbot": "🤖",
}

MENU_ITEMS = [
    ("home", "Trang chủ"),
    ("favorite", "Quan tâm"),
    ("search", "Tìm kiếm"),
    ("compare", "So sánh"),
    ("chatbot", "Chatbot"),
]


class Sidebar(tk.Frame):
    """Sidebar navigation panel."""

    def __init__(self, parent, on_navigate=None, **kwargs):
        super().__init__(parent, bg=SIDEBAR_BG, width=SIDEBAR_WIDTH, **kwargs)
        self.pack_propagate(False)
        self._on_navigate = on_navigate
        self._active_key = "home"
        self._menu_buttons = {}

        self._build_logo()
        self._build_menu()
        self._build_user_profile()

    # ─── Logo & Branding ──────────────────────────────────────
    def _build_logo(self):
        logo_frame = tk.Frame(self, bg=SIDEBAR_BG)
        logo_frame.pack(fill="x", padx=20, pady=(24, 8))

        # Logo icon (hình vuông bo góc xanh lá)
        logo_canvas = tk.Canvas(
            logo_frame, width=42, height=42,
            bg=SIDEBAR_BG, highlightthickness=0, bd=0
        )
        logo_canvas.pack(side="left", padx=(0, 10))
        # Vẽ hình vuông bo góc
        _draw_rounded_rect(logo_canvas, 2, 2, 40, 40, 8, ACCENT_GREEN)
        logo_canvas.create_text(
            21, 21, text="U", fill="#FFFFFF",
            font=("Segoe UI", 16, "bold")
        )

        # Tên ứng dụng
        brand_frame = tk.Frame(logo_frame, bg=SIDEBAR_BG)
        brand_frame.pack(side="left", fill="x")
        tk.Label(
            brand_frame, text="UniCompare",
            bg=SIDEBAR_BG, fg=TEXT_COLOR,
            font=("Segoe UI", 13, "bold"), anchor="w"
        ).pack(anchor="w")
        tk.Label(
            brand_frame, text="ACADEMIC INSIGHTS",
            bg=SIDEBAR_BG, fg=TEXT_DIM,
            font=("Segoe UI", 7), anchor="w"
        ).pack(anchor="w")

        # Đường phân cách
        separator = tk.Frame(self, bg="#2E3FA8", height=1)
        separator.pack(fill="x", padx=20, pady=(16, 8))

    # ─── Menu Navigation ─────────────────────────────────────
    def _build_menu(self):
        menu_frame = tk.Frame(self, bg=SIDEBAR_BG)
        menu_frame.pack(fill="x", padx=12, pady=(4, 0))

        for key, label in MENU_ITEMS:
            btn = self._create_menu_button(menu_frame, key, label)
            btn.pack(fill="x", pady=2)
            self._menu_buttons[key] = btn

        # Đánh dấu nút active ban đầu
        self._update_active("home")

    def _create_menu_button(self, parent, key, label):
        """Tạo một nút menu trong sidebar."""
        icon = ICONS.get(key, "•")
        frame = tk.Frame(parent, bg=SIDEBAR_BG, cursor="hand2")

        # Padding bên trong
        inner = tk.Frame(frame, bg=SIDEBAR_BG, padx=16, pady=10)
        inner.pack(fill="x")

        lbl = tk.Label(
            inner, text=f"  {icon}   {label}",
            bg=SIDEBAR_BG, fg=TEXT_COLOR,
            font=("Segoe UI", 11), anchor="w",
            cursor="hand2"
        )
        lbl.pack(fill="x", anchor="w")

        # Bind click events
        for widget in (frame, inner, lbl):
            widget.bind("<Button-1>", lambda e, k=key: self._on_menu_click(k))
            widget.bind("<Enter>", lambda e, f=frame, k=key: self._on_hover(f, k, True))
            widget.bind("<Leave>", lambda e, f=frame, k=key: self._on_hover(f, k, False))

        frame._key = key
        frame._inner = inner
        frame._label = lbl
        return frame

    def _on_menu_click(self, key):
        """Xử lý khi click menu item."""
        self._update_active(key)
        if self._on_navigate:
            self._on_navigate(key)

    def _on_hover(self, frame, key, entering):
        """Hiệu ứng hover trên menu item."""
        if key == self._active_key:
            return
        color = HOVER_BG if entering else SIDEBAR_BG
        self._set_frame_bg(frame, color)

    def _update_active(self, key):
        """Cập nhật trạng thái active cho menu."""
        self._active_key = key
        for k, frame in self._menu_buttons.items():
            if k == key:
                self._set_frame_bg(frame, ACTIVE_BG)
            else:
                self._set_frame_bg(frame, SIDEBAR_BG)

    @staticmethod
    def _set_frame_bg(frame, color):
        """Đặt màu nền cho frame và tất cả children."""
        frame.configure(bg=color)
        if hasattr(frame, "_inner"):
            frame._inner.configure(bg=color)
        if hasattr(frame, "_label"):
            frame._label.configure(bg=color)

    # ─── User Profile ─────────────────────────────────────────
    def _build_user_profile(self):
        # Spacer đẩy profile xuống dưới
        spacer = tk.Frame(self, bg=SIDEBAR_BG)
        spacer.pack(fill="both", expand=True)

        # Separator
        sep = tk.Frame(self, bg="#2E3FA8", height=1)
        sep.pack(fill="x", padx=20, pady=(0, 12))

        profile_frame = tk.Frame(self, bg=SIDEBAR_BG)
        profile_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Avatar
        avatar = CircleAvatar(
            profile_frame, text="NA", size=42,
            bg_color=ACCENT_GREEN, fg_color="#FFFFFF",
            font=("Segoe UI", 11, "bold")
        )
        avatar.pack(side="left", padx=(0, 10))

        # Info
        info_frame = tk.Frame(profile_frame, bg=SIDEBAR_BG)
        info_frame.pack(side="left", fill="x")
        tk.Label(
            info_frame, text="Nam Anh",
            bg=SIDEBAR_BG, fg=TEXT_COLOR,
            font=("Segoe UI", 11, "bold"), anchor="w"
        ).pack(anchor="w")
        tk.Label(
            info_frame, text="Sinh viên",
            bg=SIDEBAR_BG, fg=TEXT_DIM,
            font=("Segoe UI", 9), anchor="w"
        ).pack(anchor="w")


def _draw_rounded_rect(canvas, x1, y1, x2, y2, r, fill):
    """Hàm helper vẽ hình chữ nhật bo góc."""
    points = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2,
        x1 + r, y2, x1, y2, x1, y2 - r,
        x1, y1 + r, x1, y1,
    ]
    canvas.create_polygon(points, fill=fill, smooth=True, outline="")
