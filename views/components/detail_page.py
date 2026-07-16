"""Trang Chi tiết trường — Detail Page.

Hiển thị thông tin chi tiết một trường đại học:
- Banner thông tin với logo, tên, địa chỉ
- Quick Stats (World Rank, Học phí, IELTS, Tỷ lệ việc làm)
- Mục lục bên trái + Nội dung chi tiết bên phải (scrollable)
- Khối Tổng quan: mô tả, grid 2x2 thông tin
- Khối Điều kiện nhập học: bảng điểm tiếng Anh

Dữ liệu lấy từ fake_repo.get_by_id().
"""

import tkinter as tk
from views.components.rounded_widgets import RoundedButton


# ─── Hằng số ──────────────────────────────────────────────────
MAIN_BG = "#F4F6F9"
CARD_BG = "#FFFFFF"
NAVY = "#1E2A78"
DARK_NAVY = "#1A237E"
ACCENT_GREEN = "#4CAF50"
ACCENT_BLUE = "#3B5BDB"
TEXT_DARK = "#1A1A2E"
TEXT_GRAY = "#6B7280"
TEXT_LIGHT = "#9CA3AF"
BORDER_COLOR = "#E5E7EB"
INFO_BG = "#F8F9FA"
WARNING_BG = "#FFF3CD"
WARNING_TEXT = "#856404"
ACTIVE_ANCHOR_BG = "#E8F0FE"
ACTIVE_ANCHOR_FG = ACCENT_BLUE

# Menu mục lục
ANCHOR_ITEMS = [
    "Tổng quan",
    "Điều kiện nhập học",
    "Học phí & Chi phí",
    "Chương trình đào tạo",
    "Cơ sở vật chất",
    "Học bổng",
]


