"""Trang Tìm kiếm (SearchPage) — Issue 1.5, dùng university_service (Issue 1.4).

Đúng Frame contract (ARCHITECTURE.md mục 5.1): kế thừa thẳng ttk.Frame,
constructor (master, controller), có refresh(). Pill filter dùng lại
PillFilter đã có sẵn (ARCHITECTURE.md mục 5.3: ttk.Radiobutton
bootstyle="toolbutton"), KHÔNG tự vẽ lại bằng tk.Canvas.

Bố cục theo wireframe 3: search bar -> 3 nhóm pill (Quốc gia / Học phí /
IELTS, kết hợp AND với nhau) -> card grid kết quả.

Dữ liệu: dùng controller.repo (fake_repo ở tuần 1). Khi Issue 2.3 đổi sang
mongo_repo ở app_shell.py, page này không cần sửa gì vì chỉ phụ thuộc
UniversityRepo interface (get_all/search) qua university_service.

Issue 2.9 (Khánh): thêm StickyCompareBar dùng chung với Watchlist + nút
tick "So sánh" trên mỗi card — CHỈ thêm phần này, không đổi logic
search/filter của Huy ở trên.
"""

import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as tb

from services import university_service, compare_service
from views.components.scrollable_frame import ScrollableFrame
from views.components.compare_bar import CompareBar
ALL_LABEL="Tất cả"
# (nhãn hiển thị, tuition_max) — None = không giới hạn, không nằm trong pill
TUITION_PILLS = [
    ("≤ $25,000", 25000),
    ("≤ $40,000", 40000),
    ("≤ $55,000", 55000),
]

# (nhãn hiển thị, ielts_max)
IELTS_PILLS = [
    ("≤ 6.5", 6.5),
    ("≤ 7.0", 7.0),
    ("≤ 7.5", 7.5),
]
# so ket qua/trang - khop luoi 3 cot san co (3 hang/trang)
PAGE_SIZE = 9

