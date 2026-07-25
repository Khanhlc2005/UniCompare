# -*- coding: utf-8 -*-
"""Trang Chi tiết trường (Detail) — Issue 2.11.

Hoàn thiện DetailView với data thật: đủ mục lục (tổng quan, yêu cầu đầu vào,
học phí & học bổng, ngành học, liên hệ), nút Quan tâm / So sánh trên banner.

Đúng Frame contract (ARCHITECTURE.md mục 5.1): frame được AppShell tạo 1 lần
lúc khởi động, refresh(university_id=...) nạp lại dữ liệu mỗi lần mở từ card
khác (không destroy/recreate frame).

Hỗ trợ CẢ fake_repo (field gpa/ielts/tuition/description) LẪN mongo_repo /
seed_data.json (field gpa_min/ielts_min/tuition_per_year/overview) bằng cách
fallback: ưu tiên field chuẩn ARCHITECTURE.md, nếu không có thì thử field cũ.
Mọi trường trong seed mở được, không lỗi field thiếu (AC Issue 2.11).
"""

from tkinter import messagebox

import ttkbootstrap as tb

from services import watchlist_service, compare_service
from views.components.scrollable_frame import ScrollableFrame

# Muc luc 5 phan — fraction tuong doi de scroll_to (ScrollableFrame)
ANCHOR_ITEMS = [
    ("Tổng quan", 0.0),
    ("Yêu cầu đầu vào", 0.20),
    ("Học phí & Học bổng", 0.42),
    ("Ngành học", 0.65),
    ("Liên hệ", 0.85),
]


