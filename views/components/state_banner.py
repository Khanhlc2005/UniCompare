# -*- coding: utf-8 -*-
"""StateBanner — Issue #54 (Polish UI: bootstyle, spacing, edge case).

1. `StateBanner(parent, message, icon=...)` — danh sách rỗng (đã có sẵn dữ
   liệu, chỉ là không có kết quả / chưa lưu gì).
2. `StateBanner.mongo_error(parent, exc)` — mất kết nối MongoDB giữa lúc
   đang dùng app (config.py mục 7: thông báo rõ ràng, không traceback thô
   ra cho người dùng). Dùng icon/màu khác empty-state thường để phân biệt
   "chưa có dữ liệu" với "không tải được dữ liệu".
"""

import ttkbootstrap as tb


class StateBanner(tb.Frame):
    """Card 'light' căn giữa: icon lớn + thông điệp hướng dẫn."""

    def __init__(self, parent, message, icon="ℹ️", **kwargs):
        kwargs.setdefault("bootstyle", "light")
        kwargs.setdefault("padding", 40)
        super().__init__(parent, **kwargs)
        colors = tb.Style().colors
        tb.Label(self, text=icon, font=("Segoe UI", 32)).pack()
        tb.Label(
            self, text=message, foreground=colors.secondary, justify="center"
        ).pack(pady=(10, 0))

    @classmethod
    def mongo_error(cls, parent, exc=None, **kwargs):
        """Banner chuẩn khi mất kết nối MongoDB GIỮA LÚC đang dùng app (khác
        với lúc mở app — lúc đó app_shell.py đã tự fallback sang FakeRepo).
        Không hiện traceback, chỉ hiện lý do + hướng xử lý (config.py mục 7)."""
        message = (
            "Mất kết nối MongoDB, không tải được dữ liệu lúc này.\n"
            "Kiểm tra mạng / MONGO_URI rồi thử lại (chuyển sang màn khác "
            "rồi quay lại để tải lại)."
        )
        if exc is not None and str(exc):
            message += f"\n\nChi tiết: {exc}"
        return cls(parent, message, icon="⚠️", **kwargs)
