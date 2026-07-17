"""PillFilter — hàng pill để lọc (VD lọc theo quốc gia), dùng chung nhiều
trang. Đúng ARCHITECTURE.md mục 5.3: ttk.Radiobutton với
bootstyle="toolbutton" (segmented control, chỉ chọn 1 giá trị tại 1 lúc).
"""

import tkinter as tk

import ttkbootstrap as tb


class PillFilter(tb.Frame):
    """Hàng pill chọn 1 giá trị (hoặc "Tất cả"), click để đổi filter."""

    def __init__(self, parent, options, on_select=None, active=None,
                 all_label="Tất cả", **kwargs):
        super().__init__(parent, **kwargs)
        self._on_select = on_select
        # StringVar khong chua duoc None -> dung "" lam gia tri "Tat ca"
        self._var = tk.StringVar(value=active or "")

        values = [("", all_label)] + [(v, v) for v in options]
        for value, text in values:
            btn = tb.Radiobutton(
                self, text=text, value=value, variable=self._var,
                bootstyle="toolbutton", command=self._on_change
            )
            btn.pack(side="left", padx=(0, 6))

    def _on_change(self):
        value = self._var.get() or None
        if self._on_select:
            self._on_select(value)
