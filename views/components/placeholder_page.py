"""PlaceholderPage — trang tạm cho menu chưa có View thật (Search/Compare/
Chatbot ở tuần 1), sẽ được thay bằng View thật đúng contract ở Issue tương
ứng của từng người (xem PLAN.md).
"""

import ttkbootstrap as tb


class PlaceholderPage(tb.Frame):
    def __init__(self, master, controller, title="Trang", icon="📄"):
        super().__init__(master)
        self._controller = controller

        box = tb.Frame(self, bootstyle="light", padding=60)
        box.place(relx=0.5, rely=0.4, anchor="center")
        tb.Label(box, text=icon, font=("Segoe UI", 36)).pack()
        tb.Label(box, text=title, font=("Segoe UI", 16, "bold")).pack(pady=(12, 4))
        tb.Label(box, text="Tính năng đang được phát triển...", bootstyle="secondary").pack()

    def refresh(self, **kwargs):
        pass