class DetailPage(tk.Frame):
    """Trang chi tiết trường đại học."""

    def __init__(self, parent, uni_data: dict, on_back=None, **kwargs):
        super().__init__(parent, bg=MAIN_BG, **kwargs)
        self._data = uni_data or {}
        self._on_back = on_back
        self._active_anchor = "Tổng quan"
        self._anchor_labels = {}

        # Main scrollable area
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

        # Build UI
        self._build_banner()
        self._build_quick_stats()
        self._build_body()

    def _on_canvas_resize(self, event):
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_mousewheel_up(self, event):
        self._canvas.yview_scroll(-1, "units")

    def _on_mousewheel_down(self, event):
        self._canvas.yview_scroll(1, "units")

    # ─── Banner ───────────────────────────────────────────────
    def _build_banner(self):
        banner = tk.Canvas(
            self._scroll_frame, height=180,
            bg=MAIN_BG, highlightthickness=0, bd=0
        )
        banner.pack(fill="x", padx=0, pady=0)

        data = self._data
        name = data.get("name", "Trường Đại học")
        country = data.get("country", "")

        def draw_banner(event):
            banner.delete("all")
            w = event.width
            h = 180

            # Background
            banner.create_rectangle(0, 0, w, h, fill=DARK_NAVY, outline="")

            # Decorative elements
            banner.create_oval(
                w - 200, -50, w - 50, 100,
                fill="", outline="#3949AB", width=2
            )
            banner.create_oval(
                w - 150, 80, w - 30, 200,
                fill="", outline="#3949AB", width=2
            )

            # Back button
            back_text = banner.create_text(
                28, 22, text="← Quay lại", fill="#C5CAE9",
                font=("Segoe UI", 10), anchor="w"
            )
            banner.tag_bind(back_text, "<Button-1>",
                            lambda e: self._on_back() if self._on_back else None)

            # Logo circle
            banner.create_oval(28, 50, 78, 100, fill="#FFFFFF", outline="")
            # Chữ viết tắt từ tên trường
            initials = "".join(
                word[0] for word in name.split()[:2] if word
            ).upper()
            banner.create_text(
                53, 75, text=initials, fill=NAVY,
                font=("Segoe UI", 14, "bold")
            )

            # Tên trường
            banner.create_text(
                95, 58, text=name, fill="#FFFFFF",
                font=("Segoe UI", 16, "bold"), anchor="w"
            )

            # Địa chỉ
            banner.create_text(
                95, 85, text=f"📍 {country}",
                fill="#C5CAE9", font=("Segoe UI", 10), anchor="w"
            )

            # Action buttons
            # Nút "Lưu vào quan tâm"
            self._draw_action_btn(
                banner, 95, 115, 180, 38,
                "⭐ Lưu vào quan tâm", ACCENT_GREEN, "#FFFFFF"
            )
            # Nút "Thêm vào so sánh"
            self._draw_action_btn(
                banner, 290, 115, 180, 38,
                "📊 Thêm vào so sánh", "transparent", "#FFFFFF",
                border_color="#FFFFFF"
            )

        banner.bind("<Configure>", draw_banner)

    def _draw_action_btn(self, canvas, x, y, w, h, text, fill, fg,
                         border_color=None):
        """Vẽ nút hành động trên canvas."""
        r = 8
        if fill == "transparent":
            fill = DARK_NAVY
        points = [
            x + r, y, x + w - r, y, x + w, y, x + w, y + r,
            x + w, y + h - r, x + w, y + h, x + w - r, y + h,
            x + r, y + h, x, y + h, x, y + h - r,
            x, y + r, x, y,
        ]
        btn_id = canvas.create_polygon(
            points, fill=fill, smooth=True,
            outline=border_color or "", width=1 if border_color else 0
        )
        text_id = canvas.create_text(
            x + w // 2, y + h // 2, text=text,
            fill=fg, font=("Segoe UI", 9, "bold")
        )

    # ─── Quick Stats ──────────────────────────────────────────
    def _build_quick_stats(self):
        stats_frame = tk.Frame(self._scroll_frame, bg=MAIN_BG)
        stats_frame.pack(fill="x", padx=28, pady=(16, 0))

        data = self._data
        tuition = data.get("tuition", "N/A")
        ielts = data.get("ielts", "N/A")

        stats = [
            ("🏆", "World Rank", "#1 - #50", "#FFF7ED"),
            ("💰", "Học phí / năm", f"${tuition:,}" if isinstance(tuition, (int, float)) else str(tuition), "#F0FDF4"),
            ("📝", "IELTS tối thiểu", str(ielts), "#EEF2FF"),
            ("💼", "Tỷ lệ việc làm", "94%", "#FDF2F8"),
        ]

        for i, (icon, label, value, accent_bg) in enumerate(stats):
            card = tk.Frame(stats_frame, bg=CARD_BG, padx=16, pady=14,
                            highlightbackground=BORDER_COLOR, highlightthickness=1)
            stats_frame.columnconfigure(i, weight=1, uniform="qstats")
            card.grid(row=0, column=i, sticky="nsew",
                      padx=(0 if i == 0 else 8, 0))

            # Icon
            tk.Label(
                card, text=icon, bg=accent_bg,
                font=("Segoe UI", 14), padx=6, pady=2
            ).pack(anchor="w")

            # Value
            tk.Label(
                card, text=value, bg=CARD_BG, fg=TEXT_DARK,
                font=("Segoe UI", 16, "bold"), anchor="w"
            ).pack(anchor="w", pady=(6, 0))

            # Label
            tk.Label(
                card, text=label, bg=CARD_BG, fg=TEXT_GRAY,
                font=("Segoe UI", 9), anchor="w"
            ).pack(anchor="w")

    # ─── Body (Mục lục + Nội dung) ────────────────────────────
    def _build_body(self):
        body = tk.Frame(self._scroll_frame, bg=MAIN_BG)
        body.pack(fill="both", expand=True, padx=28, pady=(16, 24))
        body.columnconfigure(0, weight=0, minsize=200)
        body.columnconfigure(1, weight=1)

        # ── Mục lục (Bên trái) ──
        toc_card = tk.Frame(body, bg=CARD_BG, padx=4, pady=12,
                            highlightbackground=BORDER_COLOR, highlightthickness=1)
        toc_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(
            toc_card, text="📋  Mục lục",
            bg=CARD_BG, fg=TEXT_DARK,
            font=("Segoe UI", 11, "bold"), anchor="w"
        ).pack(anchor="w", padx=12, pady=(4, 8))

        tk.Frame(toc_card, bg=BORDER_COLOR, height=1).pack(fill="x", padx=8)

        for item in ANCHOR_ITEMS:
            lbl = tk.Label(
                toc_card, text=f"    {item}",
                bg=CARD_BG, fg=TEXT_GRAY,
                font=("Segoe UI", 10), anchor="w",
                padx=12, pady=8, cursor="hand2"
            )
            lbl.pack(fill="x")
            self._anchor_labels[item] = lbl

            lbl.bind("<Button-1>", lambda e, name=item: self._set_anchor(name))
            lbl.bind("<Enter>", lambda e, l=lbl, name=item: self._hover_anchor(l, name, True))
            lbl.bind("<Leave>", lambda e, l=lbl, name=item: self._hover_anchor(l, name, False))

        self._set_anchor("Tổng quan")

        # ── Nội dung chi tiết (Bên phải) ──
        content_card = tk.Frame(body, bg=CARD_BG, padx=24, pady=20,
                                highlightbackground=BORDER_COLOR, highlightthickness=1)
        content_card.grid(row=0, column=1, sticky="nsew")

        self._build_overview_section(content_card)
        self._build_admission_section(content_card)

    def _set_anchor(self, name):
        """Đặt mục lục active."""
        self._active_anchor = name
        for item_name, lbl in self._anchor_labels.items():
            if item_name == name:
                lbl.configure(bg=ACTIVE_ANCHOR_BG, fg=ACTIVE_ANCHOR_FG,
                              font=("Segoe UI", 10, "bold"))
            else:
                lbl.configure(bg=CARD_BG, fg=TEXT_GRAY,
                              font=("Segoe UI", 10))

    def _hover_anchor(self, lbl, name, entering):
        if name == self._active_anchor:
            return
        if entering:
            lbl.configure(bg="#F0F0F5")
        else:
            lbl.configure(bg=CARD_BG)

    # ─── Tổng quan ────────────────────────────────────────────
    def _build_overview_section(self, parent):
        # Section header
        header_frame = tk.Frame(parent, bg=CARD_BG)
        header_frame.pack(fill="x", pady=(0, 12))

        accent_bar = tk.Frame(header_frame, bg=ACCENT_BLUE, width=4)
        accent_bar.pack(side="left", fill="y", padx=(0, 10))

        tk.Label(
            header_frame, text="Tổng quan",
            bg=CARD_BG, fg=TEXT_DARK,
            font=("Segoe UI", 14, "bold"), anchor="w"
        ).pack(side="left")

        # Description
        desc = self._data.get("description", "Đang cập nhật thông tin...")
        tk.Label(
            parent, text=desc,
            bg=CARD_BG, fg=TEXT_GRAY,
            font=("Segoe UI", 10), anchor="w",
            wraplength=600, justify="left"
        ).pack(fill="x", pady=(0, 16))

        # Grid 2x2 thông tin
        info_grid = tk.Frame(parent, bg=CARD_BG)
        info_grid.pack(fill="x", pady=(0, 20))
        info_grid.columnconfigure(0, weight=1, uniform="info")
        info_grid.columnconfigure(1, weight=1, uniform="info")

        info_items = [
            ("🏛️", "Loại hình", "Công lập"),
            ("👥", "Tổng sinh viên", "42,000+"),
            ("📐", "Diện tích", "150 hecta"),
            ("📅", "Năm thành lập", "1905"),
        ]

        for idx, (icon, label, value) in enumerate(info_items):
            row = idx // 2
            col = idx % 2
            cell = tk.Frame(
                info_grid, bg=INFO_BG, padx=16, pady=12
            )
            cell.grid(row=row, column=col, sticky="nsew",
                      padx=(0 if col == 0 else 6, 0),
                      pady=(0 if row == 0 else 6, 0))

            tk.Label(
                cell, text=f"{icon}  {label}",
                bg=INFO_BG, fg=TEXT_GRAY,
                font=("Segoe UI", 9), anchor="w"
            ).pack(anchor="w")
            tk.Label(
                cell, text=value,
                bg=INFO_BG, fg=TEXT_DARK,
                font=("Segoe UI", 12, "bold"), anchor="w"
            ).pack(anchor="w", pady=(4, 0))

    # ─── Điều kiện nhập học ───────────────────────────────────
    def _build_admission_section(self, parent):
        # Separator
        tk.Frame(parent, bg=BORDER_COLOR, height=1).pack(fill="x", pady=(0, 20))

        # Section header
        header_frame = tk.Frame(parent, bg=CARD_BG)
        header_frame.pack(fill="x", pady=(0, 12))

        accent_bar = tk.Frame(header_frame, bg="#F59E0B", width=4)
        accent_bar.pack(side="left", fill="y", padx=(0, 10))

        tk.Label(
            header_frame, text="Điều kiện nhập học",
            bg=CARD_BG, fg=TEXT_DARK,
            font=("Segoe UI", 14, "bold"), anchor="w"
        ).pack(side="left")

        # Warning badge
        warning_frame = tk.Frame(parent, bg=WARNING_BG, padx=12, pady=8)
        warning_frame.pack(fill="x", pady=(0, 16))
        tk.Label(
            warning_frame, text="⚠️  HẠN CHÓT NGHIÊM NGẶT — Kiểm tra deadline trên website trường",
            bg=WARNING_BG, fg=WARNING_TEXT,
            font=("Segoe UI", 9, "bold"), anchor="w"
        ).pack(anchor="w")

        # Bảng điểm tiếng Anh
        tk.Label(
            parent, text="Trình độ tiếng Anh yêu cầu",
            bg=CARD_BG, fg=TEXT_DARK,
            font=("Segoe UI", 11, "bold"), anchor="w"
        ).pack(anchor="w", pady=(0, 8))

        ielts_score = self._data.get("ielts", 7.0)

        # Table header
        table_header = tk.Frame(parent, bg="#E8ECF4")
        table_header.pack(fill="x")
        for i, col_text in enumerate(("Kỳ thi", "Điểm tối thiểu", "Khuyến nghị")):
            table_header.columnconfigure(i, weight=1, uniform="table")
            tk.Label(
                table_header, text=col_text,
                bg="#E8ECF4", fg=TEXT_DARK,
                font=("Segoe UI", 10, "bold"),
                padx=12, pady=8, anchor="w"
            ).grid(row=0, column=i, sticky="nsew")

        # Table rows
        rows_data = [
            ("IELTS Academic", str(ielts_score), str(ielts_score + 0.5)),
            ("TOEFL iBT", str(int(ielts_score * 13)), str(int((ielts_score + 0.5) * 13))),
            ("Duolingo English Test", "120", "130"),
        ]

        for r_idx, (exam, minimum, recommended) in enumerate(rows_data):
            row_bg = CARD_BG if r_idx % 2 == 0 else INFO_BG
            row_frame = tk.Frame(parent, bg=row_bg)
            row_frame.pack(fill="x")
            for c_idx, val in enumerate((exam, minimum, recommended)):
                row_frame.columnconfigure(c_idx, weight=1, uniform="table")
                font_style = ("Segoe UI", 10, "bold") if c_idx == 0 else ("Segoe UI", 10)
                tk.Label(
                    row_frame, text=val,
                    bg=row_bg, fg=TEXT_DARK if c_idx == 0 else TEXT_GRAY,
                    font=font_style,
                    padx=12, pady=8, anchor="w"
                ).grid(row=0, column=c_idx, sticky="nsew")

        # GPA requirement
        gpa = self._data.get("gpa", "N/A")
        gpa_frame = tk.Frame(parent, bg=INFO_BG, padx=16, pady=12)
        gpa_frame.pack(fill="x", pady=(16, 0))
        tk.Label(
            gpa_frame, text=f"📋  GPA tối thiểu yêu cầu: {gpa}/4.0",
            bg=INFO_BG, fg=TEXT_DARK,
            font=("Segoe UI", 10, "bold"), anchor="w"
        ).pack(anchor="w")

    def destroy(self):
        """Cleanup bindings khi destroy."""
        try:
            self._canvas.unbind_all("<Button-4>")
            self._canvas.unbind_all("<Button-5>")
        except Exception:
            pass
        super().destroy()
