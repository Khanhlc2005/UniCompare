"""Trang Chi tiết trường (Detail) — banner tên trường, 4 stat card, mục lục
trái + nội dung phải. Đúng Frame contract (ARCHITECTURE.md mục 5.1): frame
được AppShell tạo 1 lần lúc khởi động, refresh(university_id=...) nạp lại
dữ liệu mỗi lần mở từ 1 card khác (không destroy/recreate frame).

Banner nền navy đặc theo mockup University_Browser_Wireframes-print.pdf
trang 8. Mockup còn có 2 nút "Lưu vào quan tâm"/"Thêm vào so sánh" trong
banner — CHƯA thêm ở đây vì phải gọi watchlist_service/compare_service,
ngoài phạm vi việc chỉnh visual lần này.
"""

import ttkbootstrap as tb

from views.components.scrollable_frame import ScrollableFrame

ANCHOR_ITEMS = [
    ("Tổng quan", 0.0),
    ("Điều kiện nhập học", 0.5),
]


class DetailPage(tb.Frame):
    """Trang chi tiết 1 trường — nhận university_id qua refresh()."""

    def __init__(self, master, controller):
        super().__init__(master)
        self._controller = controller
        self._data = {}
        self._colors = tb.Style().colors

        self._banner = tb.Frame(self, bootstyle="primary", padding=(28, 16))
        self._banner.pack(fill="x")
        tb.Button(
            self._banner, text="← Quay lại", style="BannerLink.TButton",
            command=lambda: self._controller.show_frame("home")
        ).pack(anchor="w")
        self._name_lbl = tb.Label(
            self._banner, text="", bootstyle="inverse-primary", font=("Segoe UI", 16, "bold")
        )
        self._name_lbl.pack(anchor="w", pady=(4, 0))
        self._country_lbl = tb.Label(self._banner, text="", bootstyle="inverse-primary")
        self._country_lbl.pack(anchor="w")

        self._scroll = ScrollableFrame(self)
        self._scroll.pack(fill="both", expand=True)

    def refresh(self, university_id=None, **kwargs):
        """AppShell gọi khi show_frame("detail", university_id=...)."""
        if university_id is not None:
            uni = self._controller.repo.get_by_id(university_id)
            if uni:
                self._data = uni
        elif not self._data:
            all_unis = self._controller.repo.get_all()
            self._data = all_unis[0] if all_unis else {}
        self._render()

    def _render(self):
        data = self._data
        self._name_lbl.configure(text=data.get("name", "Chưa chọn trường"))
        self._country_lbl.configure(text=f"📍 {data.get('country', '')}")

        for w in self._scroll.body.winfo_children():
            w.destroy()

        self._build_stats(data)

        body = tb.Frame(self._scroll.body)
        body.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        body.columnconfigure(0, weight=0, minsize=160)
        body.columnconfigure(1, weight=1)

        self._build_toc(body)
        self._build_content(body, data)

    def _build_stats(self, data):
        tuition = data.get("tuition")
        tuition_text = f"${tuition:,}" if isinstance(tuition, (int, float)) else "N/A"
        stats = [
            ("💰", "Học phí / năm", tuition_text),
            ("📝", "IELTS tối thiểu", str(data.get("ielts", "N/A"))),
            ("📋", "GPA tối thiểu", str(data.get("gpa", "N/A"))),
            ("🌍", "Quốc gia", data.get("country", "N/A")),
        ]
        row = tb.Frame(self._scroll.body)
        row.pack(fill="x", padx=28, pady=(16, 16))
        for i, (icon, label, value) in enumerate(stats):
            row.columnconfigure(i, weight=1, uniform="dstats")
            card = tb.Frame(row, bootstyle="light", padding=14)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            tb.Label(card, text=icon, font=("Segoe UI", 14)).pack(anchor="w")
            tb.Label(
                card, text=value, foreground=self._colors.primary, font=("Segoe UI", 13, "bold")
            ).pack(anchor="w", pady=(4, 0))
            tb.Label(card, text=label, foreground=self._colors.secondary).pack(anchor="w")

    def _build_toc(self, parent):
        toc = tb.Frame(parent, bootstyle="light", padding=8)
        toc.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        tb.Label(
            toc, text="📋 Mục lục", foreground=self._colors.primary, font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=8, pady=(4, 8))
        for label, fraction in ANCHOR_ITEMS:
            btn = tb.Button(
                toc, text=label, bootstyle="link",
                command=lambda f=fraction: self._scroll.scroll_to(f)
            )
            btn.pack(fill="x", anchor="w")

    def _build_content(self, parent, data):
        content = tb.Frame(parent, bootstyle="light", padding=20)
        content.grid(row=0, column=1, sticky="nsew")

        tb.Label(
            content, text="Tổng quan", foreground=self._colors.primary, font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 8))
        tb.Label(
            content, text=data.get("description", "Đang cập nhật thông tin..."),
            foreground=self._colors.secondary, wraplength=560, justify="left"
        ).pack(anchor="w", pady=(0, 20))

        tb.Separator(content).pack(fill="x", pady=(0, 20))

        tb.Label(
            content, text="Điều kiện nhập học", foreground=self._colors.primary, font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 8))
        ielts = data.get("ielts", "N/A")
        gpa = data.get("gpa", "N/A")
        tb.Label(content, text=f"• IELTS tối thiểu: {ielts}", foreground=self._colors.secondary).pack(anchor="w")
        tb.Label(content, text=f"• GPA tối thiểu: {gpa}/4.0", foreground=self._colors.secondary).pack(anchor="w")
