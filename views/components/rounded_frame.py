"""RoundedFrame - the/card co 4 goc bo tron.

ttk khong ho tro border-radius nen phai tu ve nen bang tk.Canvas (idiom
chuan cho tkinter, khong phai "ve UI tay" tuy tien - xem ScrollableFrame
cung dung Canvas lam viewport). Dat noi dung vao thuoc tinh `.body`.
"""

import tkinter as tk

import ttkbootstrap as tb


class RoundedFrame(tk.Frame):
    """Card bo goc. `.body` la tk.Frame de dat widget con vao."""

    def __init__(
        self,
        master,
        radius: int = 16,
        bg_color: str | None = None,
        border_color: str | None = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self._radius = radius
        # mau nen ben trong card mac dinh lay theo "light" cua theme dang
        # dung (dong bo voi cac card bootstyle="light" khac trong app) -
        # public de noi dung ben trong (.body) dung chung mau, khong bi lech
        self.bg_color = bg_color or tb.Style().colors.light
        # vien mong quanh card (relief) - lay dung token "border" cua theme,
        # khong hard-code mau rieng de doi theme van dong bo
        self._border_color = border_color or tb.Style().colors.border
        # mau ben ngoai 4 goc (phan Canvas khong bi polygon che) phai trung
        # mau nen trang, khong thi 4 goc se lo hinh vuong mau nen cu
        outer_bg = tb.Style().colors.bg

        self._canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=outer_bg)
        self._canvas.pack(fill="both", expand=True)

        self.body = tk.Frame(self._canvas, bg=self.bg_color)
        self._window = self._canvas.create_window(0, 0, window=self.body, anchor="nw")

        self._canvas.bind("<Configure>", self._on_resize)

    def _on_resize(self, event: "tk.Event") -> None:
        width, height = event.width, event.height
        if width <= 1 or height <= 1:
            return
        self._canvas.itemconfig(self._window, width=width, height=height)
        self._canvas.delete("bg")
        # chua 1px cho vien khoi bi Canvas cat mat o 4 canh
        self._ve_hcn_bo_goc(1, 1, width - 2, height - 2, self._radius)
        self._canvas.tag_lower("bg")

    def _ve_hcn_bo_goc(self, x1, y1, x2, y2, r) -> None:
        r = max(0, min(r, (x2 - x1) // 2, (y2 - y1) // 2))
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        # co outline (vien mong) thay vi de trong nhu truoc - thieu vien la
        # ly do card truoc do nhin "phang", khong tach biet voi nen trang
        self._canvas.create_polygon(
            points, smooth=True, fill=self.bg_color,
            outline=self._border_color, width=1, tags="bg",
        )
