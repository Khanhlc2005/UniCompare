# -*- coding: utf-8 -*-
"""Trang Chatbot (ChatbotView) — Issue 3.7 & Modern Minimalist Soft UI Redesign.

Phong cách thiết kế Modern Minimalist & Soft UI:
- Tone màu chính: Nền xám nhạt (#F4F5F7), màu chính Xanh Rêu Trầm (#3B5E4D / #2D4A3E), chữ xám đậm (#2D3748).
- Nút bấm bo tròn viên thuốc (Pill-shaped buttons), bo góc mềm mại, spacing rộng rãi thoáng mắt.
- Typography: Font Roboto / Segoe UI hiện đại.
- 2 Frame chính: Frame 1 (Nhập thông tin cá nhân) & Frame 2 (Hỗ trợ và giải đáp thắc mắc).
"""

import threading
import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as tb

from services import recommend_service, wizard_service, university_service
from views.components.scrollable_frame import ScrollableFrame


# Bảng màu Modern Minimalist & Soft UI Palette
COLOR_PAGE_BG = "#F4F5F7"         # Nền trang xám nhạt mềm dịu
COLOR_CARD_BG = "#FFFFFF"         # Nền thẻ trắng tinh
COLOR_TEXT_MAIN = "#2D3748"       # Chữ xám đậm (không dùng đen tuyền)
COLOR_TEXT_MUTED = "#64748B"      # Chữ xám phụ nhẹ mắt
COLOR_ACCENT = "#03c6fc"          # Màu xanh dương nhạt chủ đạo
COLOR_ACCENT_HOVER = "#00a8d8"    # Màu xanh dương khi hover
COLOR_ACCENT_LIGHT = "#e6f9ff"    # Nền xanh dương cực nhạt cho AI label
COLOR_BOT_BUBBLE = "#EFF8FF"      # Nền bong bóng bot (xanh dương nhạt)
COLOR_BOT_TEXT = "#0A2540"        # Chữ bong bóng bot (navy đậm)
COLOR_USER_BUBBLE = "#03c6fc"     # Nền bong bóng user (xanh dương nhạt)
COLOR_USER_TEXT = "#FFFFFF"       # Chữ bong bóng user (Trắng tinh)
COLOR_PILL_BG = "#E6F9FF"         # Nền nút viên thuốc gợi ý
COLOR_PILL_HOVER = "#B3EDFB"      # Hover nút viên thuốc gợi ý
# Giữ alias tương thích
COLOR_MOSS_GREEN = COLOR_ACCENT
COLOR_MOSS_HOVER = COLOR_ACCENT_HOVER

# Bảng tỷ giá tham khảo để quy đổi học phí ngoại tệ sang VNĐ
TY_GIA_HIEN_THI = {
    "CNY": 3600,
    "JPY": 175,
    "KRW": 19,
    "GBP": 34500,
    "USD": 25400,
    "AUD": 16500,
    "EUR": 27500,
    "VND": 1,
}


def _format_budget(budget_per_year) -> str:
    """Hiển thị ngân sách học phí dễ đọc."""
    if budget_per_year is None or budget_per_year == 0:
        return "Chưa xác định"
    if budget_per_year == wizard_service.NGAN_SACH_KHONG_GIOI_HAN:
        return "Không giới hạn"
    if budget_per_year >= 10**9:
        return f"{budget_per_year / 10**9:.1f} Tỷ VNĐ/năm"
    if budget_per_year >= 10**6:
        return f"{budget_per_year / 10**6:.0f} Triệu VNĐ/năm"
    return f"{budget_per_year:,.0f} VNĐ/năm"


def _format_tuition_with_vnd(uni: dict) -> str:
    """Định dạng học phí trường kèm quy đổi ra VNĐ nếu là ngoại tệ."""
    tuition = uni.get("tuition_per_year")
    currency = (uni.get("currency") or "USD").upper()

    if tuition is None or tuition == 0:
        return "Chưa công bố"

    base_str = f"{tuition:,.0f} {currency}"
    if currency == "VND":
        if tuition >= 10**9:
            return f"{tuition / 10**9:.1f} Tỷ VNĐ/năm"
        return f"{tuition / 10**6:.0f} Triệu VNĐ/năm"

    rate = TY_GIA_HIEN_THI.get(currency)
    if rate:
        vnd_val = tuition * rate
        if vnd_val >= 10**9:
            vnd_str = f"~{vnd_val / 10**9:.1f} Tỷ VNĐ"
        else:
            vnd_str = f"~{vnd_val / 10**6:.0f} Tr VNĐ"
        return f"{base_str} ({vnd_str})"
    
    return base_str