class DetailPage(tb.Frame):
    """Trang chi tiết 1 trường — nhận university_id qua refresh()."""

    def __init__(self, master, controller):
        super().__init__(master)
        self._controller = controller
        self._data: dict = {}
        self._colors = tb.Style().colors

        # ── Banner ───────────────────────────────────────────────────────
        self._banner = tb.Frame(self, bootstyle="primary", padding=(28, 16))
        self._banner.pack(fill="x")

        tb.Button(
            self._banner, text="← Quay lại", style="BannerLink.TButton",
            command=self._on_back,
        ).pack(anchor="w")

        self._name_lbl = tb.Label(
            self._banner, text="", bootstyle="inverse-primary",
            font=("Segoe UI", 16, "bold"),
        )
        self._name_lbl.pack(anchor="w", pady=(4, 0))

        self._location_lbl = tb.Label(
            self._banner, text="", bootstyle="inverse-primary",
        )
        self._location_lbl.pack(anchor="w")

        # Nút Quan tâm + So sánh trên banner (yêu cầu Issue 2.11)
        action_row = tb.Frame(self._banner, bootstyle="primary")
        action_row.pack(anchor="w", pady=(10, 0))

        self._watchlist_btn = tb.Button(
            action_row, text="☆ Lưu vào quan tâm",
            style="BannerLink.TButton", command=self._toggle_watchlist,
        )
        self._watchlist_btn.pack(side="left", padx=(0, 16))

        self._compare_btn = tb.Button(
            action_row, text="📊 Thêm vào so sánh",
            style="BannerLink.TButton", command=self._toggle_compare,
        )
        self._compare_btn.pack(side="left")

        # ── Scrollable body ──────────────────────────────────────────────
        self._scroll = ScrollableFrame(self)
        self._scroll.pack(fill="both", expand=True)

    # ─── Frame contract ──────────────────────────────────────────────────

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

    def _on_back(self):
        """Quay lại màn hình trước đó trong navigation stack."""
        if hasattr(self._controller, "go_back"):
            self._controller.go_back()
        else:
            self._controller.show_frame("home")

    # ─── Helpers ─────────────────────────────────────────────────────────

    def _v(self, key, *fallback_keys, default="N/A"):
        """Lấy giá trị từ self._data, thử lần lượt key chính rồi fallback.
        Trả về `default` nếu tất cả đều None / không tồn tại."""
        val = self._data.get(key)
        if val is not None:
            return val
        for fb in fallback_keys:
            val = self._data.get(fb)
            if val is not None:
                return val
        return default

    def _fmt_tuition(self):
        """Định dạng học phí kèm đơn vị tiền tệ."""
        tuition = self._v("tuition_per_year", "tuition", default=None)
        currency = self._v("currency", default="USD")
        if isinstance(tuition, (int, float)):
            return f"{tuition:,.0f} {currency}"
        return "N/A"

    # ─── Render ──────────────────────────────────────────────────────────

    def _render(self):
        data = self._data
        uid = data.get("id", "")

        # Banner text
        self._name_lbl.configure(text=data.get("name", "Chưa chọn trường"))
        city = data.get("city", "")
        country = data.get("country", "")
        location = f"📍 {city}, {country}" if city else f"📍 {country}"
        self._location_lbl.configure(text=location)

        # Cập nhật trạng thái nút Quan tâm / So sánh
        if watchlist_service.is_in_watchlist(uid):
            self._watchlist_btn.configure(text="★ Đã quan tâm")
        else:
            self._watchlist_btn.configure(text="☆ Lưu vào quan tâm")

        if uid in compare_service.get_compare_ids():
            self._compare_btn.configure(text="📊 Đang so sánh")
        else:
            self._compare_btn.configure(text="📊 Thêm vào so sánh")

        # Clear + rebuild nội dung cuộn
        for w in self._scroll.body.winfo_children():
            w.destroy()

        self._build_stats()

        body = tb.Frame(self._scroll.body)
        body.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        body.columnconfigure(0, weight=0, minsize=180)
        body.columnconfigure(1, weight=1)

        self._build_toc(body)
        self._build_content(body)

    # ─── 4 Stat Cards ───────────────────────────────────────────────────

    def _build_stats(self):
        ranking = self._v("ranking", default=None)
        ranking_text = f"#{ranking}" if isinstance(ranking, (int, float)) else "N/A"

        stats = [
            ("🏆", "Xếp hạng", ranking_text),
            ("💰", "Học phí / năm", self._fmt_tuition()),
            ("📝", "IELTS tối thiểu", str(self._v("ielts_min", "ielts"))),
            ("📋", "GPA tối thiểu", str(self._v("gpa_min", "gpa"))),
        ]
        row = tb.Frame(self._scroll.body)
        row.pack(fill="x", padx=28, pady=(16, 16))
        for i, (icon, label, value) in enumerate(stats):
            row.columnconfigure(i, weight=1, uniform="dstats")
            card = tb.Frame(row, bootstyle="light", padding=14)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            tb.Label(card, text=icon, font=("Segoe UI", 14)).pack(anchor="w")
            tb.Label(
                card, text=value, foreground=self._colors.primary,
                font=("Segoe UI", 13, "bold"),
            ).pack(anchor="w", pady=(4, 0))
            tb.Label(card, text=label, foreground=self._colors.secondary).pack(anchor="w")

    # ─── TOC (mục lục trái) ─────────────────────────────────────────────

    def _build_toc(self, parent):
        toc = tb.Frame(parent, bootstyle="light", padding=8)
        toc.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        tb.Label(
            toc, text="📋 Mục lục", foreground=self._colors.primary,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=8, pady=(4, 8))
        for label, fraction in ANCHOR_ITEMS:
            btn = tb.Button(
                toc, text=label, bootstyle="link",
                command=lambda f=fraction: self._scroll.scroll_to(f),
            )
            btn.pack(fill="x", anchor="w")

    # ─── Nội dung chính (5 phần) ────────────────────────────────────────

    def _build_content(self, parent):
        content = tb.Frame(parent, bootstyle="light", padding=20)
        content.grid(row=0, column=1, sticky="nsew")

        self._section_overview(content)
        tb.Separator(content).pack(fill="x", pady=20)
        self._section_admission(content)
        tb.Separator(content).pack(fill="x", pady=20)
        self._section_tuition(content)
        tb.Separator(content).pack(fill="x", pady=20)
        self._section_majors(content)
        tb.Separator(content).pack(fill="x", pady=20)
        self._section_contact(content)

    # ── 1. Tổng quan ────────────────────────────────────────────────────

    def _section_overview(self, parent):
        self._heading(parent, "Tổng quan")
        overview = self._v("overview", "description", default="Đang cập nhật thông tin...")
        tb.Label(
            parent, text=overview, foreground=self._colors.secondary,
            wraplength=560, justify="left",
        ).pack(anchor="w", pady=(0, 4))

    # ── 2. Yêu cầu đầu vào ─────────────────────────────────────────────

    def _section_admission(self, parent):
        self._heading(parent, "Yêu cầu đầu vào")

        items = [
            ("IELTS tối thiểu", self._v("ielts_min", "ielts")),
            ("TOEFL tối thiểu", self._v("toefl_min")),
            ("GPA tối thiểu", self._v("gpa_min", "gpa")),
            ("Hạn nộp hồ sơ", self._v("deadline")),
        ]
        for label, value in items:
            tb.Label(
                parent, text=f"•  {label}: {value}",
                foreground=self._colors.secondary,
            ).pack(anchor="w", pady=2)

        admission = self._data.get("admission_detail")
        if admission:
            tb.Label(
                parent, text="", foreground=self._colors.secondary,
            ).pack(anchor="w")  # khoảng cách nhỏ
            tb.Label(
                parent, text=admission, foreground=self._colors.secondary,
                wraplength=560, justify="left",
            ).pack(anchor="w", pady=(0, 4))

    # ── 3. Học phí & Học bổng ───────────────────────────────────────────

    def _section_tuition(self, parent):
        self._heading(parent, "Học phí & Học bổng")

        tb.Label(
            parent, text=f"•  Học phí / năm: {self._fmt_tuition()}",
            foreground=self._colors.secondary,
        ).pack(anchor="w", pady=2)

        tuition_detail = self._data.get("tuition_detail")
        if tuition_detail:
            tb.Label(
                parent, text=tuition_detail, foreground=self._colors.secondary,
                wraplength=560, justify="left",
            ).pack(anchor="w", pady=(4, 8))

        scholarship = self._data.get("scholarship")
        if scholarship:
            tb.Label(
                parent, text="🎓 Học bổng:", foreground=self._colors.primary,
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w", pady=(8, 4))
            tb.Label(
                parent, text=scholarship, foreground=self._colors.secondary,
                wraplength=560, justify="left",
            ).pack(anchor="w", pady=(0, 4))

    # ── 4. Ngành học ────────────────────────────────────────────────────

    def _section_majors(self, parent):
        self._heading(parent, "Ngành học")

        majors = self._data.get("majors")
        if majors and isinstance(majors, list):
            for major in majors:
                tb.Label(
                    parent, text=f"•  {major}",
                    foreground=self._colors.secondary,
                ).pack(anchor="w", pady=2)
        else:
            tb.Label(
                parent, text="Đang cập nhật...",
                foreground=self._colors.secondary,
            ).pack(anchor="w")

    # ── 5. Liên hệ ─────────────────────────────────────────────────────

    def _section_contact(self, parent):
        self._heading(parent, "Liên hệ")

        # seed_data dùng field phẳng (website, email); ARCHITECTURE.md mô tả
        # contact.website / contact.email — hỗ trợ cả hai
        contact = self._data.get("contact") or {}
        website = self._data.get("website") or contact.get("website")
        email = self._data.get("email") or contact.get("email")

        has_info = False
        if website:
            tb.Label(
                parent, text=f"🌐  {website}",
                foreground=self._colors.success, cursor="hand2",
            ).pack(anchor="w", pady=2)
            has_info = True
        if email:
            tb.Label(
                parent, text=f"📧  {email}",
                foreground=self._colors.secondary,
            ).pack(anchor="w", pady=2)
            has_info = True
        if not has_info:
            tb.Label(
                parent, text="Đang cập nhật thông tin liên hệ...",
                foreground=self._colors.secondary,
            ).pack(anchor="w")

    # ─── Shared UI helper ───────────────────────────────────────────────

    def _heading(self, parent, text):
        tb.Label(
            parent, text=text, foreground=self._colors.primary,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 8))

    # ─── Action handlers (banner buttons) ────────────────────────────────

    def _toggle_watchlist(self):
        uid = self._data.get("id", "")
        if not uid:
            return
        if watchlist_service.is_in_watchlist(uid):
            watchlist_service.remove_from_watchlist(uid)
        else:
            watchlist_service.add_to_watchlist(uid)
        self._render()

    def _toggle_compare(self):
        uid = self._data.get("id", "")
        if not uid:
            return
        ok, msg = compare_service.toggle_compare(uid)
        if not ok:
            messagebox.showwarning("Không thể thêm vào so sánh", msg)
            return
        self._render()
