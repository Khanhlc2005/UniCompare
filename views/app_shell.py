"""AppShell — cửa sổ chính của UniCompare.

Đúng Frame contract đã chốt (ARCHITECTURE.md mục 5.1):
- AppShell tạo cửa sổ chính (ttkbootstrap.Window), sidebar trái, 1 container.
- AppShell chính là `controller` truyền cho mỗi View: cung cấp
  `show_frame(name, **kwargs)` và các service/repo đã khởi tạo sẵn
  (`self.repo`).
- Mỗi View là 1 `ttk.Frame` con, được tạo 1 lần lúc khởi động và giữ nguyên
  trong bộ nhớ (không destroy/recreate) — chuyển màn bằng `tkraise()`.
- Mỗi View có `refresh(**kwargs)`, AppShell gọi trước khi tkraise() để dữ
  liệu luôn mới (VD Watchlist cập nhật sau khi lưu trường ở Search).

Bảng màu "Academic Precision" (theo University_Browser_Wireframes-print.pdf)
khai báo MỘT chỗ duy nhất ở đây qua `self.style.colors` (ARCHITECTURE.md
§5.3) — mọi file khác chỉ dùng bootstyle có sẵn (primary/success/danger/...),
không tự khai màu rời.
"""

import ttkbootstrap as tb

from views.components.sidebar import Sidebar
from views.components.home_page import HomePage
from views.components.detail_page import DetailPage
from views.components.watchlist_page import WatchlistPage
from views.components.compare_page import ComparePage
from views.components.placeholder_page import PlaceholderPage
from repositories.fake_repo import FakeRepo
from views.components.search_page import SearchPage


APP_TITLE = "UniCompare — Academic Insights"
MIN_WIDTH = 1100
MIN_HEIGHT = 700

# man nao chua co View that thi de placeholder (title, icon) - doi thanh
# class View that dan theo tung Issue trong PLAN.md
FRAME_SPECS = {
    "home": HomePage,
    "favorite": WatchlistPage,
    "detail": DetailPage,   # mo tu card, khong nam trong sidebar menu
    "search": SearchPage,
    "compare": ComparePage,
    "chatbot": ("Chatbot", "🤖"),
}


class AppShell(tb.Window):
    """Cửa sổ chính + sidebar + chuyển frame, đóng vai trò controller."""

    def __init__(self):
        super().__init__(
            title=APP_TITLE, themename="flatly",
            size=(1280, 800), minsize=(MIN_WIDTH, MIN_HEIGHT)
        )

        # bang mau "Academic Precision" - phai gan TRUOC khi tao widget nao
        # khac, vi ttkbootstrap dung mau nay de dung style luc widget tao ra
        self.style.colors.primary = "#1A237E"   # navy - tieu de, hanh dong chinh
        self.style.colors.success = "#008080"   # teal - highlight, CTA
        self.style.colors.danger = "#5C1800"    # maroon - hanh dong xoa/canh bao
        self.style.colors.dark = "#12194F"      # navy dam hon - nen sidebar + item chua active
        self.style.colors.bg = "#F4F6F9"        # nen toan trang, nhat hon card
        self.style.colors.light = "#FFFFFF"     # nen card, noi bat tren nen trang

        # ttkbootstrap luon to nen nut kieu "<mau>-link" bang colors.bg (mau
        # nen trang), nen bi lech khi dat nut do tren card/banner mau khac -
        # khai bao rieng 3 style Button "phang" (nen dung mau cha, chi doi
        # chu) ngay tai day, cac file khac chi tham chieu qua style=
        colors = self.style.colors
        for style_name, fg, bg in [
            ("BannerLink.TButton", colors.light, colors.primary),      # nut tren banner navy
            ("CardDangerLink.TButton", colors.danger, colors.light),   # nut "Bo luu" tren card trang
            ("CardTealLink.TButton", colors.success, colors.light),    # nut lien ket teal tren card trang
        ]:
            self.style.configure(style_name, foreground=fg, background=bg, borderwidth=0, focuscolor=bg)
            self.style.map(style_name, foreground=[("active", fg)], background=[("active", bg)])

        # repo dung chung cho moi View, lay qua controller.repo
        self.repo = FakeRepo()

        self._sidebar = Sidebar(self, on_navigate=self.show_frame)
        self._sidebar.pack(side="left", fill="y")

        container = tb.Frame(self)
        container.pack(side="right", fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        self._frames = {}
        for key, spec in FRAME_SPECS.items():
            if isinstance(spec, tuple):
                title, icon = spec
                frame = PlaceholderPage(container, self, title=title, icon=icon)
            else:
                frame = spec(container, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self._frames[key] = frame

        self.show_frame("home")

    def show_frame(self, name, **kwargs):
        """Controller API dùng chung cho mọi View: chuyển sang frame `name`,
        gọi refresh(**kwargs) trước khi đưa lên để dữ liệu luôn mới."""
        frame = self._frames.get(name)
        if frame is None:
            return
        if hasattr(frame, "refresh"):
            frame.refresh(**kwargs)
        frame.tkraise()
        self._sidebar.set_active(name)
