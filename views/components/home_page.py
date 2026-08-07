# -*- coding: utf-8 -*-
"""Trang chủ (Home) — Issue 2.12.

Nâng cấp HomeView:
- 3 StatCard với số liệu thật từ repo (tổng số trường, số quốc gia, số ngành học).
- Lối tắt 4 tính năng chính (Quan tâm, Tìm kiếm, So sánh, Chatbot) điều hướng qua show_frame().
- Danh sách trường nổi bật dạng card, bấm vào tên/nút/card đều mở đúng DetailView.
- Đúng Frame contract (ARCHITECTURE.md mục 5.1): refresh() cập nhật số liệu mỗi khi quay lại trang.
"""

import ttkbootstrap as tb
from pymongo.errors import PyMongoError

from repositories.mongo_repo import MongoRepositoryError
from views.components.scrollable_frame import ScrollableFrame
from views.components.state_banner import StateBanner

FEATURES_DATA = [
    ("⭐", "Quan tâm", "Quản lý danh sách các trường bạn yêu thích", "favorite"),
    ("🔍", "Tìm kiếm", "Tìm kiếm trường theo nhiều tiêu chí khác nhau", "search"),
    ("📊", "So sánh", "So sánh chi tiết giữa các trường đại học", "compare"),
    ("🤖", "Chatbot", "Hỏi đáp thông minh với trợ lý AI", "chatbot"),
]


