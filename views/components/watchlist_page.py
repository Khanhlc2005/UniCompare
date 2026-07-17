"""Trang Quan tâm (Watchlist) — Issue 1.7.

Kế thừa ttk.Frame(master, controller) đúng Frame contract (ARCHITECTURE.md
mục 5.1). `refresh()` được AppShell gọi mỗi lần frame được tkraise() lên,
đọc lại watchlist_service/compare_service để dữ liệu luôn mới (VD vừa lưu
trường ở màn Search). Vẫn dùng fake_repo qua controller.repo (tuần 1),
chưa đổi mongo_repo.
"""

import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as tb

from services import watchlist_service, compare_service
from views.components.scrollable_frame import ScrollableFrame
from views.components.pill_filter import PillFilter
from views.components.compare_bar import CompareBar


class WatchlistPage(tb.Frame):
    """Trang Quan tâm — card trường đã lưu + pill quốc gia + tick so sánh."""

    def __init__(self, master, controller):
        super().__init__(master)
        self._controller = controller
        self._active_country = None  # None = xem tat ca quoc gia
        self._colors = tb.Style().colors

        self._scroll = ScrollableFrame(self)
        self._scroll.pack(fill="both", expand=True)

    def refresh(self, **kwargs):
        """AppShell goi moi lan man nay duoc dua len - doc lai state moi nhat."""
        self._render()

    def _get_watchlist_data(self):
        data = []
        for uid in watchlist_service.get_watchlist_ids():
            uni = self._controller.repo.get_by_id(uid)
            if uni:
                data.append(uni)
        return data

    def _render(self):
        for w in self._scroll.body.winfo_children():
            w.destroy()

        # nam truc tiep tren nen trang (khong phai trong card trang) nen
        # dung bootstyle="primary" (tu khop mau nen trang), KHONG dung
        # foreground=... tren Label thuong (mac dinh luon nen trang, se
        # lech mau voi nen trang xam nhat - xem app_shell.py doan khai bao style)
        tb.Label(
            self._scroll.body, text="Quan tâm", bootstyle="primary",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=28, pady=(20, 12))

        all_data = self._get_watchlist_data()

        if not all_data:
            self._build_empty_state(
                "Chưa có trường nào trong danh sách quan tâm.\n"
                "Vào Tìm kiếm để lưu trường bạn thích."
            )
            return

        compare_bar = CompareBar(self._scroll.body, on_compare=self._go_to_compare)
        compare_bar.pack(fill="x", padx=28, pady=(0, 12))

        # pill loc quoc gia lay tu chinh cac truong da luu (khong phai toan bo DB)
        countries = sorted({uni["country"] for uni in all_data})
        pill = PillFilter(
            self._scroll.body, options=countries, active=self._active_country,
            on_select=self._on_filter_country,
        )
        pill.pack(anchor="w", padx=28, pady=(0, 16))

        shown = [
            uni for uni in all_data
            if not self._active_country or uni["country"] == self._active_country
        ]

        if not shown:
            self._build_empty_state(
                f"Không có trường nào ở {self._active_country} trong danh sách quan tâm."
            )
            return

        grid = tb.Frame(self._scroll.body)
        grid.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        cols = 3
        for i in range(cols):
            grid.columnconfigure(i, weight=1, uniform="watchlist")

        for idx, uni in enumerate(shown):
            card = self._build_card(grid, uni)
            card.grid(row=idx // cols, column=idx % cols, sticky="nsew", padx=6, pady=6)

    def _build_empty_state(self, message):
        empty = tb.Frame(self._scroll.body, bootstyle="light", padding=40)
        empty.pack(fill="x", padx=28, pady=20)
        tb.Label(empty, text="⭐", font=("Segoe UI", 32)).pack()
        tb.Label(empty, text=message, foreground=self._colors.secondary, justify="center").pack(pady=(10, 0))

    def _build_card(self, parent, uni):
        card = tb.Frame(parent, bootstyle="light", padding=16)

        tb.Label(
            card, text=uni.get("name", ""), foreground=self._colors.primary,
            font=("Segoe UI", 11, "bold"), wraplength=220, justify="left"
        ).pack(anchor="w")

        tb.Label(
            card, text=f"📍 {uni.get('country', '')}", foreground=self._colors.secondary
        ).pack(anchor="w", pady=(4, 8))

        tuition = uni.get("tuition")
        tuition_text = f"${tuition:,}" if isinstance(tuition, (int, float)) else "N/A"
        stats = f"GPA {uni.get('gpa', 'N/A')}  •  IELTS {uni.get('ielts', 'N/A')}  •  {tuition_text}"
        tb.Label(card, text=stats, foreground=self._colors.secondary).pack(anchor="w", pady=(0, 10))

        action_row = tb.Frame(card, bootstyle="light")
        action_row.pack(fill="x")

        tb.Button(
            action_row, text="🗑 Bỏ lưu", style="CardDangerLink.TButton",
            command=lambda uid=uni["id"]: self._remove(uid)
        ).pack(side="left")

        compare_var = tk.BooleanVar(value=uni["id"] in compare_service.get_compare_ids())
        chk = tb.Checkbutton(
            action_row, text="So sánh", variable=compare_var,
            bootstyle="success-round-toggle",
            command=lambda uid=uni["id"], var=compare_var: self._toggle_compare(uid, var)
        )
        chk.pack(side="right")

        return card

    def _remove(self, uni_id):
        watchlist_service.remove_from_watchlist(uni_id)
        self._render()

    def _toggle_compare(self, uni_id, var):
        ok, msg = compare_service.toggle_compare(uni_id)
        if not ok:
            var.set(False)  # bi chan (qua 5 truong) thi bo tick lai
            messagebox.showwarning("Không thể thêm vào so sánh", msg)
            return
        self._render()

    def _on_filter_country(self, country):
        self._active_country = country
        self._render()

    def _go_to_compare(self):
        self._controller.show_frame("compare")
