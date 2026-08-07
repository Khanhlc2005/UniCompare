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

import tkinter as tk
import traceback
from tkinter import messagebox

import ttkbootstrap as tb
from pymongo.errors import PyMongoError

from repositories.mongo_repo import MongoRepositoryError
from views.components.sidebar import Sidebar
from views.components.home_page import HomePage
from views.components.detail_page import DetailPage
from views.components.watchlist_page import WatchlistPage
from views.components.compare_page import ComparePage
from views.components.placeholder_page import PlaceholderPage
from repositories.fake_repo import FakeRepo
from repositories.mongo_repo import MongoUniversityRepository
import config
from views.components.search_page import SearchPage
from views.components.chatbot_page import ChatbotPage
from views.admin_view import open_admin_window


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
    "chatbot": ChatbotPage,
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
            ("MessengerBlue.TButton", colors.light, "#0084FF"),        # nut style Messenger Blue
            ("QuickPill.TButton", "#0084FF", "#E7F3FF"),               # nut pill goi y nhanh messenger
        ]:
            self.style.configure(style_name, foreground=fg, background=bg, borderwidth=0, focuscolor=bg)
            self.style.map(style_name, foreground=[("active", fg)], background=[("active", bg)])

        # Messenger Chat Bubble Label styles
        self.style.configure("UserBubble.TLabel", background="#0084FF", foreground="#FFFFFF", font=("Segoe UI", 10, "bold"), padding=(14, 10))
        self.style.configure("BotBubble.TLabel", background="#E7F3FF", foreground="#0F172A", font=("Segoe UI", 10), padding=(14, 10))

        # repo dung chung cho moi View, lay qua controller.repo
        # Issue 2.3: dùng MongoRepo nếu có MONGO_URI, fallback FakeRepo nếu lỗi kết nối
        if config.has_mongo():
            try:
                mongo_repo = MongoUniversityRepository()
                mongo_repo.get_all()  # Test kết nối sớm
                self.repo = mongo_repo
            except Exception as err:
                print(f"[Cảnh báo MongoDB Atlas] {err}\n  -> Tự động dùng FakeRepo để ứng dụng tiếp tục chạy bình thường.")
                self.repo = FakeRepo()
        else:
            self.repo = FakeRepo()

        # Admin man rieng ngoai luong chinh (ARCHITECTURE.md muc 5.2, wireframe 8)
        # - khong nam trong sidebar/tkraise, mo bang Toplevel qua menu bar.
        self.config(menu=self._build_menu_bar())

        self._sidebar = Sidebar(self, on_navigate=self.show_frame)
        self._sidebar.pack(side="left", fill="y")

        container = tb.Frame(self)
        container.pack(side="right", fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        self._current_frame_name = None
        self._nav_stack = []

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

    def _build_menu_bar(self):
        """Menu bar rieng cho Admin - tach khoi sidebar vi Admin khong phai
        1 trong 5 frame chinh (xem PLAN.md Issue 1.9: "Admin tach rieng")."""
        menu_bar = tk.Menu(self)
        quan_tri_menu = tk.Menu(menu_bar, tearoff=False)
        quan_tri_menu.add_command(label="Mở màn Quản trị", command=self._open_admin)
        menu_bar.add_cascade(label="Quản trị", menu=quan_tri_menu)
        return menu_bar

    def _open_admin(self):
        open_admin_window(self, self.repo)

    def show_frame(self, name, is_back=False, **kwargs):
        """Controller API dùng chung cho mọi View: chuyển sang frame `name`,
        gọi refresh(**kwargs) trước khi đưa lên để dữ liệu luôn mới."""
        frame = self._frames.get(name)
        if frame is None:
            return

        if not is_back:
            if self._current_frame_name and self._current_frame_name != name:
                self._nav_stack.append(self._current_frame_name)

        self._current_frame_name = name

        if hasattr(frame, "refresh"):
            frame.refresh(**kwargs)
        frame.tkraise()
        self._sidebar.set_active(name)

    def go_back(self, fallback="home"):
        """Quay lại màn hình trước đó trong Navigation Stack."""
        if self._nav_stack:
            prev_name = self._nav_stack.pop()
        else:
            prev_name = fallback
        self.show_frame(prev_name, is_back=True)

    def report_callback_exception(self, exc, val, tb_obj):
        """Issue #54 (edge case mất kết nối Mongo): lưới an toàn cuối cùng.

        Tkinter tự gọi hàm này thay vì để lỗi văng thẳng ra console mỗi khi
        một callback (click nút, refresh() lúc tkraise()...) ném exception
        không được bắt cục bộ. Các View NÊN tự bắt MongoRepositoryError ở
        chỗ gọi repo (xem StateBanner.mongo_error) để hiện thông báo ngay
        trong màn hình thay vì mất nội dung cũ; hàm này chỉ là lưới an toàn
        cho phần chưa/không tự bắt được (VD nút Bỏ lưu/Thêm vào so sánh khi
        Mongo vừa rớt giữa chừng) — mục tiêu duy nhất: KHÔNG BAO GIỜ để lộ
        traceback thô cho người dùng (config.py mục 7).
        """
        # log day du ra console cho dev debug, nguoi dung chi thay hop thoai gon
        traceback.print_exception(exc, val, tb_obj)

        if isinstance(val, (MongoRepositoryError, PyMongoError)):
            messagebox.showerror(
                "Mất kết nối MongoDB",
                "Không thể kết nối hoặc thao tác với MongoDB Atlas.\n"
                f"{val}\n\n"
                "Kiểm tra mạng / MONGO_URI rồi thử lại.",
                parent=self,
            )
        else:
            messagebox.showerror(
                "Đã có lỗi xảy ra",
                f"{val}\n\nVui lòng thử lại thao tác vừa rồi.",
                parent=self,
            )
