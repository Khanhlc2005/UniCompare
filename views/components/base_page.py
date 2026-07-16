"""BasePage — Template cơ sở cho tất cả các trang trong UniCompare.

Đồng đội tạo trang mới chỉ cần:
1. Kế thừa BasePage
2. Override _build_content() để xây dựng giao diện
3. Đăng ký vào PAGE_REGISTRY ở cuối file

Ví dụ:
    class SearchPage(BasePage):
        def _build_content(self, container):
            tk.Label(container, text="Tìm kiếm", ...).pack()

    # Đăng ký ở cuối file:
    PAGE_REGISTRY["search"] = SearchPage
"""

import tkinter as tk


# ─── Hằng số dùng chung ──────────────────────────────────────
MAIN_BG = "#F4F6F9"
CARD_BG = "#FFFFFF"
NAVY = "#1E2A78"
ACCENT_GREEN = "#4CAF50"
ACCENT_BLUE = "#3B5BDB"
TEXT_DARK = "#1A1A2E"
TEXT_GRAY = "#6B7280"
BORDER_COLOR = "#E5E7EB"


class BasePage(tk.Frame):
    """Lớp cơ sở cho mọi trang trong UniCompare.

    Cung cấp sẵn:
    - Scrollable canvas (cuộn chuột hoạt động trên Linux)
    - Container frame để đặt nội dung
    - Header mặc định với tiêu đề trang

    Subclass chỉ cần override:
    - _build_content(container): xây dựng giao diện bên trong container
    """

    # Tiêu đề hiển thị trên header (override trong subclass)
    PAGE_TITLE = "Trang"
    PAGE_ICON = "📄"

    def __init__(self, parent, on_navigate=None, **kwargs):
        super().__init__(parent, bg=MAIN_BG, **kwargs)
        self._on_navigate = on_navigate

        # ── Scrollable container ──
        self._canvas = tk.Canvas(self, bg=MAIN_BG, highlightthickness=0, bd=0)
        self._scrollbar = tk.Scrollbar(self, orient="vertical",
                                       command=self._canvas.yview)
        self._scroll_frame = tk.Frame(self._canvas, bg=MAIN_BG)

        self._scroll_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        )
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._scroll_frame, anchor="nw"
        )
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._canvas.bind("<Configure>", self._on_canvas_resize)
        self._canvas.bind_all("<Button-4>", self._on_mousewheel_up)
        self._canvas.bind_all("<Button-5>", self._on_mousewheel_down)

        # ── Build ──
        self._build_header()
        self._build_content(self._scroll_frame)

    def _on_canvas_resize(self, event):
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_mousewheel_up(self, _event):
        self._canvas.yview_scroll(-1, "units")

    def _on_mousewheel_down(self, _event):
        self._canvas.yview_scroll(1, "units")

    def _build_header(self):
        """Header mặc định — có thể override."""
        header = tk.Frame(self._scroll_frame, bg=MAIN_BG)
        header.pack(fill="x", padx=28, pady=(20, 4))

        tk.Label(
            header, text=f"{self.PAGE_ICON}  {self.PAGE_TITLE}",
            bg=MAIN_BG, fg=TEXT_DARK,
            font=("Segoe UI", 18, "bold"), anchor="w"
        ).pack(side="left")

    def _build_content(self, container):
        """Override method này để xây dựng nội dung trang.

        Args:
            container: tk.Frame — frame cha để đặt widget vào.
                       Đã có sẵn scrollbar, cứ pack/grid thoải mái.
        """
        # Placeholder mặc định — đồng đội sẽ override
        placeholder = tk.Frame(container, bg=CARD_BG, padx=40, pady=60,
                               highlightbackground=BORDER_COLOR,
                               highlightthickness=1)
        placeholder.pack(fill="x", padx=28, pady=20)

        tk.Label(
            placeholder, text=f"{self.PAGE_ICON}", bg=CARD_BG,
            font=("Segoe UI", 36)
        ).pack()
        tk.Label(
            placeholder, text=f"{self.PAGE_TITLE}",
            bg=CARD_BG, fg=TEXT_DARK,
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(12, 4))
        tk.Label(
            placeholder, text="Tính năng đang được phát triển...",
            bg=CARD_BG, fg=TEXT_GRAY,
            font=("Segoe UI", 11)
        ).pack()

    def destroy(self):
        """Cleanup scroll bindings."""
        try:
            self._canvas.unbind_all("<Button-4>")
            self._canvas.unbind_all("<Button-5>")
        except Exception:
            pass
        super().destroy()


# ═══════════════════════════════════════════════════════════════
# PAGE REGISTRY — Đồng đội đăng ký trang mới vào đây
# ═══════════════════════════════════════════════════════════════
# Key = sidebar menu key (xem sidebar.py MENU_ITEMS)
# Value = Page class (kế thừa BasePage)
#
# Ví dụ:  PAGE_REGISTRY["search"] = SearchPage
#
# AppShell sẽ tự động tìm class trong registry khi user click menu.
# ═══════════════════════════════════════════════════════════════

PAGE_REGISTRY: dict[str, type] = {}
