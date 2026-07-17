"""ScrollableFrame — frame ttk có sẵn thanh cuộn dọc, dùng chung cho các
trang nội dung dài (Home, Detail, Watchlist...). Đây là widget dùng chung
đơn giản (ARCHITECTURE.md mục 5.3), KHÔNG phải base class/interface cho
View — mỗi View vẫn kế thừa thẳng ttk.Frame theo đúng Frame contract mục 5.1.

tk.Canvas vẫn cần dùng làm viewport cuộn vì ttk không có widget cuộn dựng
sẵn — đây là idiom chuẩn, không phải vẽ UI tay bằng Canvas.
"""

import tkinter as tk

import ttkbootstrap as tb


class ScrollableFrame(tb.Frame):
    """Đặt nội dung vào thuộc tính `.body`, tự cuộn khi nội dung dài hơn khung."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # doc mau nen trang tu Style dung chung (khai bao 1 cho duy nhat o
        # app_shell.py) - tk.Canvas khong theo ttk style nen phai set tay
        bg = tb.Style().colors.bg
        self._canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=bg)
        scrollbar = tb.Scrollbar(self, orient="vertical",
                                  command=self._canvas.yview, bootstyle="round")
        self.body = tb.Frame(self._canvas)

        self.body.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        )
        self._window = self._canvas.create_window((0, 0), window=self.body, anchor="nw")
        self._canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(self._window, width=e.width))

        # chi bat scroll chuot khi con tro dang o tren canvas nay - AppShell
        # tao san moi trang 1 lan (khong destroy/recreate), neu bind_all luon
        # thi trang tao sau se "cuop" scroll cua moi trang khac
        self._canvas.bind("<Enter>", self._bind_mousewheel)
        self._canvas.bind("<Leave>", self._unbind_mousewheel)

    def _bind_mousewheel(self, _event=None):
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind_all("<Button-4>", self._on_mousewheel_up)
        self._canvas.bind_all("<Button-5>", self._on_mousewheel_down)

    def _unbind_mousewheel(self, _event=None):
        self._canvas.unbind_all("<MouseWheel>")
        self._canvas.unbind_all("<Button-4>")
        self._canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _on_mousewheel_up(self, _event):
        self._canvas.yview_scroll(-1, "units")

    def _on_mousewheel_down(self, _event):
        self._canvas.yview_scroll(1, "units")

    def scroll_to(self, fraction):
        """Nhay toi vi tri fraction (0.0 = dau, 1.0 = cuoi) - dung cho muc luc."""
        self._canvas.yview_moveto(fraction)
