"""Reusable rounded widgets dựa trên tk.Canvas.

Cung cấp các widget bo góc tùy chỉnh cho giao diện UniCompare:
- RoundedFrame: Frame có viền bo tròn
- RoundedButton: Nút bấm bo góc tùy chỉnh màu sắc
- CircleAvatar: Hình tròn chứa chữ viết tắt (avatar)
"""

import tkinter as tk


class RoundedFrame(tk.Canvas):
    """Frame bo góc dùng Canvas vẽ hình chữ nhật rounded."""

    def __init__(self, parent, width=200, height=100, radius=15,
                 bg_color="#FFFFFF", border_color=None, border_width=0,
                 **kwargs):
        # Lấy bg của parent làm highlight background
        parent_bg = kwargs.pop("highlightbackground", parent.cget("bg") if hasattr(parent, "cget") else "#F4F6F9")
        super().__init__(
            parent, width=width, height=height,
            bg=parent_bg, highlightthickness=0, bd=0, **kwargs
        )
        self._bg_color = bg_color
        self._radius = radius
        self._width = width
        self._height = height
        self._rect_id = None
        self._border_color = border_color
        self._border_width = border_width
        self._draw()

    def _draw(self):
        r = self._radius
        w = self._width
        h = self._height
        # Xóa cũ
        self.delete("rounded_rect")
        # Vẽ border nếu có
        if self._border_color and self._border_width > 0:
            self._draw_rounded_rect(0, 0, w, h, r, self._border_color, "border_rect")
            self._rect_id = self._draw_rounded_rect(
                self._border_width, self._border_width,
                w - self._border_width, h - self._border_width,
                r, self._bg_color, "rounded_rect"
            )
        else:
            self._rect_id = self._draw_rounded_rect(0, 0, w, h, r, self._bg_color, "rounded_rect")

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, fill, tag):
        """Vẽ hình chữ nhật bo góc bằng polygon mượt."""
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        return self.create_polygon(points, fill=fill, smooth=True,
                                   outline="", tags=tag)

    def update_bg(self, new_color):
        """Cập nhật màu nền."""
        self._bg_color = new_color
        self._draw()


class RoundedButton(tk.Canvas):
    """Nút bấm bo góc tùy chỉnh, hỗ trợ hover effect."""

    def __init__(self, parent, text="Button", width=140, height=38,
                 radius=10, bg_color="#4CAF50", fg_color="#FFFFFF",
                 hover_color=None, font=("Segoe UI", 10, "bold"),
                 command=None, **kwargs):
        parent_bg = parent.cget("bg") if hasattr(parent, "cget") else "#F4F6F9"
        super().__init__(
            parent, width=width, height=height,
            bg=parent_bg, highlightthickness=0, bd=0,
            cursor="hand2", **kwargs
        )
        self._text = text
        self._bg_color = bg_color
        self._fg_color = fg_color
        self._hover_color = hover_color or self._darken(bg_color, 20)
        self._radius = radius
        self._font = font
        self._command = command
        self._w = width
        self._h = height

        self._draw(self._bg_color)

        # Bind events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _draw(self, fill_color):
        self.delete("all")
        r = self._radius
        w = self._w
        h = self._h
        points = [
            r, 0, w - r, 0, w, 0, w, r,
            w, h - r, w, h, w - r, h,
            r, h, 0, h, 0, h - r,
            0, r, 0, 0,
        ]
        self.create_polygon(points, fill=fill_color, smooth=True, outline="")
        self.create_text(w // 2, h // 2, text=self._text,
                         fill=self._fg_color, font=self._font)

    def _on_enter(self, _event):
        self._draw(self._hover_color)

    def _on_leave(self, _event):
        self._draw(self._bg_color)

    def _on_click(self, _event):
        if self._command:
            self._command()

    @staticmethod
    def _darken(hex_color, amount=20):
        """Tạo màu tối hơn cho hover effect."""
        hex_color = hex_color.lstrip("#")
        r = max(0, int(hex_color[0:2], 16) - amount)
        g = max(0, int(hex_color[2:4], 16) - amount)
        b = max(0, int(hex_color[4:6], 16) - amount)
        return f"#{r:02x}{g:02x}{b:02x}"


class CircleAvatar(tk.Canvas):
    """Hình tròn chứa chữ viết tắt (avatar)."""

    def __init__(self, parent, text="NA", size=40,
                 bg_color="#4CAF50", fg_color="#FFFFFF",
                 font=("Segoe UI", 12, "bold"), **kwargs):
        parent_bg = parent.cget("bg") if hasattr(parent, "cget") else "#1E2A78"
        super().__init__(
            parent, width=size, height=size,
            bg=parent_bg, highlightthickness=0, bd=0, **kwargs
        )
        self.create_oval(2, 2, size - 2, size - 2, fill=bg_color, outline="")
        self.create_text(size // 2, size // 2, text=text,
                         fill=fg_color, font=font)
