# -*- coding: utf-8 -*-
"""Trang Chatbot (ChatbotView) — Issue 3.7 (Wireframe 7).

Nâng cấp ChatbotView theo phong cách Messenger:
- Chat bubble người gửi: Nền xanh blue Messenger (#0084FF), chữ TRẮNG tinh nổi bật (#FFFFFF).
- Chat bubble Bot: Nền xanh nhạt Messenger (#E7F3FF), chữ xanh đen dễ đọc (#0F172A).
- Thanh tiến trình 4 bước bo tròn mượt mà.
- Quick pills gợi ý câu trả lời nhanh dạng chip bong bóng.
- Card kết quả Top N trường kèm % phù hợp chuẩn Rule Engine L1.
- Cảnh báo Option A khi hồ sơ quá yếu (0% phù hợp).
"""

import threading
import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as tb

from services import recommend_service, wizard_service
from views.components.scrollable_frame import ScrollableFrame


def _format_budget(budget_per_year) -> str:
    """Hien thi ngan sach cho de doc - rieng gia tri sentinel 'khong gioi han' thi ghi chu vay luon."""
    if budget_per_year == wizard_service.NGAN_SACH_KHONG_GIOI_HAN:
        return "Không giới hạn"
    return f"{budget_per_year:,.0f} VNĐ/năm"

WIZARD_STEPS = [
    ("1", "Học lực", "GPA"),
    ("2", "Chứng chỉ", "IELTS"),
    ("3", "Ngân sách", "Học phí/năm"),
    ("4", "Ưu tiên", "Quốc gia & Ngành"),
]

# Bảng màu Messenger Style
COLOR_MESSENGER_BLUE = "#0084FF"   # Nền bong bóng tin nhắn người gửi
COLOR_BOT_BUBBLE_BG = "#E7F3FF"    # Nền xanh nhạt bong bóng tin nhắn bot
COLOR_BOT_TEXT = "#0F172A"         # Chữ xanh đen đậm cho bot
COLOR_WHITE = "#FFFFFF"            # Chữ trắng tinh cho tin nhắn người gửi
COLOR_PROGRESS_BG = "#F0F4F9"       # Nền thanh tiến trình
COLOR_SUCCESS_GREEN = "#10B981"     # Màu hoàn thành step / badge phù hợp cao