class PillButton(tk.Canvas):
    """Nút bấm hình viên thuốc bo tròn thật sự vẽ bằng Canvas.
    
    Dùng kỹ thuật vẽ arc + rectangle để tạo rounded-corners thực sự,
    khác với ttk.Button chỉ làm phẳng viền mà không thể bo góc.
    """

    def __init__(self, master, text="", command=None,
                 bg=COLOR_MOSS_GREEN, fg="#FFFFFF",
                 hover_bg=COLOR_MOSS_HOVER,
                 font_family="Segoe UI", font_size=10, bold=True,
                 px=22, py=9, **kwargs):
        self._text = text
        self._command = command
        self._bg = bg
        self._fg = fg
        self._hover_bg = hover_bg
        self._font_spec = (font_family, font_size, "bold" if bold else "normal")
        self._px = px
        self._py = py

        # Đo kích thước chữ bằng tk.font.Font (không cần tạo widget tạm)
        import tkinter.font as tkfont
        f = tkfont.Font(family=font_family, size=font_size, weight="bold" if bold else "normal")
        tw = f.measure(text)
        th = f.metrics("linespace")

        self._pw = max(tw + px * 2, 60)   # pill width, tối thiểu 60px
        self._ph = max(th + py * 2, 28)   # pill height, tối thiểu 28px
        self._pr = self._ph // 2          # pill radius = nửa chiều cao → hình viên thuốc

        try:
            parent_bg = master.cget("background")
        except Exception:
            try:
                parent_bg = master.cget("bg")
            except Exception:
                parent_bg = COLOR_PAGE_BG

        super().__init__(
            master,
            width=self._pw, height=self._ph,
            bg=parent_bg,
            highlightthickness=0, bd=0, **kwargs
        )
        self._draw(self._bg)
        self.bind("<Enter>", lambda e: self._draw(self._hover_bg))
        self.bind("<Leave>", lambda e: self._draw(self._bg))
        self.bind("<Button-1>", lambda e: self._on_click())
        self.bind("<ButtonRelease-1>", lambda e: self._draw(self._hover_bg if self._is_hovered() else self._bg))
        self._hovering = False

    def _is_hovered(self):
        try:
            mx, my = self.winfo_pointerxy()
            x1 = self.winfo_rootx()
            y1 = self.winfo_rooty()
            x2 = x1 + self.winfo_width()
            y2 = y1 + self.winfo_height()
            return x1 <= mx <= x2 and y1 <= my <= y2
        except Exception:
            return False

    def _draw(self, fill_color: str):
        self.delete("all")
        w, h, r = self._pw, self._ph, self._pr
        # Vẽ hình viên thuốc: 2 nửa tròn 2 bên + hình chữ nhật giữa
        self.create_oval(0, 0, 2 * r, h, fill=fill_color, outline="")
        self.create_oval(w - 2 * r, 0, w, h, fill=fill_color, outline="")
        self.create_rectangle(r, 0, w - r, h, fill=fill_color, outline="")
        # Vẽ nhãn chữ căn giữa
        self.create_text(
            w // 2, h // 2,
            text=self._text, fill=self._fg,
            font=self._font_spec, anchor="center"
        )


    def _on_click(self):
        self._draw(self._hover_bg)
        if self._command:
            self._command()


class SmallPillButton(PillButton):
    """Nút viên thuốc nhỏ cho Quick Pills gợi ý nhanh."""

    def __init__(self, master, text="", command=None, **kwargs):
        super().__init__(
            master, text=text, command=command,
            bg=COLOR_PILL_BG, fg="#2D3748",
            hover_bg=COLOR_PILL_HOVER,
            font_size=9, bold=False,
            px=14, py=6, **kwargs
        )


