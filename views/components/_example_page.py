"""Ví dụ: Cách tạo trang mới trong UniCompare.

File này là MẪU THAM KHẢO cho đồng đội.
Sau khi hiểu cách hoạt động, hãy xóa file này và tạo file riêng.

══════════════════════════════════════════════════════
HƯỚNG DẪN 3 BƯỚC ĐỂ THÊM TRANG MỚI:
══════════════════════════════════════════════════════

Bước 1: Tạo file views/components/<ten_trang>.py
Bước 2: Viết class kế thừa BasePage, override _build_content()
Bước 3: Đăng ký vào PAGE_REGISTRY

Xong! Không cần sửa app_shell.py hay sidebar.py.
══════════════════════════════════════════════════════
"""

import tkinter as tk
from views.components.base_page import BasePage, PAGE_REGISTRY
from views.components.base_page import MAIN_BG, CARD_BG, TEXT_DARK, TEXT_GRAY, BORDER_COLOR


class SearchPage(BasePage):
    """Trang Tìm kiếm — VÍ DỤ MẪU.

    Đây là ví dụ minh họa cách tạo trang mới.
    Đồng đội phụ trách trang Tìm kiếm sẽ thay thế nội dung này.
    """

    # Override tiêu đề và icon
    PAGE_TITLE = "Tìm kiếm trường đại học"
    PAGE_ICON = "🔍"

    def __init__(self, parent, on_navigate=None, **kwargs):
        # Nếu cần thêm tham số (VD: repo, service), thêm vào đây
        # self._repo = repo
        super().__init__(parent, on_navigate=on_navigate, **kwargs)

    def _build_content(self, container):
        """Override method này — đây là nơi xây dựng giao diện trang.

        Args:
            container: tk.Frame đã có sẵn scroll, cứ pack/grid thoải mái.
        """
        # ── Ví dụ: Search bar ──
        search_frame = tk.Frame(container, bg=CARD_BG, padx=20, pady=16,
                                highlightbackground=BORDER_COLOR,
                                highlightthickness=1)
        search_frame.pack(fill="x", padx=28, pady=(8, 16))

        tk.Label(
            search_frame, text="🔍  Nhập từ khóa tìm kiếm:",
            bg=CARD_BG, fg=TEXT_DARK,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 8))

        entry = tk.Entry(
            search_frame, font=("Segoe UI", 12),
            bd=1, relief="solid"
        )
        entry.pack(fill="x", pady=(0, 8))

        # ── Ví dụ: Kết quả ──
        results_frame = tk.Frame(container, bg=CARD_BG, padx=20, pady=16,
                                 highlightbackground=BORDER_COLOR,
                                 highlightthickness=1)
        results_frame.pack(fill="x", padx=28, pady=(0, 16))

        tk.Label(
            results_frame, text="Kết quả sẽ hiển thị ở đây...",
            bg=CARD_BG, fg=TEXT_GRAY,
            font=("Segoe UI", 11)
        ).pack(pady=20)


# ═══════════════════════════════════════════════════════════════
# BƯỚC 3: Đăng ký trang vào registry
# Key phải khớp với menu key trong sidebar.py:
#   "favorite", "search", "compare", "chatbot"
# ═══════════════════════════════════════════════════════════════

# BỎ COMMENT DÒNG DƯỚI ĐỂ KÍCH HOẠT (khi đã code xong):
# PAGE_REGISTRY["search"] = SearchPage