class SearchPage(tb.Frame):
    """Trang Tìm kiếm — search bar + 3 nhóm pill filter + card grid."""

    def __init__(self, master, controller):
        super().__init__(master)
        self._controller = controller
        self._colors = tb.Style().colors

        # state cac dieu kien loc hien tai (AND voi nhau)
        self._active_country = None
        self._active_tuition_label = None
        self._active_ielts_label = None
        self._page = 1  # trang hien tai (Issue 2.6), reset ve 1 moi khi doi filter/keyword
        self._keyword_var = tk.StringVar()
        # go phim -> loc lai ngay (khong can nut "Tim"), dung cho UX pill filter
        self._keyword_var.trace_add("write", lambda *_: self._on_filters_changed())
        self._country_var=tk.StringVar(value=ALL_LABEL)
        self._tuition_var=tk.StringVar(value=ALL_LABEL)
        self._ielts_var=tk.StringVar(value=ALL_LABEL)
        
        self._scroll = ScrollableFrame(self)
        self._scroll.pack(fill="both", expand=True)

        self._build_header()

        # 3 khu vuc nay se bi xoa/ve lai moi lan filter doi (_render); search
        # bar nam ngoai de khong mat focus/con tro khi go tung ky tu.
        # _compare_bar_holder khong co padx/pady rieng - de luc CompareBar tu
        # an (0 truong duoc chon) thi khong con khoang trong thua lai (xem
        # compare_bar.py refresh())
        self._compare_bar_holder = tb.Frame(self._scroll.body)
        self._compare_bar_holder.pack(fill="x")
        self._results_holder = tb.Frame(self._scroll.body)
        self._results_holder.pack(fill="both", expand=True, padx=28, pady=(0, 24))

        self._render()

    def _build_header(self):
        tb.Label(
            self._scroll.body, text="Tìm kiếm", bootstyle="primary",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=28, pady=(20, 12))

        search_row = tb.Frame(self._scroll.body)
        search_row.pack(fill="x", padx=28, pady=(0, 16))
        tb.Entry(
            search_row, textvariable=self._keyword_var, font=("Segoe UI", 11)
        ).pack(fill="x", ipady=4)
        filter_row = tb.Frame(self._scroll.body)
        filter_row.pack(fill="x", padx=28, pady=(0, 16))

        self._country_combo = self._build_filter_dropdown(
            filter_row, "Quốc gia", self._country_var, [], self._on_country_select
        )
        self._tuition_combo = self._build_filter_dropdown(
            filter_row, "Học phí", self._tuition_var,
            [l for l, _ in TUITION_PILLS], self._on_tuition_select
        )
        self._ielts_combo = self._build_filter_dropdown(
            filter_row, "IELTS", self._ielts_var,
            [l for l, _ in IELTS_PILLS], self._on_ielts_select
        )
    def _build_filter_dropdown(self, parent, title, var, options, handler):
        group = tb.Frame(parent)
        group.pack(side="left", padx=(0, 12), fill="x", expand=True)

        tb.Label(
            group, text=title, foreground=self._colors.secondary,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        combo = tb.Combobox(
            group, textvariable=var, values=[ALL_LABEL] + list(options),
            state="readonly", bootstyle="secondary",
        )
        combo.pack(fill="x", pady=(2, 0))
        combo.bind(
            "<<ComboboxSelected>>",
            lambda e, v=var, h=handler: h(None if v.get() == ALL_LABEL else v.get())
        )
        return combo

    def refresh(self, **kwargs):
        """AppShell gọi mỗi lần trang này được tkraise() lên - đọc lại dữ
        liệu mới nhất (VD vừa thêm trường mới ở màn Admin)."""
        self._render()

    def _render(self):
        for w in self._compare_bar_holder.winfo_children():
            w.destroy()
        for w in self._results_holder.winfo_children():
            w.destroy()

        self._build_compare_bar()
        self._refresh_country_options()

        tuition_max = dict(TUITION_PILLS).get(self._active_tuition_label)
        ielts_max = dict(IELTS_PILLS).get(self._active_ielts_label)

        results = university_service.search(
            self._controller.repo,
            keyword=self._keyword_var.get(),
            country=self._active_country,
            tuition_max=tuition_max,
            ielts_max=ielts_max,
        )

        if not results:
            self._build_empty_state()
            return

        # Issue 2.6: chi ve 1 trang, khong ve het toan bo results cung luc
        page_results, self._page, total_pages = university_service.phan_trang(
            results, self._page, PAGE_SIZE
        )

        grid = tb.Frame(self._results_holder)
        grid.pack(fill="both", expand=True)
        cols = 3
        for i in range(cols):
            grid.columnconfigure(i, weight=1, uniform="search")

        for idx, uni in enumerate(page_results):
            card = self._build_card(grid, uni)
            card.grid(row=idx // cols, column=idx % cols, sticky="nsew", padx=6, pady=6)

        if total_pages > 1:
            self._build_pagination(total_pages)

    def _build_compare_bar(self):
        """Issue 2.9: doc chung compare_service voi Watchlist - CompareBar tu
        an khi chua chon truong nao (xem compare_bar.py refresh())."""
        CompareBar(
            self._compare_bar_holder, on_compare=self._go_to_compare,
            pack_opts={"fill": "x", "padx": 28, "pady": (0, 12)},
        )

    def _go_to_compare(self):
        self._controller.show_frame("compare")

    def _refresh_country_options(self):
        countries = university_service.get_countries(self._controller.repo)
        self._country_combo["values"] = [ALL_LABEL] + list(countries)

    def _build_empty_state(self):
        empty = tb.Frame(self._results_holder, bootstyle="light", padding=40)
        empty.pack(fill="x", pady=20)
        tb.Label(empty, text="🔍", font=("Segoe UI", 32)).pack()
        tb.Label(
            empty, text="Không tìm thấy trường phù hợp với điều kiện đã chọn.",
            foreground=self._colors.secondary
        ).pack(pady=(10, 0))

    def _build_card(self, parent, uni):
        card = tb.Frame(parent, bootstyle="light", padding=16, cursor="hand2")

        name_lbl = tb.Label(
            card, text=uni.get("name", ""), foreground=self._colors.primary,
            font=("Segoe UI", 11, "bold"), wraplength=220, justify="left"
        )
        name_lbl.pack(anchor="w")

        country_lbl = tb.Label(
            card, text=f"📍 {uni.get('country', '')}", foreground=self._colors.secondary
        )
        country_lbl.pack(anchor="w", pady=(4, 8))

        # dung chung ham doc field voi university_service.search() de card
        # hien dung du lieu du khi con o fake_repo hay da doi sang schema chuan
        tuition = university_service.lay_hoc_phi(uni)
        tuition_text = f"${tuition:,.0f}" if tuition is not None else "N/A"
        ielts = university_service.lay_ielts(uni)
        gpa = uni.get("gpa_min", uni.get("gpa", "N/A"))
        stats_text = f"GPA {gpa}  •  IELTS {ielts if ielts is not None else 'N/A'}  •  {tuition_text}"
        stats_lbl = tb.Label(card, text=stats_text, foreground=self._colors.secondary)
        stats_lbl.pack(anchor="w", pady=(0, 8))

        # ca card co the click de mo Detail, khong chi rieng ten truong
        for widget in (card, name_lbl, country_lbl, stats_lbl):
            widget.bind(
                "<Button-1>",
                lambda e, uid=uni["id"]: self._controller.show_frame("detail", university_id=uid)
            )

        # Issue 2.9: tick them/bo truong khoi danh sach so sanh - dung chung
        # compare_service voi Watchlist, khong giu state rieng o day
        compare_var = tk.BooleanVar(value=uni["id"] in compare_service.get_compare_ids())
        tb.Checkbutton(
            card, text="So sánh", variable=compare_var,
            bootstyle="success-round-toggle",
            command=lambda uid=uni["id"], var=compare_var: self._toggle_compare(uid, var)
        ).pack(anchor="w")

        return card

    def _toggle_compare(self, uni_id, var):
        ok, msg = compare_service.toggle_compare(uni_id)
        if not ok:
            var.set(False)  # bi chan (qua 5 truong) thi bo tick lai
            messagebox.showwarning("Không thể thêm vào so sánh", msg)
            return
        self._render()

    def _build_pagination(self, total_pages):
        bar = tb.Frame(self._results_holder)
        bar.pack(fill="x", pady=(12, 0))

        tb.Button(
            bar, text="‹ Trước", bootstyle="secondary-outline",
            command=self._prev_page,
            state="normal" if self._page > 1 else "disabled",
        ).pack(side="left")

        tb.Label(
            bar, text=f"Trang {self._page}/{total_pages}",
            foreground=self._colors.secondary,
        ).pack(side="left", padx=12)

        tb.Button(
            bar, text="Sau ›", bootstyle="secondary-outline",
            command=self._next_page,
            state="normal" if self._page < total_pages else "disabled",
        ).pack(side="left")

    def _prev_page(self):
        self._page -= 1
        self._render()

    def _next_page(self):
        self._page += 1
        self._render()

    def _on_filters_changed(self):
        """Goi lai moi khi doi keyword/pill - reset ve trang 1 vi ket qua moi
        co the it hon trang dang xem (Issue 2.6)."""
        self._page = 1
        self._render()

    def _on_country_select(self, value):
        self._active_country = value
        self._on_filters_changed()

    def _on_tuition_select(self, value):
        self._active_tuition_label = value
        self._on_filters_changed()

    def _on_ielts_select(self, value):
        self._active_ielts_label = value
        self._on_filters_changed()