class ChatbotPage(tb.Frame):
    """Trang Chatbot phong cách Modern Minimalist & Soft UI — Nền xám nhạt, nút Xanh rêu trầm viên thuốc."""

    def __init__(self, master, controller):
        super().__init__(master)
        self._controller = controller

        # Cấu hình font chữ Roboto / Segoe UI chuẩn typography
        self._font_family = "Roboto" if "Roboto" in tk.font.families() else "Segoe UI"
        self._font_title = (self._font_family, 14, "bold")
        self._font_subtitle = (self._font_family, 9)
        self._font_label = (self._font_family, 9, "bold")
        self._font_body = (self._font_family, 10)
        self._font_bold = (self._font_family, 10, "bold")

        # Cấu hình TTK Styles cho Soft UI (Labels / Bubbles)
        style = tb.Style()
        style.configure(
            "UserBubble.TLabel", background=COLOR_USER_BUBBLE, foreground=COLOR_USER_TEXT,
            font=(self._font_family, 10, "bold"), padding=(14, 10)
        )
        style.configure(
            "BotBubble.TLabel", background=COLOR_BOT_BUBBLE, foreground=COLOR_BOT_TEXT,
            font=(self._font_family, 10), padding=(14, 10)
        )

        self._profile = {}
        self._has_analyzed = False

        # Thiết lập nền tổng quan xám nhạt #F4F5F7
        self.config(style="TFrame")
        
        self._build_header()

        # Main Container rộng rãi
        self._main_container = tb.Frame(self, padding=(20, 12))
        self._main_container.pack(fill="both", expand=True)

        self._build_frame1_profile_input()
        self._build_frame2_ai_chat()

    def refresh(self, **kwargs):
        """AppShell gọi mỗi lần tkraise() — tự động nạp danh sách quốc gia & ngành học."""
        self._populate_dropdown_data()

    # ── 1. Header Minimalist Banner ──────────────────────────────────────

    def _build_header(self):
        banner = tb.Frame(self, padding=(24, 16))
        banner.pack(fill="x")
        tb.Label(
            banner, text="🤖 Trợ lý AI Tư vấn Du học UniCompare",
            foreground=COLOR_MOSS_GREEN, font=self._font_title,
        ).pack(anchor="w")
        tb.Label(
            banner, text="Nhập hồ sơ ở đây để hệ thống gợi ý & đưa ra nhận xét trường phù hợp.",
            foreground=COLOR_TEXT_MUTED, font=self._font_subtitle,
        ).pack(anchor="w", pady=(3, 0))

    # ── 2. FRAME 1 (PHÍA TRÊN): Nhập thông tin cá nhân (Soft UI Form) ──

    def _build_frame1_profile_input(self):
        self._frame1 = tb.Labelframe(
            self._main_container, text=" 📋 Nhập thông tin cá nhân ",
            padding=(20, 16), bootstyle="default"
        )
        self._frame1.pack(fill="x", side="top", pady=(0, 14))

        # Hàng 1: GPA + Ngoại ngữ + Ngân sách
        row1 = tb.Frame(self._frame1)
        row1.pack(fill="x", pady=(0, 10))

        # 1.1 Điểm học lực GPA
        f_gpa = tb.Frame(row1)
        f_gpa.pack(side="left", fill="x", expand=True, padx=(0, 12))
        tb.Label(f_gpa, text="Điểm học lực (GPA):", foreground=COLOR_TEXT_MAIN, font=self._font_label).pack(anchor="w", pady=(0, 5))
        
        gpa_sub = tb.Frame(f_gpa)
        gpa_sub.pack(fill="x")
        self._cbo_gpa_scale = tb.Combobox(gpa_sub, values=["Thang 10", "Thang 4"], state="readonly", width=10, font=self._font_body)
        self._cbo_gpa_scale.current(0)
        self._cbo_gpa_scale.pack(side="left", padx=(0, 6))

        self._ent_gpa = tb.Entry(gpa_sub, font=self._font_body)
        self._ent_gpa.insert(0, "8.0")
        self._ent_gpa.pack(side="left", fill="x", expand=True)

        # 1.2 Ngoại ngữ
        f_lang = tb.Frame(row1)
        f_lang.pack(side="left", fill="x", expand=True, padx=(0, 12))
        tb.Label(f_lang, text="Chứng chỉ ngoại ngữ:", foreground=COLOR_TEXT_MAIN, font=self._font_label).pack(anchor="w", pady=(0, 5))

        lang_sub = tb.Frame(f_lang)
        lang_sub.pack(fill="x")
        self._cbo_lang_type = tb.Combobox(lang_sub, values=["IELTS", "TOEFL"], state="readonly", width=8, font=self._font_body)
        self._cbo_lang_type.current(0)
        self._cbo_lang_type.pack(side="left", padx=(0, 6))

        self._ent_lang_score = tb.Entry(lang_sub, font=self._font_body)
        self._ent_lang_score.insert(0, "6.5")
        self._ent_lang_score.pack(side="left", fill="x", expand=True)

        # 1.3 Ngân sách
        f_budget = tb.Frame(row1)
        f_budget.pack(side="left", fill="x", expand=True)
        tb.Label(f_budget, text="Ngân sách dự kiến:", foreground=COLOR_TEXT_MAIN, font=self._font_label).pack(anchor="w", pady=(0, 5))

        budget_sub = tb.Frame(f_budget)
        budget_sub.pack(fill="x")
        self._ent_budget = tb.Entry(budget_sub, font=self._font_body)
        self._ent_budget.insert(0, "250 triệu")
        self._ent_budget.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tb.Label(budget_sub, text="VNĐ/năm", font=self._font_label, foreground=COLOR_TEXT_MUTED).pack(side="right")

        # Hàng 2: Ưu tiên Quốc gia + Lĩnh vực mong muốn + Nút Phân tích
        row2 = tb.Frame(self._frame1)
        row2.pack(fill="x", pady=(4, 0))

        # 2.1 Ưu tiên khu vực/quốc gia
        f_country = tb.Frame(row2)
        f_country.pack(side="left", fill="x", expand=True, padx=(0, 12))
        tb.Label(f_country, text="Ưu tiên khu vực / Quốc gia:", foreground=COLOR_TEXT_MAIN, font=self._font_label).pack(anchor="w", pady=(0, 5))
        self._cbo_country = tb.Combobox(f_country, font=self._font_body)
        self._cbo_country.pack(fill="x")

        # 2.2 Lĩnh vực mong muốn
        f_major = tb.Frame(row2)
        f_major.pack(side="left", fill="x", expand=True, padx=(0, 12))
        tb.Label(f_major, text="Lĩnh vực / Ngành học mong muốn:", foreground=COLOR_TEXT_MAIN, font=self._font_label).pack(anchor="w", pady=(0, 5))
        self._cbo_major = tb.Combobox(f_major, font=self._font_body)
        self._cbo_major.pack(fill="x")

        # Nút bấm Phân tích viên thuốc Xanh Rêu Trầm (Canvas-based thật sự)
        self._btn_analyze = PillButton(
            row2, text="🚀 Phân tích hồ sơ",
            command=self._on_analyze_profile,
            font_family=self._font_family, font_size=10,
        )
        self._btn_analyze.pack(side="right", anchor="e", pady=(18, 0))

        self._populate_dropdown_data()

    def _populate_dropdown_data(self):
        """Nạp sẵn dữ liệu Quốc gia & Ngành học từ Database vào Combobox."""
        try:
            all_unis = self._controller.repo.get_all() or []
        except Exception:
            all_unis = []

        countries = sorted({u.get("country") for u in all_unis if u.get("country")})
        c_values = ["Tất cả (Không bắt buộc)"] + countries
        self._cbo_country["values"] = c_values
        if not self._cbo_country.get():
            self._cbo_country.current(0)

        majors_set = set()
        for u in all_unis:
            for m in u.get("majors", []):
                if m:
                    majors_set.add(m)
        sorted_majors = sorted(majors_set)
        m_values = ["Tất cả ngành"] + sorted_majors
        self._cbo_major["values"] = m_values
        if not self._cbo_major.get():
            self._cbo_major.current(0)

    # ── 3. FRAME 2 (PHÍA DƯỚI): Hỗ trợ và giải đáp thắc mắc ─────────────

    def _build_frame2_ai_chat(self):
        self._frame2 = tb.Labelframe(
            self._main_container, text=" 💬 Hỗ trợ và giải đáp thắc mắc ",
            padding=(16, 12), bootstyle="default"
        )
        self._frame2.pack(fill="both", expand=True)

        # Khu vực tin nhắn hội thoại Chat (ScrollableFrame)
        self._scroll = ScrollableFrame(self._frame2)
        self._scroll.pack(fill="both", expand=True, pady=(0, 10))

        # Thanh nhập liệu câu hỏi phụ phía dưới
        self._chat_input_frame = tb.Frame(self._frame2)
        self._chat_input_frame.pack(fill="x", side="bottom", pady=(4, 0))

        # Quick Pills gợi ý nhanh viên thuốc
        self._pills_row = tb.Frame(self._chat_input_frame)
        self._pills_row.pack(fill="x", pady=(0, 6))
        tb.Label(
            self._pills_row, text="💡 Gợi ý câu hỏi:",
            foreground=COLOR_TEXT_MAIN, font=self._font_subtitle
        ).pack(side="left", padx=(0, 8))

        for q_str in ["Học phí trường nào hợp lý nhất?", "Trường nào có nhiều học bổng?", "Đâu là trường đào tạo CNTT tốt?"]:
            SmallPillButton(
                self._pills_row, text=q_str,
                command=lambda s=q_str: self._send_ai_chat_message(s)
            ).pack(side="left", padx=4)

        # Entry chat & Nút Gửi viên thuốc thật sự
        input_row = tb.Frame(self._chat_input_frame)
        input_row.pack(fill="x")

        self._ent_chat_var = tk.StringVar()
        self._ent_chat = tb.Entry(input_row, textvariable=self._ent_chat_var, font=self._font_body)
        self._ent_chat.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=4)
        self._ent_chat.bind("<Return>", lambda e: self._submit_chat_message())

        PillButton(input_row, text="Gửi ✈️", command=self._submit_chat_message, font_family=self._font_family).pack(side="right")

        # Tin nhắn chào mừng ban đầu
        self._add_bot_bubble(
            "Xin chào! Tôi là Trợ lý AI tư vấn UniCompare.\n"
            "Hãy điền điểm số và yêu cầu của bạn ở **Phần thông tin cá nhân (phía trên)** rồi nhấn **'Phân tích hồ sơ'** "
            "để tôi đề xuất danh sách trường đại học phù hợp nhất dành cho bạn!"
        )

    # ── 4. Xử lý Logic Phân Tích Hồ Sơ (L1 Rule Engine + Gemini AI) ──────

    def _on_analyze_profile(self):
        """Đọc & chuẩn hóa dữ liệu Form Frame 1 -> Gọi L1 Rule Engine -> Render Card Grid 3 Cột -> Gọi Gemini AI."""
        # 1. Parse & Chuẩn hóa GPA về thang 4.0
        raw_gpa = self._ent_gpa.get().strip()
        scale = self._cbo_gpa_scale.get().strip()

        ok, gpa_val, err_msg = wizard_service.parse_gpa(raw_gpa)
        if not ok:
            messagebox.showerror("Lỗi GPA", err_msg)
            return

        if scale == "Thang 10":
            try:
                gpa_float = float(raw_gpa.replace(",", "."))
                if gpa_float > 4.0:
                    gpa_val = round(gpa_float / 2.5, 2)
            except ValueError:
                pass

        # 2. Parse & Chuẩn hóa Ngoại ngữ
        lang_type = self._cbo_lang_type.get().strip()
        raw_lang = self._ent_lang_score.get().strip()

        ielts_val = None
        toefl_val = None

        if lang_type == "IELTS":
            ok, ielts_val, err_msg = wizard_service.parse_ielts(raw_lang)
            if not ok:
                messagebox.showerror("Lỗi IELTS", err_msg)
                return
        else:
            ok, toefl_val, err_msg = wizard_service.parse_toefl(raw_lang)
            if not ok:
                messagebox.showerror("Lỗi TOEFL", err_msg)
                return

        # 3. Parse Ngân sách
        raw_budget = self._ent_budget.get().strip()
        ok, budget_val, err_msg = wizard_service.parse_budget(raw_budget)
        if not ok:
            messagebox.showerror("Lỗi Ngân sách", err_msg)
            return

        # 4. Parse Ưu tiên Quốc gia & Ngành
        country_val = self._cbo_country.get().strip()
        pref_countries = []
        if country_val and not country_val.startswith("Tất cả"):
            pref_countries = [country_val]

        major_val = self._cbo_major.get().strip()
        pref_majors = []
        if major_val and not major_val.startswith("Tất cả"):
            pref_majors = [major_val]

        self._profile = {
            "gpa": gpa_val,
            "ielts": ielts_val,
            "toefl": toefl_val,
            "budget_per_year": budget_val,
            "preferred_countries": pref_countries,
            "preferred_majors": pref_majors,
        }
        self._has_analyzed = True

        for w in self._scroll.body.winfo_children():
            w.destroy()

        lang_str = f"IELTS {ielts_val}" if ielts_val is not None else (f"TOEFL {toefl_val}" if toefl_val is not None else "Chưa có chứng chỉ")
        c_str = f", Quốc gia: {country_val}" if pref_countries else ""
        m_str = f", Ngành: {major_val}" if pref_majors else ""

        user_msg = (
            f"Phân tích hồ sơ của tôi:\n"
            f"• GPA: {gpa_val}/4.0 ({scale})\n"
            f"• Ngoại ngữ: {lang_str}\n"
            f"• Ngân sách: {_format_budget(budget_val)}{c_str}{m_str}"
        )
        self._add_user_bubble(user_msg)

        all_unis = university_service.get_all(self._controller.repo)
        available_countries = sorted({u.get("country") for u in all_unis if u.get("country")})
        
        majors_set = set()
        for u in all_unis:
            for m in u.get("majors", []):
                if m:
                    majors_set.add(m)
        available_majors = sorted(majors_set)[:6]

        selected_countries = set()
        selected_majors = set()

        options_frame = tb.Frame(self._control_frame)
        options_frame.pack(fill="x", pady=(0, 8))

        # Chọn quốc gia
        tb.Label(options_frame, text="Quốc gia:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        c_row = tb.Frame(options_frame)
        c_row.pack(fill="x", pady=(2, 6))

        for country in available_countries:
            var = tk.BooleanVar(value=False)
            def _toggle_c(c=country, v=var):
                if v.get():
                    selected_countries.add(c)
                else:
                    selected_countries.discard(c)

            tb.Checkbutton(
                c_row, text=country, variable=var, command=_toggle_c,
                bootstyle="outline-toolbutton",
            ).pack(side="left", padx=4)

    def _run_l1_analysis_and_render(self):
        """Chạy thuật toán L1 Rule Engine, render thẻ dạng LƯỚI 3 CỘT mềm mại kèm quy đổi VNĐ."""
        try:
            all_unis = self._controller.repo.get_all() or []
        except Exception:
            all_unis = []

        if not all_unis:
            self._add_bot_bubble("⚠️ Không tìm thấy dữ liệu trường đại học nào trong cơ sở dữ liệu.")
            return

        def finish():
            c_list = list(selected_countries)
            m_list = list(selected_majors)
            self._wizard.set_preferences(c_list, m_list)
            
            user_txt = []
            if c_list:
                user_txt.append(f"Quốc gia: {', '.join(c_list)}")
            if m_list:
                user_txt.append(f"Ngành: {', '.join(m_list)}")
            
            self._add_user_bubble(" | ".join(user_txt) if user_txt else "Không yêu cầu ưu tiên cụ thể")
            self._show_results()

        btn_row = tb.Frame(self._control_frame)
        btn_row.pack(fill="x")

        tb.Button(
            btn_row, text="✨ Hoàn tất & Phân tích Gợi ý",
            style="BannerLink.TButton", command=finish,
        ).pack(side="right")

    # ── 4. Card Kết Quả Gợi Ý & AI Interactive Chat ─────────────────────

    def _show_results(self):
        self._clear_controls()
        self._update_progress_bar()

        all_unis = university_service.get_all(self._controller.repo)
        profile = self._wizard.get_profile()

        # Phân tích điểm phù hợp bằng L1 Rule Engine (tức thì, 0ms delay)
        results = recommend_service.score_all(profile, all_unis, top_n=5)
        top_score = results[0]["score"] if results else 0

        if top_score == 0:
            self._add_bot_bubble(
                "⚠️ Hồ sơ của bạn hiện tại chưa đạt điều kiện tối thiểu của các trường (0% phù hợp).\n"
                "💡 Lời khuyên: Hãy nâng cao GPA, thi lấy chứng chỉ tiếng Anh (IELTS/TOEFL) hoặc chuẩn bị thêm ngân sách."
            )
        else:
            self._add_bot_bubble(
                f"🎉 Phân tích L1 hoàn tất!\n"
                f"Dựa trên thuật toán chấm điểm 6 tiêu chí chuẩn, dưới đây là danh sách trường đại học phù hợp nhất dành cho bạn:"
            )

        cards_container = tb.Frame(self._scroll.body)
        cards_container.pack(fill="x", pady=10)

        for col in range(3):
            cards_container.columnconfigure(col, weight=1, uniform="uni_card_col")

        exp_frames = {}

        for idx, item in enumerate(results):
            row_idx = idx // 3
            col_idx = idx % 3

            uni_id = item["university_id"]
            score_val = item["score"]
            uni = university_service.get_by_id(self._controller.repo, uni_id) or {}

            name = uni.get("name", item.get("name", "N/A"))
            country = uni.get("country", "")
            city = uni.get("city", "")
            location = f"📍 {city}, {country}" if city else f"📍 {country}"
            ranking = uni.get("ranking")
            rank_str = f"#{ranking}" if isinstance(ranking, (int, float)) else ""

            # ── Card container: nền trắng, viền xanh nhạt, bo góc mềm ──
            card_outer = tk.Frame(
                cards_container,
                bg="#FFFFFF",
                highlightbackground="#b3edfb",
                highlightthickness=1,
                bd=0,
            )
            card_outer.grid(row=row_idx, column=col_idx, padx=10, pady=10, sticky="nsew")

            card = tk.Frame(card_outer, bg="#FFFFFF")
            card.pack(fill="both", expand=True, padx=14, pady=12)

            # ── Score badge + Ranking ──
            top_bar = tk.Frame(card, bg="#FFFFFF")
            top_bar.pack(fill="x", pady=(0, 4))

            if score_val >= 75:
                badge_bg, badge_fg = "#03c6fc", "#FFFFFF"
            elif score_val >= 40:
                badge_bg, badge_fg = "#e6f9ff", "#0891b2"
            else:
                badge_bg, badge_fg = "#f1f5f9", "#64748B"

            score_badge = tk.Frame(top_bar, bg=badge_bg, padx=8, pady=3)
            score_badge.pack(side="left")
            tk.Label(
                score_badge, text=f"🎯 {score_val}% Phù hợp",
                bg=badge_bg, fg=badge_fg,
                font=(self._font_family, 8, "bold"),
            ).pack()

            if rank_str:
                tk.Label(
                    top_bar, text=rank_str,
                    bg="#FFFFFF", fg=COLOR_TEXT_MUTED,
                    font=(self._font_family, 9, "bold"),
                ).pack(side="right")

            # ── Đường kẻ phân cách nhạt ──
            sep = tk.Frame(card, bg="#e6f9ff", height=1)
            sep.pack(fill="x", pady=(6, 0))

            # ── Tên trường ──
            name_lbl = tk.Label(
                card, text=f"#{idx + 1}. {name}",
                bg="#FFFFFF", fg=COLOR_ACCENT,
                font=(self._font_family, 10, "bold"),
                wraplength=230, justify="left",
                cursor="hand2",
            )
            name_lbl.pack(anchor="w", pady=(8, 2))

            # ── Vị trí địa lý ──
            tk.Label(
                card, text=location,
                bg="#FFFFFF", fg=COLOR_TEXT_MUTED,
                font=(self._font_family, 8),
            ).pack(anchor="w", pady=(0, 6))

            # ── Thống kê GPA / IELTS / Học phí ──
            tuition_text = _format_tuition_with_vnd(uni)
            ielts_val = university_service.lay_ielts(uni)
            gpa_val = university_service.lay_gpa(uni)
            ielts_req = ielts_val if ielts_val is not None else "N/A"
            gpa_req = gpa_val if gpa_val is not None else "N/A"

            stats_frame = tk.Frame(card, bg="#f8fcff", padx=8, pady=6)
            stats_frame.pack(fill="x", pady=(0, 8))
            tk.Label(
                stats_frame,
                text=f"GPA ≥ {gpa_req}   •   IELTS ≥ {ielts_req}",
                bg="#f8fcff", fg=COLOR_TEXT_MAIN,
                font=(self._font_family, 8, "bold"),
            ).pack(anchor="w")
            tk.Label(
                stats_frame,
                text=f"💰 {tuition_text}",
                bg="#f8fcff", fg=COLOR_TEXT_MUTED,
                font=(self._font_family, 8),
            ).pack(anchor="w", pady=(2, 0))

            # ── AI Explanation ──
            exp_frame = tk.Frame(card, bg=COLOR_ACCENT_LIGHT, padx=8, pady=6)
            exp_frame.pack(fill="x", anchor="w", pady=(0, 10))
            exp_lbl = tk.Label(
                exp_frame, text="💡 AI: Đang tải đánh giá...",
                bg=COLOR_ACCENT_LIGHT, fg="#0369a1",
                font=(self._font_family, 8, "italic"),
                wraplength=220, justify="left",
            )
            exp_lbl.pack(anchor="w")
            exp_frames[str(uni_id)] = (exp_frame, exp_lbl)

            # ── Nút xem chi tiết ──
            action_bar = tk.Frame(card, bg="#FFFFFF")
            action_bar.pack(fill="x", side="bottom", pady=(4, 0))

            btn_detail = PillButton(
                action_bar, text="🔍 Xem chi tiết trường",
                command=lambda uid=uni_id: self._controller.show_frame("detail", university_id=uid),
                bg=COLOR_ACCENT, hover_bg=COLOR_ACCENT_HOVER,
                font_family=self._font_family, font_size=9, px=14, py=7,
            )
            btn_detail.pack(fill="x")

            name_lbl.bind(
                "<Button-1>",
                lambda e, uid=uni_id: self._controller.show_frame("detail", university_id=uid),
            )

        def fetch_explanations():
            ai_results = recommend_service.get_explanation(self._profile, results)
            def update_ui():
                try:
                    if not self.winfo_exists():
                        return
                    if ai_results:
                        for item in ai_results:
                            uid = str(item.get("university_id"))
                            if uid in exp_frames:
                                _, lbl = exp_frames[uid]
                                explanation = item.get("explanation", "")
                                if explanation:
                                    clean_exp = explanation.replace("**", "")
                                    lbl.config(text=f"💡 AI: {clean_exp}")
                                else:
                                    exp_frames[uid][0].pack_forget()
                    else:
                        for frame, _ in exp_frames.values():
                            frame.pack_forget()
                except Exception:
                    pass

            try:
                if self.winfo_exists():
                    self.after(0, update_ui)
            except Exception:
                pass

        threading.Thread(target=fetch_explanations, daemon=True).start()
        self._scroll_to_bottom()

    # ── 5. Helper Chat Bubble & Direct Interactive AI Chat ───────────────

    def _create_markdown_widget(self, parent, text: str, bg: str, fg: str, font_size: int = 10, max_width: int = 55):
        """Tạo widget Text phong cách Soft Bubble hỗ trợ render in đậm Markdown (**text**)."""
        import math
        import re

        lines = text.split("\n")
        calc_height = 0
        for line in lines:
            if not line.strip():
                calc_height += 1
            else:
                calc_height += max(1, math.ceil(len(line) / (max_width - 5)))

        txt_widget = tk.Text(
            parent, bg=bg, fg=fg, font=(self._font_family, font_size),
            wrap="word", bd=0, highlightthickness=0, relief="flat",
            width=max_width, height=max(1, calc_height), padx=12, pady=10
        )
        txt_widget.tag_configure("bold", font=(self._font_family, font_size, "bold"))
        txt_widget.tag_configure("normal", font=(self._font_family, font_size))

        parts = re.split(r"(\*\*.*?\*\*)", text)
        for part in parts:
            if part.startswith("**") and part.endswith("**") and len(part) >= 4:
                txt_widget.insert("end", part[2:-2], "bold")
            else:
                txt_widget.insert("end", part, "normal")

        txt_widget.config(state="disabled")
        return txt_widget

    def _add_bot_bubble(self, text: str):
        """Bong bóng chat của Bot (Nền rêu kem nhạt #EAEFE9, chữ rêu đậm #1A2E24)."""
        row = tb.Frame(self._scroll.body)
        row.pack(fill="x", pady=6, anchor="w")

        tb.Label(row, text="🤖", font=(self._font_family, 13)).pack(side="left", anchor="n", padx=(0, 6))

        bubble = self._create_markdown_widget(
            row, text, bg=COLOR_BOT_BUBBLE, fg=COLOR_BOT_TEXT, font_size=10, max_width=55
        )
        bubble.pack(side="left", anchor="w")
        self._scroll_to_bottom()

    def _add_user_bubble(self, text: str):
        """Bong bóng chat của Người dùng (Nền Xanh Rêu Trầm #3B5E4D, chữ TRẮNG #FFFFFF)."""
        row = tb.Frame(self._scroll.body)
        row.pack(fill="x", pady=6, anchor="e")

        bubble = tb.Label(
            row, text=text, style="UserBubble.TLabel",
            wraplength=450, justify="right"
        )
        bubble.pack(side="right", anchor="e")
        tb.Label(row, text="👤", font=(self._font_family, 13)).pack(side="right", anchor="n", padx=(6, 0))

        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        self.update_idletasks()
        self._scroll.body.update_idletasks()

    def _submit_chat_message(self):
        txt = self._ent_chat_var.get().strip()
        if not txt:
            return
        self._ent_chat_var.set("")
        self._send_ai_chat_message(txt)

    def _send_ai_chat_message(self, user_question: str):
        """Gửi câu hỏi của người dùng tới Gemini AI qua background thread."""
        self._add_user_bubble(user_question)

        loading_row = tb.Frame(self._scroll.body)
        loading_row.pack(fill="x", pady=6, anchor="w")
        tb.Label(loading_row, text="🤖", font=(self._font_family, 13)).pack(side="left", anchor="n", padx=(0, 6))
        loading_lbl = tb.Label(
            loading_row, text="⏳ AI đang suy nghĩ...", style="BotBubble.TLabel",
            font=(self._font_family, 9, "italic")
        )
        loading_lbl.pack(side="left", anchor="w")
        self._scroll_to_bottom()

        profile = self._wizard.get_profile()
        all_unis = university_service.get_all(self._controller.repo)

        def worker():
            answer = recommend_service.chat_with_ai(user_question, profile, all_unis)
            def update_ui():
                try:
                    if not self.winfo_exists():
                        return
                    loading_row.destroy()
                    self._add_bot_bubble(answer)
                except Exception:
                    pass

            try:
                if self.winfo_exists():
                    self.after(0, update_ui)
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()
