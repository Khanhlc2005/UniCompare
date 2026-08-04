# -*- coding: utf-8 -*-
"""wizard_service.py — Issue 3.6: Logic & Validation cho Wizard 4 bước thu thập hồ sơ.

4 bước thu thập thông tin người dùng:
- Bước 1: Học lực (GPA): Thu thập & chuẩn hóa về thang 4.0.
- Bước 2: Chứng chỉ tiếng Anh (IELTS / TOEFL): 0.0 - 9.0 (IELTS), 0 - 120 (TOEFL).
- Bước 3: Ngân sách học phí (VND/năm): Xử lý số tiền hoặc định dạng "200tr", "150 triệu".
- Bước 4: Ưu tiên (Quốc gia & Ngành học): Danh sách lựa chọn hoặc tất cả.

Đảm bảo sau 4 bước thu thập đúng định dạng dict profile cho recommend_service.py.
"""

import re

# Dai dien cho "khong gioi han ngan sach" - lon hon bat ky hoc phi thuc te nao
# sau khi quy doi VND (xem TY_GIA_VND trong recommend_service.py), de tieu chi
# C3 luon dat diem toi da thay vi bi hieu nham la "thieu du lieu ngan sach".
NGAN_SACH_KHONG_GIOI_HAN = 10**12


def parse_gpa(raw_input: str | float | int) -> tuple[bool, float | None, str]:
    """Validate & quy đổi GPA về thang 4.0.

    - Nếu gpa > 4.0 và <= 10.0: coi là thang 10, quy đổi = gpa / 2.5.
    - Nếu 0.0 <= gpa <= 4.0: coi là thang 4.
    - Khung ngoài 0-10 hoặc sai định dạng: báo lỗi.
    """
    if raw_input is None or str(raw_input).strip() == "":
        return False, None, "Vui lòng nhập điểm GPA (ví dụ: 3.2 hoặc 8.0)."

    try:
        val = float(str(raw_input).replace(",", ".").strip())
    except ValueError:
        return False, None, "GPA phải là một con số (ví dụ: 3.2 hoặc 8.5)."

    if val < 0.0 or val > 10.0:
        return False, None, "GPA phải nằm trong khoảng từ 0.0 đến 10.0."

    if val > 4.0:
        # Quy đổi từ thang 10 sang thang 4
        gpa_4 = round(val / 2.5, 2)
    else:
        gpa_4 = round(val, 2)

    return True, gpa_4, f"GPA hợp lệ: {gpa_4}/4.0 (gốc: {val})"


def parse_ielts(raw_input: str | float | int) -> tuple[bool, float | None, str]:
    """Validate điểm IELTS (0.0 - 9.0). 0 hoặc rỗng nghĩa là chưa có."""
    text = str(raw_input or "").strip().lower()
    if text in ("", "0", "chưa có", "chua co", "khong", "không", "none"):
        return True, 0.0, "Chưa có chứng chỉ IELTS (tính 0.0)."

    try:
        val = float(text.replace(",", "."))
    except ValueError:
        return False, None, "Điểm IELTS phải là một con số từ 0.0 đến 9.0 (hoặc nhập 0 nếu chưa có)."

    if val < 0.0 or val > 9.0:
        return False, None, "Điểm IELTS phải nằm trong thang điểm từ 0.0 đến 9.0."

    return True, round(val, 1), f"IELTS: {val}"


def parse_toefl(raw_input: str | float | int | None) -> tuple[bool, float | None, str]:
    """Validate điểm TOEFL (0 - 120). Trả về None nếu không nhập."""
    if raw_input is None or str(raw_input).strip() in ("", "0", "chưa có", "chua co"):
        return True, None, "Không nhập TOEFL."

    try:
        val = float(str(raw_input).replace(",", ".").strip())
    except ValueError:
        return False, None, "Điểm TOEFL phải là số từ 0 đến 120."

    if val < 0.0 or val > 120.0:
        return False, None, "Điểm TOEFL phải nằm trong khoảng 0 - 120."

    return True, round(val, 1), f"TOEFL: {val}"


