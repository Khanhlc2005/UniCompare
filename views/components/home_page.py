"""Trang chủ UniCompare — Home Page.

Hiển thị:
- Header với search bar
- Welcome Banner
- Stats Cards (3 thẻ thống kê)
- Feature Cards (4 thẻ lối tắt tính năng)
- Tin tức nổi bật + Gợi ý cho bạn
"""

import tkinter as tk
from views.components.rounded_widgets import RoundedButton


# ─── Hằng số ──────────────────────────────────────────────────
MAIN_BG = "#F4F6F9"
CARD_BG = "#FFFFFF"
NAVY = "#1E2A78"
ACCENT_GREEN = "#4CAF50"
ACCENT_BLUE = "#3B5BDB"
TEXT_DARK = "#1A1A2E"
TEXT_GRAY = "#6B7280"
TEXT_LIGHT = "#9CA3AF"
BORDER_COLOR = "#E5E7EB"

# Dữ liệu stats
STATS_DATA = [
    ("📚", "Tổng số trường", "2,847", "#EEF2FF"),
    ("🌍", "Quốc gia", "95", "#F0FDF4"),
    ("🔄", "Cập nhật lần cuối", "Hôm nay", "#FFF7ED"),
]

# Dữ liệu feature cards
FEATURES_DATA = [
    ("⭐", "Quan tâm", "Quản lý danh sách các trường bạn yêu thích", "favorite", "#FFF7ED"),
    ("🔍", "Tìm kiếm", "Tìm kiếm trường theo nhiều tiêu chí khác nhau", "search", "#EEF2FF"),
    ("📊", "So sánh", "So sánh chi tiết giữa các trường đại học", "compare", "#F0FDF4"),
    ("🤖", "Chatbot", "Hỏi đáp thông minh với trợ lý AI", "chatbot", "#FDF2F8"),
]

# Dữ liệu gợi ý
SUGGESTIONS = [
    ("BK", "Đại học Bách Khoa Hà Nội", "TOP 1", "#E8F5E9"),
    ("KT", "Đại học Kinh tế Quốc dân", "TOP 2", "#E3F2FD"),
    ("RM", "RMIT Việt Nam", "TOP 3", "#FFF3E0"),
]


