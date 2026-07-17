"""Trang chủ (Home) — 3 stat card tổng quan, lối tắt 4 tính năng, trường
nổi bật. Đúng Frame contract (ARCHITECTURE.md mục 5.1): kế thừa thẳng
ttk.Frame, constructor (master, controller), có refresh().

Số liệu stat card (tổng số trường, số quốc gia...) chưa có nguồn thật ở tuần
1 (chưa có university_service thống kê) nên tạm hiển thị placeholder "—";
tránh bịa số liệu giả trông như số thật.

Màu chữ navy/teal/xám dùng trực tiếp `tb.Style().colors...` (đọc lại đúng
bảng màu đã khai báo 1 chỗ ở app_shell.py), không tự định nghĩa hex riêng.
"""

import ttkbootstrap as tb

from views.components.scrollable_frame import ScrollableFrame

FEATURES_DATA = [
    ("⭐", "Quan tâm", "Quản lý danh sách các trường bạn yêu thích", "favorite"),
    ("🔍", "Tìm kiếm", "Tìm kiếm trường theo nhiều tiêu chí khác nhau", "search"),
    ("📊", "So sánh", "So sánh chi tiết giữa các trường đại học", "compare"),
    ("🤖", "Chatbot", "Hỏi đáp thông minh với trợ lý AI", "chatbot"),
]


class HomePage(tb.Frame):
    """Trang chủ — stat card, lối tắt tính năng, trường nổi bật."""

    def __init__(self, master, controller):
        super().__init__(master)
        self._controller = controller
        self._colors = tb.Style().colors

        self._scroll = ScrollableFrame(self)
        self._scroll.pack(fill="both", expand=True)

        self._build_header()
        self._build_stats()
        self._build_features()
        self._build_featured()

    def _build_header(self):
        banner = tb.Frame(self._scroll.body, bootstyle="primary", padding=24)
        banner.pack(fill="x", padx=28, pady=(20, 16))
        tb.Label(
            banner, text="Chào mừng trở lại 👋", bootstyle="inverse-primary",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w")
        tb.Label(
            banner, bootstyle="inverse-primary",
            text="Khám phá và so sánh các trường đại học trên toàn thế giới.",
        ).pack(anchor="w", pady=(4, 0))

    def _build_stats(self):
        stats_data = [
            ("📚", "Tổng số trường", str(len(self._controller.repo.get_all()))),
            ("🌍", "Quốc gia", str(len({u["country"] for u in self._controller.repo.get_all()}))),
            ("🔄", "Dữ liệu", "fake_repo"),
        ]

        row = tb.Frame(self._scroll.body)
        row.pack(fill="x", padx=28, pady=(0, 16))
        for i, (icon, title, value) in enumerate(stats_data):
            row.columnconfigure(i, weight=1, uniform="stats")
            card = tb.Frame(row, bootstyle="light", padding=16)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            # icon trai + text phai, canh giua theo chieu doc (dung mockup StatCard)
            card.columnconfigure(1, weight=1)
            tb.Label(card, text=icon, font=("Segoe UI", 20)).grid(
                row=0, column=0, rowspan=2, sticky="ns", padx=(0, 12)
            )
            tb.Label(
                card, text=title, foreground=self._colors.secondary, font=("Segoe UI", 8, "bold")
            ).grid(row=0, column=1, sticky="sw")
            tb.Label(
                card, text=value, foreground=self._colors.primary, font=("Segoe UI", 16, "bold")
            ).grid(row=1, column=1, sticky="nw")

    def _build_features(self):
        row = tb.Frame(self._scroll.body)
        row.pack(fill="x", padx=28, pady=(0, 16))
        for i, (icon, title, desc, nav_key) in enumerate(FEATURES_DATA):
            row.columnconfigure(i, weight=1, uniform="features")
            card = tb.Frame(row, bootstyle="light", padding=16)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            tb.Label(card, text=icon, font=("Segoe UI", 18)).pack(anchor="w")
            tb.Label(
                card, text=title, foreground=self._colors.primary, font=("Segoe UI", 11, "bold")
            ).pack(anchor="w", pady=(8, 4))
            tb.Label(
                card, text=desc, foreground=self._colors.secondary,
                wraplength=180, justify="left"
            ).pack(anchor="w")
            tb.Button(
                card, text="Xem danh sách →", style="CardTealLink.TButton",
                command=lambda k=nav_key: self._controller.show_frame(k)
            ).pack(anchor="w", pady=(8, 0))

    def _build_featured(self):
        card = tb.Frame(self._scroll.body, bootstyle="light", padding=16)
        card.pack(fill="x", padx=28, pady=(0, 24))
        tb.Label(
            card, text="🎓 Trường nổi bật", foreground=self._colors.primary,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 8))

        featured = self._controller.repo.get_all()[:3]
        if not featured:
            tb.Label(card, text="Chưa có dữ liệu trường.", foreground=self._colors.secondary).pack(anchor="w")
            return

        for uni in featured:
            row = tb.Frame(card, bootstyle="light")
            row.pack(fill="x", pady=4)
            name_lbl = tb.Label(
                row, text=uni.get("name", ""), foreground=self._colors.primary, cursor="hand2"
            )
            name_lbl.pack(side="left")
            name_lbl.bind(
                "<Button-1>",
                lambda e, uid=uni["id"]: self._controller.show_frame("detail", university_id=uid)
            )
            tb.Label(row, text=uni.get("country", ""), foreground=self._colors.secondary).pack(side="right")

    def refresh(self, **kwargs):
        """Chưa có số liệu động cần nạp lại ở tuần 1, giữ để đúng contract."""
        pass
