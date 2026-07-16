"""AppShell — Khung ứng dụng chính của UniCompare.

Kết hợp Sidebar + Main Content area.
Điều khiển việc chuyển đổi giữa các trang (HomePage, DetailPage, ...).

Cơ chế mở rộng (dành cho đồng đội):
    AppShell tự động tra cứu PAGE_REGISTRY trong base_page.py.
    Đồng đội chỉ cần:
    1. Tạo class kế thừa BasePage trong views/components/
    2. Đăng ký: PAGE_REGISTRY["menu_key"] = MyPage
    → AppShell sẽ tự hiển thị khi user click menu tương ứng.
"""

import tkinter as tk
from views.components.sidebar import Sidebar
from views.components.home_page import HomePage
from views.components.detail_page import DetailPage
from views.components.base_page import PAGE_REGISTRY, BasePage
from repositories.fake_repo import FakeRepo


# ─── Hằng số ──────────────────────────────────────────────────
MAIN_BG = "#F4F6F9"
APP_TITLE = "UniCompare — Academic Insights"
MIN_WIDTH = 1100
MIN_HEIGHT = 700


class AppShell(tk.Tk):
    """Cửa sổ chính của ứng dụng UniCompare.

    Navigation flow:
        Sidebar click → _handle_navigate(key)
                       → Nếu key == "home": hiển thị HomePage
                       → Nếu key có trong PAGE_REGISTRY: hiển thị page đã đăng ký
                       → Nếu không: hiển thị placeholder BasePage

    Để thêm trang mới (dành cho đồng đội):
        Xem hướng dẫn trong base_page.py
    """

    def __init__(self):
        super().__init__()

        # Window setup
        self.title(APP_TITLE)
        self.geometry("1280x800")
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.configure(bg=MAIN_BG)

        # Cố gắng set icon (bỏ qua nếu thất bại)
        try:
            # Tạo icon đơn giản bằng PhotoImage
            icon = tk.PhotoImage(width=32, height=32)
            icon.put(("#4CAF50",), to=(0, 0, 32, 32))
            self.iconphoto(True, icon)
        except Exception:
            pass

        # Repository
        self._repo = FakeRepo()

        # Layout: Sidebar (trái) + Content (phải)
        self._sidebar = Sidebar(self, on_navigate=self._handle_navigate)
        self._sidebar.pack(side="left", fill="y")

        self._content_area = tk.Frame(self, bg=MAIN_BG)
        self._content_area.pack(side="right", fill="both", expand=True)

        # Current page reference
        self._current_page = None

        # Hiển thị trang chủ mặc định
        self._show_home()

    # ─── Navigation ───────────────────────────────────────────
    def _handle_navigate(self, key):
        """Xử lý điều hướng từ sidebar.

        Ưu tiên:
        1. "home" → HomePage (hardcoded vì là trang chính)
        2. PAGE_REGISTRY[key] → trang đã đăng ký bởi đồng đội
        3. Fallback → BasePage placeholder (hiển thị "đang phát triển")
        """
        if key == "home":
            self._show_home()
            return

        # Tra cứu registry — đồng đội đăng ký page vào đây
        page_class = PAGE_REGISTRY.get(key)
        if page_class:
            self._show_registered_page(key, page_class)
        else:
            # Chưa ai đăng ký → hiển thị placeholder
            self._show_placeholder(key)

    def _clear_content(self):
        """Xóa nội dung hiện tại trong content area."""
        if self._current_page:
            self._current_page.destroy()
            self._current_page = None

    def _show_home(self):
        """Hiển thị trang chủ."""
        self._clear_content()
        self._current_page = HomePage(
            self._content_area,
            on_navigate=self._handle_navigate,
            on_view_detail=self._show_detail
        )
        self._current_page.pack(fill="both", expand=True)
        # Cập nhật sidebar
        self._sidebar._update_active("home")

    def _show_detail(self, uni_id: str):
        """Hiển thị trang chi tiết trường."""
        uni_data = self._repo.get_by_id(uni_id)
        if not uni_data:
            # Fallback: dùng trường đầu tiên
            all_unis = self._repo.get_all()
            uni_data = all_unis[0] if all_unis else {
                "name": "Trường không tìm thấy",
                "country": "N/A",
                "description": "Không có dữ liệu.",
                "gpa": 0,
                "ielts": 0,
                "tuition": 0,
            }

        self._clear_content()
        self._current_page = DetailPage(
            self._content_area,
            uni_data=uni_data,
            on_back=self._show_home
        )
        self._current_page.pack(fill="both", expand=True)

    def _show_registered_page(self, key, page_class):
        """Hiển thị trang đã đăng ký trong PAGE_REGISTRY."""
        self._clear_content()
        self._current_page = page_class(
            self._content_area,
            on_navigate=self._handle_navigate
        )
        self._current_page.pack(fill="both", expand=True)
        self._sidebar._update_active(key)

    def _show_placeholder(self, key):
        """Hiển thị trang placeholder cho tính năng chưa triển khai."""
        # Tạo placeholder page với title tương ứng
        PLACEHOLDER_TITLES = {
            "favorite": ("Quan tâm", "⭐"),
            "search": ("Tìm kiếm", "🔍"),
            "compare": ("So sánh", "📊"),
            "chatbot": ("Chatbot", "🤖"),
        }
        title, icon = PLACEHOLDER_TITLES.get(key, ("Trang", "📄"))

        self._clear_content()

        # Tạo BasePage tạm với title phù hợp
        page = BasePage(self._content_area, on_navigate=self._handle_navigate)
        page.PAGE_TITLE = title
        page.PAGE_ICON = icon
        # Rebuild content với title đúng
        for widget in page._scroll_frame.winfo_children():
            widget.destroy()
        page._build_header()
        page._build_content(page._scroll_frame)

        self._current_page = page
        self._current_page.pack(fill="both", expand=True)
        self._sidebar._update_active(key)