class HomePage(tk.Frame):
    """Trang chủ chính của ứng dụng."""

    def __init__(self, parent, on_navigate=None, on_view_detail=None, **kwargs):
        super().__init__(parent, bg=MAIN_BG, **kwargs)
        self._on_navigate = on_navigate
        self._on_view_detail = on_view_detail

        # Scrollable container
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

        # Bind canvas resize to stretch inner frame
        self._canvas.bind("<Configure>", self._on_canvas_resize)
        # Bind mousewheel
        self._canvas.bind_all("<Button-4>", self._on_mousewheel_up)
        self._canvas.bind_all("<Button-5>", self._on_mousewheel_down)

        # Build content
        self._build_header()
        self._build_welcome_banner()
        self._build_stats_cards()
        self._build_feature_cards()
        self._build_bottom_section()

    def _on_canvas_resize(self, event):
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_mousewheel_up(self, event):
        self._canvas.yview_scroll(-1, "units")

    def _on_mousewheel_down(self, event):
        self._canvas.yview_scroll(1, "units")

    # ─── Header ───────────────────────────────────────────────
    def _build_header(self):
        header = tk.Frame(self._scroll_frame, bg=MAIN_BG)
        header.pack(fill="x", padx=28, pady=(20, 4))

        # Tiêu đề
        tk.Label(
            header, text="Trang chủ",
            bg=MAIN_BG, fg=TEXT_DARK,
            font=("Segoe UI", 18, "bold"), anchor="w"
        ).pack(side="left")

        # Khu vực bên phải (search + icons)
        right_frame = tk.Frame(header, bg=MAIN_BG)
        right_frame.pack(side="right")

        # Nút thông báo & cài đặt
        for icon_text in ("⚙️", "🔔"):
            icon_btn = tk.Label(
                right_frame, text=icon_text,
                bg="#E8ECF4", fg=TEXT_GRAY,
                font=("Segoe UI", 12), padx=8, pady=4,
                cursor="hand2"
            )
            icon_btn.pack(side="right", padx=(6, 0))

        # Search bar
        search_frame = tk.Frame(right_frame, bg="#E8ECF4", padx=2, pady=2)
        search_frame.pack(side="right", padx=(0, 10))

        search_icon = tk.Label(
            search_frame, text="🔍", bg="#E8ECF4",
            font=("Segoe UI", 10)
        )
        search_icon.pack(side="left", padx=(8, 0))

        search_entry = tk.Entry(
            search_frame, bg="#E8ECF4", fg=TEXT_GRAY,
            font=("Segoe UI", 10), bd=0, width=22,
            insertbackground=TEXT_DARK
        )
        search_entry.insert(0, "Tìm kiếm trường đại học...")
        search_entry.pack(side="left", padx=8, pady=4)

        # Placeholder behavior
        def on_focus_in(e):
            if search_entry.get() == "Tìm kiếm trường đại học...":
                search_entry.delete(0, "end")
                search_entry.config(fg=TEXT_DARK)

        def on_focus_out(e):
            if not search_entry.get():
                search_entry.insert(0, "Tìm kiếm trường đại học...")
                search_entry.config(fg=TEXT_GRAY)

        search_entry.bind("<FocusIn>", on_focus_in)
        search_entry.bind("<FocusOut>", on_focus_out)

    # ─── Welcome Banner ──────────────────────────────────────
    def _build_welcome_banner(self):
        banner_canvas = tk.Canvas(
            self._scroll_frame, height=120,
            bg=MAIN_BG, highlightthickness=0, bd=0
        )
        banner_canvas.pack(fill="x", padx=28, pady=(12, 0))

        # Vẽ khi canvas sẵn sàng
        def draw_banner(event):
            banner_canvas.delete("all")
            w = event.width
            h = 120
            r = 16
            # Gradient giả lập bằng nhiều lớp
            points = [
                r, 0, w - r, 0, w, 0, w, r,
                w, h - r, w, h, w - r, h,
                r, h, 0, h, 0, h - r,
                0, r, 0, 0,
            ]
            banner_canvas.create_polygon(
                points, fill="#1A237E", smooth=True, outline=""
            )
            # Overlay gradient effect (dải sáng nhẹ)
            overlay_points = [
                r, 0, w // 2, 0, w // 2, h,
                r, h, 0, h, 0, h - r,
                0, r, 0, 0,
            ]
            banner_canvas.create_polygon(
                overlay_points, fill="#1E2A78", smooth=True, outline=""
            )

            # Text chào mừng
            banner_canvas.create_text(
                32, 38, text="Chào mừng, Nam Anh 👋",
                fill="#FFFFFF", font=("Segoe UI", 18, "bold"),
                anchor="w"
            )
            banner_canvas.create_text(
                32, 70, text="Khám phá và so sánh hơn 2,800 trường đại học trên toàn thế giới.",
                fill="#C5CAE9", font=("Segoe UI", 11),
                anchor="w"
            )
            # Decorative circles
            banner_canvas.create_oval(
                w - 140, -30, w - 40, 70,
                fill="", outline="#3949AB", width=2
            )
            banner_canvas.create_oval(
                w - 100, 50, w - 20, 130,
                fill="", outline="#3949AB", width=2
            )

        banner_canvas.bind("<Configure>", draw_banner)

    # ─── Stats Cards ─────────────────────────────────────────
    def _build_stats_cards(self):
        stats_frame = tk.Frame(self._scroll_frame, bg=MAIN_BG)
        stats_frame.pack(fill="x", padx=28, pady=(16, 0))

        for i, (icon, title, value, accent_bg) in enumerate(STATS_DATA):
            card = tk.Frame(stats_frame, bg=CARD_BG, padx=20, pady=16,
                            highlightbackground=BORDER_COLOR, highlightthickness=1)
            stats_frame.columnconfigure(i, weight=1, uniform="stats")
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))

            # Icon circle
            icon_label = tk.Label(
                card, text=icon, bg=accent_bg,
                font=("Segoe UI", 16), padx=8, pady=4
            )
            icon_label.pack(anchor="w")

            # Value
            tk.Label(
                card, text=value, bg=CARD_BG, fg=TEXT_DARK,
                font=("Segoe UI", 20, "bold"), anchor="w"
            ).pack(anchor="w", pady=(8, 0))

            # Title
            tk.Label(
                card, text=title, bg=CARD_BG, fg=TEXT_GRAY,
                font=("Segoe UI", 10), anchor="w"
            ).pack(anchor="w")

    # ─── Feature Cards ────────────────────────────────────────
    def _build_feature_cards(self):
        features_frame = tk.Frame(self._scroll_frame, bg=MAIN_BG)
        features_frame.pack(fill="x", padx=28, pady=(16, 0))

        for i, (icon, title, desc, nav_key, accent_bg) in enumerate(FEATURES_DATA):
            card = tk.Frame(features_frame, bg=CARD_BG, padx=18, pady=16,
                            highlightbackground=BORDER_COLOR, highlightthickness=1)
            features_frame.columnconfigure(i, weight=1, uniform="features")
            card.grid(row=0, column=i, sticky="nsew",
                      padx=(0 if i == 0 else 8, 0))

            # Icon
            icon_label = tk.Label(
                card, text=icon, bg=accent_bg,
                font=("Segoe UI", 18), padx=8, pady=4
            )
            icon_label.pack(anchor="w")

            # Title
            tk.Label(
                card, text=title, bg=CARD_BG, fg=TEXT_DARK,
                font=("Segoe UI", 12, "bold"), anchor="w"
            ).pack(anchor="w", pady=(10, 4))

            # Description
            tk.Label(
                card, text=desc, bg=CARD_BG, fg=TEXT_GRAY,
                font=("Segoe UI", 9), anchor="w", wraplength=180,
                justify="left"
            ).pack(anchor="w")

            # Link button
            link = tk.Label(
                card, text="Xem danh sách →", bg=CARD_BG,
                fg=ACCENT_BLUE, font=("Segoe UI", 10, "bold"),
                cursor="hand2", anchor="w"
            )
            link.pack(anchor="w", pady=(10, 0))
            link.bind("<Button-1>",
                      lambda e, k=nav_key: self._on_navigate(k) if self._on_navigate else None)
            # Hover underline
            link.bind("<Enter>", lambda e, l=link: l.config(font=("Segoe UI", 10, "bold underline")))
            link.bind("<Leave>", lambda e, l=link: l.config(font=("Segoe UI", 10, "bold")))

    # ─── Bottom Section (Tin tức + Gợi ý) ─────────────────────
    def _build_bottom_section(self):
        bottom = tk.Frame(self._scroll_frame, bg=MAIN_BG)
        bottom.pack(fill="x", padx=28, pady=(16, 24))
        bottom.columnconfigure(0, weight=2)
        bottom.columnconfigure(1, weight=1)

        # ── Tin tức nổi bật (Bên trái) ──
        news_card = tk.Frame(bottom, bg=CARD_BG, padx=20, pady=16,
                             highlightbackground=BORDER_COLOR, highlightthickness=1)
        news_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Header tin tức
        news_header = tk.Frame(news_card, bg=CARD_BG)
        news_header.pack(fill="x")
        tk.Label(
            news_header, text="📰  Tin tức nổi bật",
            bg=CARD_BG, fg=TEXT_DARK,
            font=("Segoe UI", 13, "bold"), anchor="w"
        ).pack(side="left")
        all_link = tk.Label(
            news_header, text="Tất cả bài viết →",
            bg=CARD_BG, fg=ACCENT_BLUE,
            font=("Segoe UI", 9, "bold"), cursor="hand2"
        )
        all_link.pack(side="right")

        # Separator
        tk.Frame(news_card, bg=BORDER_COLOR, height=1).pack(fill="x", pady=(12, 12))

        # Article preview
        article_frame = tk.Frame(news_card, bg=CARD_BG)
        article_frame.pack(fill="x")

        # Thumbnail placeholder
        thumb = tk.Canvas(
            article_frame, width=180, height=110,
            bg="#E8ECF4", highlightthickness=0, bd=0
        )
        thumb.pack(side="left", padx=(0, 16))
        thumb.create_text(
            90, 45, text="🎓", font=("Segoe UI", 28)
        )
        thumb.create_text(
            90, 80, text="QS Rankings 2026",
            fill=TEXT_GRAY, font=("Segoe UI", 9, "bold")
        )

        # Article text
        article_text = tk.Frame(article_frame, bg=CARD_BG)
        article_text.pack(side="left", fill="both", expand=True)

        tk.Label(
            article_text, text="Giáo dục",
            bg="#EEF2FF", fg=ACCENT_BLUE,
            font=("Segoe UI", 8, "bold"), padx=8, pady=2
        ).pack(anchor="w")
        tk.Label(
            article_text,
            text="Xếp hạng đại học thế giới 2026:\nNhững thay đổi đáng chú ý",
            bg=CARD_BG, fg=TEXT_DARK,
            font=("Segoe UI", 12, "bold"), anchor="w",
            justify="left"
        ).pack(anchor="w", pady=(6, 4))
        tk.Label(
            article_text,
            text="Bảng xếp hạng QS World University Rankings 2026\nvừa được công bố với nhiều biến động thú vị...",
            bg=CARD_BG, fg=TEXT_GRAY,
            font=("Segoe UI", 9), anchor="w",
            justify="left", wraplength=320
        ).pack(anchor="w")

        # ── Gợi ý cho bạn (Bên phải) ──
        suggest_card = tk.Frame(bottom, bg=CARD_BG, padx=20, pady=16,
                                highlightbackground=BORDER_COLOR, highlightthickness=1)
        suggest_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(
            suggest_card, text="💡  Gợi ý cho bạn",
            bg=CARD_BG, fg=TEXT_DARK,
            font=("Segoe UI", 13, "bold"), anchor="w"
        ).pack(anchor="w")

        tk.Frame(suggest_card, bg=BORDER_COLOR, height=1).pack(fill="x", pady=(12, 8))

        for i, (initials, name, badge, badge_color) in enumerate(SUGGESTIONS):
            item = tk.Frame(suggest_card, bg=CARD_BG, pady=6)
            item.pack(fill="x")

            # Mini avatar
            avatar_canvas = tk.Canvas(
                item, width=36, height=36,
                bg=CARD_BG, highlightthickness=0, bd=0
            )
            avatar_canvas.pack(side="left", padx=(0, 10))
            avatar_canvas.create_oval(2, 2, 34, 34, fill="#E8ECF4", outline="")
            avatar_canvas.create_text(
                18, 18, text=initials,
                fill=NAVY, font=("Segoe UI", 9, "bold")
            )

            # Info
            info = tk.Frame(item, bg=CARD_BG)
            info.pack(side="left", fill="x", expand=True)

            name_lbl = tk.Label(
                info, text=name, bg=CARD_BG, fg=TEXT_DARK,
                font=("Segoe UI", 10, "bold"), anchor="w",
                cursor="hand2"
            )
            name_lbl.pack(anchor="w")
            # Bind click to navigate to detail
            name_lbl.bind(
                "<Button-1>",
                lambda e, uid=str(i + 1): self._on_view_detail(uid) if self._on_view_detail else None
            )

            # Badge
            badge_lbl = tk.Label(
                item, text=badge, bg=badge_color, fg=TEXT_DARK,
                font=("Segoe UI", 8, "bold"), padx=8, pady=2
            )
            badge_lbl.pack(side="right")

            # Separator nhỏ giữa items
            if i < len(SUGGESTIONS) - 1:
                tk.Frame(suggest_card, bg=BORDER_COLOR, height=1).pack(fill="x", pady=(2, 0))

    def destroy(self):
        """Cleanup bindings khi destroy."""
        try:
            self._canvas.unbind_all("<Button-4>")
            self._canvas.unbind_all("<Button-5>")
        except Exception:
            pass
        super().destroy()