class ChatbotPage(tb.Frame):
    """Trang Chatbot tư vấn du học phong cách Messenger — Wizard 4 bước + L1 Rule Engine."""

    def __init__(self, master, controller):
        super().__init__(master)
        self._controller = controller
        self._colors = tb.Style().colors

        # Khai báo sẵn TTK style cho Messenger Bubbles
        style = tb.Style()
        style.configure("UserBubble.TLabel", background=COLOR_MESSENGER_BLUE, foreground=COLOR_WHITE, font=("Segoe UI", 10, "bold"), padding=(14, 10))
        style.configure("BotBubble.TLabel", background=COLOR_BOT_BUBBLE_BG, foreground=COLOR_BOT_TEXT, font=("Segoe UI", 10), padding=(14, 10))
        style.configure("QuickPill.TButton", foreground=COLOR_MESSENGER_BLUE, background=COLOR_BOT_BUBBLE_BG, borderwidth=0, focuscolor=COLOR_BOT_BUBBLE_BG)
        style.map("QuickPill.TButton", foreground=[("active", COLOR_MESSENGER_BLUE)], background=[("active", "#D0E7FF")])

        self._wizard = wizard_service.WizardState()

        self._build_header()
        self._build_progress_bar()

        # Scrollable area cho hội thoại chat
        self._scroll = ScrollableFrame(self)
        self._scroll.pack(fill="both", expand=True, padx=24, pady=(0, 10))

        # Khung chứa các ô nhập liệu bên dưới
        self._control_frame = tb.Frame(self, padding=(24, 12))
        self._control_frame.pack(fill="x", side="bottom")

        # Bắt đầu wizard lần đầu
        self._start_wizard()

    def refresh(self, **kwargs):
        """AppShell gọi mỗi lần tkraise() — giữ nguyên cuộc trò chuyện hoặc bắt đầu nếu rỗng."""
        pass

    # ── 1. Header & Progress Bar ──────────────────────────────────────────

    def _build_header(self):
        banner = tb.Frame(self, bootstyle="primary", padding=(24, 16))
        banner.pack(fill="x")
        tb.Label(
            banner, text="🤖 Trợ lý Tư vấn Du học UniCompare", bootstyle="inverse-primary",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")
        tb.Label(
            banner, text="Trả lời 4 câu hỏi ngắn theo dạng trò chuyện để nhận gợi ý trường đại học phù hợp.",
            bootstyle="inverse-primary", font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 0))

    def _build_progress_bar(self):
        self._progress_frame = tk.Frame(self, bg=COLOR_PROGRESS_BG, padx=16, pady=10)
        self._progress_frame.pack(fill="x", padx=24, pady=(12, 12))
        self._update_progress_bar()

    def _update_progress_bar(self):
        for w in self._progress_frame.winfo_children():
            w.destroy()

        current = self._wizard.step

        for i, (num, name, desc) in enumerate(WIZARD_STEPS, 1):
            self._progress_frame.columnconfigure(i - 1, weight=1)

            step_box = tk.Frame(self._progress_frame, bg=COLOR_PROGRESS_BG)
            step_box.grid(row=0, column=i - 1, sticky="ew")

            if i < current:
                icon_txt = " ✓ "
                badge_bg = COLOR_SUCCESS_GREEN
                badge_fg = COLOR_WHITE
                txt_color = COLOR_SUCCESS_GREEN
            elif i == current:
                icon_txt = f" {num} "
                badge_bg = COLOR_MESSENGER_BLUE
                badge_fg = COLOR_WHITE
                txt_color = self._colors.primary
            else:
                icon_txt = f" {num} "
                badge_bg = "#CBD5E1"
                badge_fg = "#475569"
                txt_color = self._colors.secondary

            tk.Label(
                step_box, text=icon_txt, bg=badge_bg, fg=badge_fg,
                font=("Segoe UI", 9, "bold"), padx=4, pady=2
            ).pack(side="left", padx=(0, 6))

            lbl_txt = f"Bước {num}: {name}" if i == current else name
            tk.Label(
                step_box, text=lbl_txt, bg=COLOR_PROGRESS_BG, fg=txt_color,
                font=("Segoe UI", 9, "bold" if i == current else "normal")
            ).pack(side="left")

    # ── 2. Chat Conversation Helpers (Messenger Style & Markdown) ────────

    def _create_markdown_widget(self, parent, text: str, bg: str, fg: str, font_size: int = 10, max_width: int = 55):
        """Tạo widget Text phong cách Messenger Bubble hỗ trợ render in đậm Markdown (**text**)."""
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
            parent, bg=bg, fg=fg, font=("Segoe UI", font_size),
            wrap="word", bd=0, highlightthickness=0, relief="flat",
            width=max_width, height=max(1, calc_height), padx=12, pady=10
        )
        txt_widget.tag_configure("bold", font=("Segoe UI", font_size, "bold"))
        txt_widget.tag_configure("normal", font=("Segoe UI", font_size))

        parts = re.split(r"(\*\*.*?\*\*)", text)
        for part in parts:
            if part.startswith("**") and part.endswith("**") and len(part) >= 4:
                txt_widget.insert("end", part[2:-2], "bold")
            else:
                txt_widget.insert("end", part, "normal")

        txt_widget.config(state="disabled")
        return txt_widget

    def _add_bot_bubble(self, text: str):
        """Thêm tin nhắn dạng Messenger Bubble của Bot (Nền xanh nhạt #E7F3FF, chữ xanh đen #0F172A)."""
        row = tb.Frame(self._scroll.body)
        row.pack(fill="x", pady=6, anchor="w")

        tb.Label(row, text="🤖", font=("Segoe UI", 14)).pack(side="left", anchor="n", padx=(0, 8))

        bubble = self._create_markdown_widget(
            row, text, bg=COLOR_BOT_BUBBLE_BG, fg=COLOR_BOT_TEXT, font_size=10, max_width=55
        )
        bubble.pack(side="left", anchor="w")

        self._scroll_to_bottom()

    def _add_user_bubble(self, text: str):
        """Thêm tin nhắn dạng Messenger Bubble của Người dùng (Nền xanh blue #0084FF, chữ TRẮNG #FFFFFF)."""
        row = tb.Frame(self._scroll.body)
        row.pack(fill="x", pady=6, anchor="e")

        bubble = tb.Label(
            row, text=text, style="UserBubble.TLabel",
            wraplength=450, justify="right"
        )
        bubble.pack(side="right", anchor="e")

        tb.Label(row, text="👤", font=("Segoe UI", 14)).pack(side="right", anchor="n", padx=(8, 0))

        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        self.update_idletasks()
        self._scroll.body.update_idletasks()

    # ── 3. Wizard Flow Controls ──────────────────────────────────────────

    def _start_wizard(self):
        """Khởi động lại hội thoại từ bước 1."""
        self._wizard.reset()
        for w in self._scroll.body.winfo_children():
            w.destroy()

        self._update_progress_bar()

        self._add_bot_bubble(
            "Xin chào! Tôi là Trợ lý AI tư vấn chọn trường đại học.\n"
            "Hãy chia sẻ một chút về hồ sơ của bạn để tôi phân tích nhé!"
        )
        self._prompt_step_1()

    def _clear_controls(self):
        for w in self._control_frame.winfo_children():
            w.destroy()

    # ── Bước 1: Học lực (GPA) ─────────────────────────────────────────────

    def _prompt_step_1(self):
        self._clear_controls()
        self._update_progress_bar()

        self._add_bot_bubble(
            "📌 Bước 1/4 (Học lực):\n"
            "Bạn vui lòng cho biết điểm GPA trung bình học tập của mình (thang 10 hoặc thang 4.0):"
        )

        input_row = tb.Frame(self._control_frame)
        input_row.pack(fill="x", pady=(0, 6))

        entry_var = tk.StringVar()
        entry = tb.Entry(input_row, textvariable=entry_var, font=("Segoe UI", 10))
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=3)
        entry.focus()

        def submit():
            val = entry_var.get().strip()
            ok, msg = self._wizard.set_gpa(val)
            if not ok:
                messagebox.showerror("Thông tin không hợp lệ", msg)
                return
            self._add_user_bubble(f"GPA: {val}")
            self._prompt_step_2()

        entry.bind("<Return>", lambda e: submit())
        tb.Button(input_row, text="Gửi →", style="BannerLink.TButton", command=submit).pack(side="right")

        # Quick Pills (Gợi ý nhanh dạng bong bóng Messenger)
        pills_row = tb.Frame(self._control_frame)
        pills_row.pack(fill="x")
        tb.Label(pills_row, text="Gợi ý nhanh:", foreground=self._colors.secondary, font=("Segoe UI", 8, "bold")).pack(side="left", padx=(0, 6))

        for gpa_str in ["3.0/4.0", "3.4/4.0", "3.6/4.0", "8.0/10", "8.5/10"]:
            tb.Button(
                pills_row, text=gpa_str, style="QuickPill.TButton",
                command=lambda s=gpa_str.split("/")[0]: [entry_var.set(s), submit()],
            ).pack(side="left", padx=4)

    # ── Bước 2: Chứng chỉ (IELTS) ──────────────────────────────────────────

    def _prompt_step_2(self):
        self._clear_controls()
        self._update_progress_bar()

        self._add_bot_bubble(
            "📌 Bước 2/4 (Chứng chỉ tiếng Anh):\n"
            "Điểm IELTS hiện tại của bạn là bao nhiêu? (Nhập 0 nếu chưa thi hoặc chưa có):"
        )

        input_row = tb.Frame(self._control_frame)
        input_row.pack(fill="x", pady=(0, 6))

        entry_var = tk.StringVar()
        entry = tb.Entry(input_row, textvariable=entry_var, font=("Segoe UI", 10))
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=3)
        entry.focus()

        def submit():
            val = entry_var.get().strip()
            ok, msg = self._wizard.set_english(val)
            if not ok:
                messagebox.showerror("Thông tin không hợp lệ", msg)
                return
            self._add_user_bubble(f"IELTS: {val if val else 'Chưa có'}")
            self._prompt_step_3()

        entry.bind("<Return>", lambda e: submit())
        tb.Button(input_row, text="Gửi →", style="BannerLink.TButton", command=submit).pack(side="right")

        # Quick Pills
        pills_row = tb.Frame(self._control_frame)
        pills_row.pack(fill="x")
        tb.Label(pills_row, text="Gợi ý nhanh:", foreground=self._colors.secondary, font=("Segoe UI", 8, "bold")).pack(side="left", padx=(0, 6))

        for ielts_str in ["Chưa có (0)", "6.0", "6.5", "7.0", "7.5", "8.0"]:
            s_val = "0" if "Chưa" in ielts_str else ielts_str
            tb.Button(
                pills_row, text=ielts_str, style="QuickPill.TButton",
                command=lambda s=s_val: [entry_var.set(s), submit()],
            ).pack(side="left", padx=4)

    # ── Bước 3: Ngân sách (Budget) ─────────────────────────────────────────

    def _prompt_step_3(self):
        self._clear_controls()
        self._update_progress_bar()

        self._add_bot_bubble(
            "📌 Bước 3/4 (Ngân sách học phí):\n"
            "Ngân sách dự kiến của gia đình dành cho học phí khoảng bao nhiêu VNĐ/năm?"
        )

        input_row = tb.Frame(self._control_frame)
        input_row.pack(fill="x", pady=(0, 6))

        entry_var = tk.StringVar()
        entry = tb.Entry(input_row, textvariable=entry_var, font=("Segoe UI", 10))
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=3)
        entry.focus()

        def submit():
            val = entry_var.get().strip()
            ok, msg = self._wizard.set_budget(val)
            if not ok:
                messagebox.showerror("Thông tin không hợp lệ", msg)
                return
            self._add_user_bubble(f"Ngân sách: {val if val else 'Không giới hạn'}")
            self._prompt_step_4()

        entry.bind("<Return>", lambda e: submit())
        tb.Button(input_row, text="Gửi →", style="BannerLink.TButton", command=submit).pack(side="right")

        # Quick Pills
        pills_row = tb.Frame(self._control_frame)
        pills_row.pack(fill="x")
        tb.Label(pills_row, text="Gợi ý nhanh:", foreground=self._colors.secondary, font=("Segoe UI", 8, "bold")).pack(side="left", padx=(0, 6))

        for b_str in ["150 triệu", "250 triệu", "400 triệu", "Không giới hạn"]:
            # truyen thang text hien thi vao wizard - parse_budget() tu nhan
            # dien "khong gioi han" (khac voi "0"/de trong la thieu du lieu)
            tb.Button(
                pills_row, text=b_str, style="QuickPill.TButton",
                command=lambda s=b_str: [entry_var.set(s), submit()],
            ).pack(side="left", padx=4)

    # ── Bước 4: Ưu tiên (Quốc gia & Ngành) ────────────────────────────────

    def _prompt_step_4(self):
        self._clear_controls()
        self._update_progress_bar()

        self._add_bot_bubble(
            "📌 Bước 4/4 (Ưu tiên du học):\n"
            "Bạn có ưu tiên đặc biệt về quốc gia hoặc ngành học nào không?"
        )

        all_unis = self._controller.repo.get_all()
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

        # Chọn ngành học
        tb.Label(options_frame, text="Ngành học:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        m_row = tb.Frame(options_frame)
        m_row.pack(fill="x", pady=(2, 8))

        for major in available_majors:
            var = tk.BooleanVar(value=False)
            def _toggle_m(m=major, v=var):
                if v.get():
                    selected_majors.add(m)
                else:
                    selected_majors.discard(m)

            tb.Checkbutton(
                m_row, text=major, variable=var, command=_toggle_m,
                bootstyle="outline-toolbutton",
            ).pack(side="left", padx=4)

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

        all_unis = self._controller.repo.get_all()
        profile = self._wizard.get_profile()

        # Phân tích điểm phù hợp bằng L1 Rule Engine (tức thì, 0ms delay)
        results = recommend_service.score_all(profile, all_unis, top_n=5)
        top_score = results[0]["score"] if results else 0

        # Option A: Cảnh báo khi hồ sơ quá yếu (0% hoặc điểm phù hợp rất thấp)
        if top_score == 0:
            self._add_bot_bubble(
                "⚠️ Hồ sơ của bạn hiện tại chưa đáp ứng điều kiện đầu vào tối thiểu của các trường (0% phù hợp).\n\n"
                "💡 Lời khuyên: Bạn nên cân nhắc cải thiện điểm GPA học tập, thi chứng chỉ tiếng Anh (IELTS/TOEFL) "
                "hoặc chuẩn bị thêm ngân sách học phí để tăng cơ hội du học thành công!\n\n"
                "Dưới đây là thông tin yêu cầu của một số trường đại học tiêu biểu để bạn tham khảo chỉ tiêu:"
            )
        elif top_score < 40:
            self._add_bot_bubble(
                f"⚠️ Hồ sơ của bạn có mức độ phù hợp tương đối thấp (cao nhất đạt {top_score}%).\n"
                f"Dựa trên GPA ({profile['gpa']}), IELTS ({profile['ielts']}), "
                f"Ngân sách ({_format_budget(profile['budget_per_year'])}), "
                f"dưới đây là danh sách các trường có yêu cầu gần nhất với hồ sơ của bạn:"
            )
        else:
            self._add_bot_bubble(
                f"🎉 Phân tích hoàn tất!\n"
                f"Dựa trên GPA ({profile['gpa']}), IELTS ({profile['ielts']}), "
                f"Ngân sách ({_format_budget(profile['budget_per_year'])}), "
                f"dưới đây là Top 5 trường đại học phù hợp nhất dành cho bạn:"
            )

        # Frame chứa danh sách card kết quả
        cards_container = tb.Frame(self._scroll.body)
        cards_container.pack(fill="x", pady=10)

        exp_frames = {}

        for rank_idx, item in enumerate(results, 1):
            uni_id = item["university_id"]
            score_val = item["score"]
            uni = self._controller.repo.get_by_id(uni_id) or {}

            name = uni.get("name", item.get("name", "N/A"))
            country = uni.get("country", "")
            city = uni.get("city", "")
            location = f"📍 {city}, {country}" if city else f"📍 {country}"
            ranking = uni.get("ranking")
            rank_str = f"#{ranking}" if isinstance(ranking, (int, float)) else ""

            card = tb.Frame(cards_container, bootstyle="light", padding=16)
            card.pack(fill="x", pady=6)

            # Top bar: Match % badge + Rank
            top_bar = tb.Frame(card, bootstyle="light")
            top_bar.pack(fill="x")

            if score_val == 0:
                badge_style = "danger"
            elif score_val >= 75:
                badge_style = "success"
            elif score_val >= 40:
                badge_style = "primary"
            else:
                badge_style = "secondary"

            tb.Label(
                top_bar, text=f"🎯 {score_val}% Phù hợp",
                bootstyle=f"{badge_style}-inverse", font=("Segoe UI", 9, "bold"),
                padding=(8, 4),
            ).pack(side="left")

            if rank_str:
                tb.Label(
                    top_bar, text=f"Xếp hạng thế giới: {rank_str}",
                    foreground=self._colors.secondary, font=("Segoe UI", 9),
                ).pack(side="right")

            # Tên trường
            name_lbl = tb.Label(
                card, text=f"#{rank_idx}. {name}", foreground=self._colors.primary,
                font=("Segoe UI", 12, "bold"), wraplength=500, justify="left",
                cursor="hand2",
            )
            name_lbl.pack(anchor="w", pady=(8, 4))

            tb.Label(card, text=location, foreground=self._colors.secondary).pack(anchor="w", pady=(0, 6))

            # Thông số chính
            tuition = uni.get("tuition_per_year")
            currency = uni.get("currency", "USD")
            t_str = f"{tuition:,.0f} {currency}" if tuition else "N/A"
            ielts_req = uni.get("ielts_min", "N/A")
            gpa_req = uni.get("gpa_min", "N/A")

            stats_txt = f"GPA min: {gpa_req}  •  IELTS min: {ielts_req}  •  Học phí: {t_str}/năm"
            tb.Label(card, text=stats_txt, foreground=self._colors.secondary, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 8))

            # Container cho AI Explanation (sẽ được điền dữ liệu asynchronously)
            exp_frame = tk.Frame(card, bg="#F0F7FF", padx=10, pady=8)
            exp_frame.pack(fill="x", anchor="w", pady=(0, 10))
            exp_lbl = tk.Label(
                exp_frame, text="💡 AI Nhận xét: Đang tải phân tích chi tiết từ Gemini...", bg="#F0F7FF", fg="#1E3A8A",
                font=("Segoe UI", 9, "italic"), wraplength=500, justify="left",
            )
            exp_lbl.pack(anchor="w")
            exp_frames[str(uni_id)] = (exp_frame, exp_lbl)

            # Nút Xem chi tiết
            action_bar = tb.Frame(card, bootstyle="light")
            action_bar.pack(fill="x")

            btn_detail = tb.Button(
                action_bar, text="Xem chi tiết trường →", style="CardTealLink.TButton",
                command=lambda uid=uni_id: self._controller.show_frame("detail", university_id=uid),
            )
            btn_detail.pack(side="left")

            # Bind click cho tên trường
            name_lbl.bind(
                "<Button-1>",
                lambda e, uid=uni_id: self._controller.show_frame("detail", university_id=uid),
            )

        # Lấy L2 AI Explanation qua background thread để tránh làm đơ giao diện
        def fetch_explanations():
            ai_results = recommend_service.get_explanation(profile, results)
            def update_ui():
                if ai_results:
                    for item in ai_results:
                        uid = str(item.get("university_id"))
                        if uid in exp_frames:
                            _, lbl = exp_frames[uid]
                            explanation = item.get("explanation", "")
                            if explanation:
                                clean_exp = explanation.replace("**", "")
                                lbl.config(text=f"💡 AI Nhận xét: {clean_exp}")
                            else:
                                exp_frames[uid][0].pack_forget()
                else:
                    for frame, _ in exp_frames.values():
                        frame.pack_forget()
            self.after(0, update_ui)

        threading.Thread(target=fetch_explanations, daemon=True).start()

        # Khởi tạo thanh Chat trực tiếp với AI phía dưới
        self._setup_followup_chat()
        self._scroll_to_bottom()

    def _setup_followup_chat(self):
        """Tạo thanh chat tương tác trực tiếp với Gemini AI sau khi hiển thị gợi ý."""
        self._clear_controls()

        # Dòng Quick Pills gợi ý câu hỏi tiếp theo
        pills_row = tb.Frame(self._control_frame)
        pills_row.pack(fill="x", pady=(0, 6))

        tb.Label(
            pills_row, text="💡 Hỏi thêm AI:",
            foreground=self._colors.secondary, font=("Segoe UI", 8, "bold")
        ).pack(side="left", padx=(0, 6))

        quick_questions = [
            "Học phí trường nào hợp lý nhất?",
            "Trường nào có nhiều học bổng?",
            "Đâu là trường đào tạo CNTT tốt?",
        ]

        for q_str in quick_questions:
            tb.Button(
                pills_row, text=q_str, style="QuickPill.TButton",
                command=lambda s=q_str: self._send_ai_chat_message(s)
            ).pack(side="left", padx=3)

        # Khung nhập tin nhắn chat
        input_row = tb.Frame(self._control_frame)
        input_row.pack(fill="x")

        entry_var = tk.StringVar()
        entry = tb.Entry(input_row, textvariable=entry_var, font=("Segoe UI", 10))
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=3)
        entry.focus()

        def submit():
            txt = entry_var.get().strip()
            if not txt:
                return
            entry_var.set("")
            self._send_ai_chat_message(txt)

        entry.bind("<Return>", lambda e: submit())

        tb.Button(input_row, text="Gửi ✈️", style="BannerLink.TButton", command=submit).pack(side="left", padx=(0, 6))
        tb.Button(input_row, text="🔄 Đặt lại", style="QuickPill.TButton", command=self._start_wizard).pack(side="right")

    def _send_ai_chat_message(self, user_question: str):
        """Gửi câu hỏi của người dùng tới Gemini AI qua background thread."""
        self._add_user_bubble(user_question)

        # Thêm bubble tạm "AI đang suy nghĩ..."
        loading_row = tb.Frame(self._scroll.body)
        loading_row.pack(fill="x", pady=6, anchor="w")
        tb.Label(loading_row, text="🤖", font=("Segoe UI", 14)).pack(side="left", anchor="n", padx=(0, 8))
        loading_lbl = tb.Label(
            loading_row, text="⏳ AI đang suy nghĩ...", style="BotBubble.TLabel",
            font=("Segoe UI", 9, "italic")
        )
        loading_lbl.pack(side="left", anchor="w")
        self._scroll_to_bottom()

        profile = self._wizard.get_profile()
        all_unis = self._controller.repo.get_all()

        def worker():
            answer = recommend_service.chat_with_ai(user_question, profile, all_unis)
            def update_ui():
                loading_row.destroy()
                self._add_bot_bubble(answer)
            self.after(0, update_ui)

        threading.Thread(target=worker, daemon=True).start()