def parse_budget(raw_input: str | float | int) -> tuple[bool, float | None, str]:
    """Validate ngân sách học phí (VND/năm).

    Hỗ trợ nhập: "200000000", "200tr", "200 triệu", "150tr/năm", v.v.
    """
    text = str(raw_input or "").strip().lower()

    # "khong gioi han" phai kiem tra TRUOC nhanh "0/rong" ben duoi - y nghia
    # nguoc han nhau: nguoi dung KHONG bi gioi han tien (cham C3 toi da), khac
    # voi "khong nhap gi/ngan sach 0" la thieu du lieu nen cham 0 diem (xem
    # recommend_service._diem_c3_ngan_sach).
    if text in ("không giới hạn", "khong gioi han", "vô hạn", "vo han", "unlimited"):
        return True, NGAN_SACH_KHONG_GIOI_HAN, "Ngân sách: Không giới hạn"

    if text == "" or text in ("0", "khong", "không", "chưa rõ", "chua ro"):
        return True, 0.0, "Ngân sách: 0 VNĐ/năm"

    # Xử lý các từ khóa "tr", "triệu", "tỷ", "ty"
    multiplier = 1
    if "triệu" in text or "trieu" in text or "tr" in text:
        multiplier = 1_000_000
        text = re.sub(r"(triệu|trieu|tr|/năm|/nam|vnd|vnđ)", "", text).strip()
    elif "tỷ" in text or "ty" in text:
        multiplier = 1_000_000_000
        text = re.sub(r"(tỷ|ty|/năm|/nam|vnd|vnđ)", "", text).strip()
    else:
        text = re.sub(r"(vnd|vnđ|/năm|/nam)", "", text).strip()

    try:
        val = float(text.replace(",", ".").replace(" ", ""))
    except ValueError:
        return False, None, "Ngân sách không hợp lệ. Vui lòng nhập số tiền (ví dụ: 200,000,000 hoặc 200 triệu)."

    total_budget = val * multiplier

    if total_budget < 0:
        return False, None, "Ngân sách không được là số âm."

    # Nếu người dùng nhập số quá nhỏ (ví dụ nhập 200 nhưng quên gõ "tr"), tự động coi là triệu nếu < 10000
    if total_budget < 10_000 and multiplier == 1 and total_budget > 0:
        total_budget *= 1_000_000

    return True, total_budget, f"Ngân sách: {total_budget:,.0f} VNĐ/năm"


class WizardState:
    """Quản lý trạng thái và lưu trữ hồ sơ qua 4 bước Wizard."""

    def __init__(self):
        self.step = 1  # 1 đến 4
        self.profile = {
            "gpa": None,
            "ielts": None,
            "toefl": None,
            "budget_per_year": None,
            "preferred_countries": [],
            "preferred_majors": [],
        }

    def reset(self):
        self.step = 1
        self.profile = {
            "gpa": None,
            "ielts": None,
            "toefl": None,
            "budget_per_year": None,
            "preferred_countries": [],
            "preferred_majors": [],
        }

    def set_gpa(self, raw_input) -> tuple[bool, str]:
        ok, val, msg = parse_gpa(raw_input)
        if ok:
            self.profile["gpa"] = val
            self.step = 2
        return ok, msg

    def set_english(self, ielts_raw, toefl_raw=None) -> tuple[bool, str]:
        ok_i, val_i, msg_i = parse_ielts(ielts_raw)
        if not ok_i:
            return False, msg_i

        ok_t, val_t, msg_t = parse_toefl(toefl_raw)
        if not ok_t:
            return False, msg_t

        self.profile["ielts"] = val_i
        self.profile["toefl"] = val_t
        self.step = 3
        return True, f"{msg_i}"

    def set_budget(self, raw_input) -> tuple[bool, str]:
        ok, val, msg = parse_budget(raw_input)
        if ok:
            self.profile["budget_per_year"] = val
            self.step = 4
        return ok, msg

    def set_preferences(self, countries: list[str] | None = None, majors: list[str] | None = None) -> tuple[bool, str]:
        self.profile["preferred_countries"] = countries or []
        self.profile["preferred_majors"] = majors or []
        self.step = 5  # Hoàn thành 4 bước
        return True, "Hoàn tất thu thập thông tin hồ sơ."

    def is_complete(self) -> bool:
        return self.step > 4

    def get_profile(self) -> dict:
        return self.profile