class HomePage(tb.Frame):
    """Trang chủ — stat card số liệu thật, lối tắt tính năng, trường nổi bật."""

    def __init__(self, master, controller):
        super().__init__(master)
        self._controller = controller
        self._colors = tb.Style().colors

        self._scroll = ScrollableFrame(self)
        self._scroll.pack(fill="both", expand=True)

        self._build_header()

        # Frame chứa stats + featured động (re-render khi refresh)
        self._stats_container = tb.Frame(self._scroll.body)
        self._stats_container.pack(fill="x", padx=28, pady=(0, 16))

        self._build_features()

        self._featured_container = tb.Frame(self._scroll.body)
        self._featured_container.pack(fill="x", padx=28, pady=(0, 24))

        # Render ban đầu
        self._render()

    def refresh(self, **kwargs):
        """AppShell gọi khi chuyển về trang Home — nạp lại số liệu mới nhất."""
        self._render()

    def _render(self):
        """Cập nhật dữ liệu thật cho StatCard và Trường nổi bật.

        Issue #54 (edge case mất kết nối Mongo): gọi repo.get_all() TRƯỚC
        khi đụng tới bất kỳ widget nào - nếu Mongo rớt kết nối giữa lúc
        đang dùng app (không phải lúc mở app - trường hợp đó app_shell.py
        đã tự fallback FakeRepo), nội dung cũ trên 2 container vẫn còn
        nguyên vẹn cho tới khi ta chủ động thay bằng StateBanner lỗi, không
        bao giờ để lại 1 vùng trắng dở dang.
        """
        try:
            all_unis = self._controller.repo.get_all()
        except (MongoRepositoryError, PyMongoError) as exc:
            self._render_error(exc)
            return

        self._render_stats(all_unis)
        self._render_featured(all_unis)

    def _render_error(self, exc):
        for container in (self._stats_container, self._featured_container):
            for w in container.winfo_children():
                w.destroy()
        StateBanner.mongo_error(self._featured_container, exc).pack(fill="x")

    # ── 1. Header Banner ──────────────────────────────────────────────────

    def _build_header(self):
        banner = tb.Frame(self._scroll.body, bootstyle="primary", padding=24)
        banner.pack(fill="x", padx=28, pady=(20, 16))
        tb.Label(
            banner, text="Chào mừng trở lại 👋", bootstyle="inverse-primary",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")
        tb.Label(
            banner, bootstyle="inverse-primary",
            text="Khám phá và so sánh các trường đại học hàng đầu trên toàn thế giới.",
        ).pack(anchor="w", pady=(4, 0))

    # ── 2. Stat Cards (Số liệu thật) ──────────────────────────────────────

    def _render_stats(self, all_unis: list[dict]):
        # Clear container cũ
        for w in self._stats_container.winfo_children():
            w.destroy()

        total_unis = len(all_unis)
        countries = {u.get("country") for u in all_unis if u.get("country")}
        
        # Đếm tổng số ngành học duy nhất từ seed/mongo
        all_majors = set()
        for u in all_unis:
            m_list = u.get("majors", [])
            if isinstance(m_list, list):
                for m in m_list:
                    if m:
                        all_majors.add(m)

        stats_data = [
            ("📚", "Tổng số trường", f"{total_unis} trường"),
            ("🌍", "Quốc gia", f"{len(countries)} quốc gia"),
            ("🎓", "Số ngành học", f"{len(all_majors)} ngành" if all_majors else "Đang cập nhật"),
        ]

        for i, (icon, title, value) in enumerate(stats_data):
            self._stats_container.columnconfigure(i, weight=1, uniform="stats")
            card = tb.Frame(self._stats_container, bootstyle="light", padding=16)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            
            card.columnconfigure(1, weight=1)
            tb.Label(card, text=icon, font=("Segoe UI", 20)).grid(
                row=0, column=0, rowspan=2, sticky="ns", padx=(0, 12)
            )
            tb.Label(
                card, text=title, foreground=self._colors.secondary,
                font=("Segoe UI", 9, "bold"),
            ).grid(row=0, column=1, sticky="sw")
            tb.Label(
                card, text=value, foreground=self._colors.primary,
                font=("Segoe UI", 15, "bold"),
            ).grid(row=1, column=1, sticky="nw")

    # ── 3. Lối tắt tính năng ──────────────────────────────────────────────

    def _build_features(self):
        row = tb.Frame(self._scroll.body)
        row.pack(fill="x", padx=28, pady=(0, 20))
        for i, (icon, title, desc, nav_key) in enumerate(FEATURES_DATA):
            row.columnconfigure(i, weight=1, uniform="features")
            card = tb.Frame(row, bootstyle="light", padding=16, cursor="hand2")
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            
            tb.Label(card, text=icon, font=("Segoe UI", 18)).pack(anchor="w")
            tb.Label(
                card, text=title, foreground=self._colors.primary,
                font=("Segoe UI", 11, "bold"),
            ).pack(anchor="w", pady=(8, 4))
            tb.Label(
                card, text=desc, foreground=self._colors.secondary,
                wraplength=180, justify="left",
            ).pack(anchor="w")
            
            btn = tb.Button(
                card, text="Xem danh sách →", style="CardTealLink.TButton",
                command=lambda k=nav_key: self._controller.show_frame(k),
            )
            btn.pack(anchor="w", pady=(12, 0))

            # Bấm vào toàn bộ card cũng chuyển trang
            card.bind("<Button-1>", lambda e, k=nav_key: self._controller.show_frame(k))

    # ── 4. Trường nổi bật (Cards) ─────────────────────────────────────────

    def _render_featured(self, all_unis: list[dict]):
        # Clear container cũ
        for w in self._featured_container.winfo_children():
            w.destroy()

        header_row = tb.Frame(self._featured_container)
        header_row.pack(fill="x", pady=(0, 12))
        
        tb.Label(
            header_row, text="🎓 Trường nổi bật", foreground=self._colors.primary,
            font=("Segoe UI", 13, "bold"),
        ).pack(side="left")

        tb.Button(
            header_row, text="Tất cả trường →", style="CardTealLink.TButton",
            command=lambda: self._controller.show_frame("search"),
        ).pack(side="right")

        if not all_unis:
            StateBanner(
                self._featured_container, "Chưa có dữ liệu trường đại học.",
                icon="🎓",
            ).pack(fill="x")
            return

        # Lấy top 4 trường xếp hạng cao nhất (hoặc 4 trường đầu)
        sorted_unis = sorted(
            all_unis,
            key=lambda x: x.get("ranking") if isinstance(x.get("ranking"), (int, float)) else 999
        )[:4]

        # Hiển thị dạng grid 2x2
        cards_grid = tb.Frame(self._featured_container)
        cards_grid.pack(fill="x")
        cards_grid.columnconfigure(0, weight=1, uniform="feat_col")
        cards_grid.columnconfigure(1, weight=1, uniform="feat_col")

        for idx, uni in enumerate(sorted_unis):
            r = idx // 2
            c = idx % 2
            
            uid = uni.get("id") or str(uni.get("_id", ""))
            name = uni.get("name", "N/A")
            country = uni.get("country", "")
            city = uni.get("city", "")
            location = f"📍 {city}, {country}" if city else f"📍 {country}"
            ranking = uni.get("ranking")
            rank_str = f"#{ranking}" if isinstance(ranking, (int, float)) else ""

            card = tb.Frame(cards_grid, bootstyle="light", padding=16, cursor="hand2")
            card.grid(row=r, column=c, sticky="nsew", padx=(0 if c == 0 else 6, 6 if c == 0 else 0), pady=6)

            # Header card: Rank tag + Location
            top_bar = tb.Frame(card, bootstyle="light")
            top_bar.pack(fill="x")
            
            if rank_str:
                tb.Label(
                    top_bar, text=rank_str, foreground=self._colors.primary,
                    font=("Segoe UI", 10, "bold"), bootstyle="secondary",
                ).pack(side="left")

            tb.Label(
                top_bar, text=location, foreground=self._colors.secondary,
                font=("Segoe UI", 9),
            ).pack(side="right")

            # Tên trường
            name_lbl = tb.Label(
                card, text=name, foreground=self._colors.primary,
                font=("Segoe UI", 11, "bold"), wraplength=260, justify="left",
                cursor="hand2",
            )
            name_lbl.pack(anchor="w", pady=(8, 12))

            # Action button
            btn_frame = tb.Frame(card, bootstyle="light")
            btn_frame.pack(fill="x")
            
            detail_btn = tb.Button(
                btn_frame, text="Xem chi tiết →", style="CardTealLink.TButton",
                command=lambda u_id=uid: self._open_detail(u_id),
            )
            detail_btn.pack(side="left")

            # Bind click cho toàn bộ card
            card.bind("<Button-1>", lambda e, u_id=uid: self._open_detail(u_id))
            name_lbl.bind("<Button-1>", lambda e, u_id=uid: self._open_detail(u_id))

    def _open_detail(self, university_id: str):
        """Mở trang chi tiết cho trường được chọn."""
        if university_id:
            self._controller.show_frame("detail", university_id=university_id)
