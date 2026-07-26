"""recommend_service.py — L1 rule engine cho chatbot goi y truong (Issue 3.5).

Cong thuc/trong so lay DUNG theo docs/cong_thuc_diem_rule_based.md (Issue 2.10,
nhom da review) - KHONG tu doi trong so/tieu chi o day. Xem file do de biet ly do
chon trong so va cac case bien da chot.

Luu y: day la L1 - thuan Python, khong duoc import requests/AI SDK/ai_cache_repo o
file nay (do la L2, Issue 3.1/3.8). score_all() nhan san list universities (da lay
tu repo.get_all()/search() o noi goi ham), khong tu query Mongo trong nay.
"""

# Ty gia tham khao luc viet tai lieu 2.10 (25/07/2026) - hard-code vi L1 khong duoc
# goi mang. Currency nao khong co trong bang nay coi nhu thieu du lieu hoc phi (bo C3).
TY_GIA_VND = {
    "CNY": 3600,
    "JPY": 175,
    "KRW": 19,
    "GBP": 34500,
}

# Trong so 6 tieu chi, tong = 100 (dung nhu tai lieu 2.10 muc 2)
TRONG_SO = {
    "c1_tieng_anh": 30,
    "c2_gpa": 15,
    "c3_ngan_sach": 30,
    "c4_quoc_gia": 10,
    "c5_nganh": 10,
    "c6_ranking": 5,
}


def _diem_c1_tieng_anh(profile: dict, uni: dict) -> float | None:
    """C1 - so ielts/toefl nguoi dung voi ielts_min/toefl_min truong, lay ket qua tot nhat."""
    ielts_min = uni.get("ielts_min")
    toefl_min = uni.get("toefl_min")
    if ielts_min is None and toefl_min is None:
        return None  # truong khong cong bo yeu cau tieng Anh nao -> bo tieu chi

    ung_vien = []
    if ielts_min is not None:
        ielts = profile.get("ielts")
        if ielts is None:
            ung_vien.append(0)  # truong co yeu cau ma nguoi dung chua co IELTS -> cham 0
        elif ielts >= ielts_min:
            ung_vien.append(30)
        elif ielts_min - ielts <= 0.5:
            ung_vien.append(15)
        else:
            ung_vien.append(0)

    if toefl_min is not None:
        toefl = profile.get("toefl")
        if toefl is None:
            ung_vien.append(0)
        elif toefl >= toefl_min:
            ung_vien.append(30)
        elif toefl_min - toefl <= 10:
            ung_vien.append(15)
        else:
            ung_vien.append(0)

    return max(ung_vien)


def _diem_c2_gpa(profile: dict, uni: dict) -> float | None:
    """C2 - so gpa nguoi dung voi gpa_min truong."""
    gpa_min = uni.get("gpa_min")
    if gpa_min is None:
        return None  # rat nhieu truong TQ trong seed dang null gpa_min -> bo tieu chi

    gpa = profile.get("gpa")
    if gpa is None:
        return 0
    if gpa >= gpa_min:
        return 15
    if gpa_min - gpa <= 0.2:
        return 8
    return 0


def _quy_doi_hoc_phi_vnd(uni: dict) -> float | None:
    tuition = uni.get("tuition_per_year")
    currency = uni.get("currency")
    if tuition is None or currency not in TY_GIA_VND:
        return None
    return tuition * TY_GIA_VND[currency]


def _diem_c3_ngan_sach(profile: dict, uni: dict) -> float | None:
    """C3 - so ngan sach VND/nam nguoi dung voi hoc phi truong da quy doi VND."""
    hoc_phi_vnd = _quy_doi_hoc_phi_vnd(uni)
    if hoc_phi_vnd is None:
        return None  # thieu tuition_per_year hoac currency la -> bo tieu chi

    budget = profile.get("budget_per_year")
    if not budget:
        return 0  # khong nhap hoac ngan sach 0 -> khong so duoc, cham 0 (tranh chia 0)

    if budget >= hoc_phi_vnd:  # bang dung cung tinh dat (dung >=)
        return 30
    # % vuot tinh tren ngan sach (xem vi du Fudan trong tai lieu 2.10 muc 6:
    # 216tr hoc phi, 150tr ngan sach -> vuot 66/150 = 44%, khong phai 66/216)
    vuot = (hoc_phi_vnd - budget) / budget
    if vuot <= 0.10:
        return 15
    return 0


def _diem_c4_quoc_gia(profile: dict, uni: dict) -> float | None:
    """C4 - uu tien quoc gia, nhi phan."""
    uu_tien = profile.get("preferred_countries") or []
    if not uu_tien:
        return None  # nguoi dung de trong buoc uu tien -> bo tieu chi khoi mau so
    return 10 if uni.get("country") in uu_tien else 0


def _diem_c5_nganh(profile: dict, uni: dict) -> float | None:
    """C5 - uu tien nganh, nhi phan (trung it nhat 1 nganh)."""
    uu_tien = profile.get("preferred_majors") or []
    if not uu_tien:
        return None
    majors_truong = uni.get("majors") or []
    return 10 if any(nganh in majors_truong for nganh in uu_tien) else 0


def _diem_c6_ranking(uni: dict) -> float | None:
    """C6 - bonus ranking, khong lay tu profile."""
    ranking = uni.get("ranking")
    if ranking is None:
        return None  # ranking null -> bo tieu chi
    if ranking <= 20:
        return 5
    if ranking <= 50:
        return 3
    if ranking <= 100:
        return 1
    return 0


def score(profile: dict, university: dict) -> int:
    """Cham 1 truong 0-100 theo cong thuc 2.10 (tong trong so co so duoc, quy ve thang 100)."""
    tieu_chi = [
        (_diem_c1_tieng_anh(profile, university), TRONG_SO["c1_tieng_anh"]),
        (_diem_c2_gpa(profile, university), TRONG_SO["c2_gpa"]),
        (_diem_c3_ngan_sach(profile, university), TRONG_SO["c3_ngan_sach"]),
        (_diem_c4_quoc_gia(profile, university), TRONG_SO["c4_quoc_gia"]),
        (_diem_c5_nganh(profile, university), TRONG_SO["c5_nganh"]),
        (_diem_c6_ranking(university), TRONG_SO["c6_ranking"]),
    ]

    tong_diem = 0.0
    tong_trong_so = 0
    for diem, trong_so in tieu_chi:
        if diem is None:
            continue  # tieu chi bi bo vi thieu du lieu, khong tinh vao mau so
        tong_diem += diem
        tong_trong_so += trong_so

    if tong_trong_so == 0:
        return 0  # thieu sach du lieu de so sanh -> khong du du lieu de cham

    diem_cuoi = tong_diem / tong_trong_so * 100
    return round(max(0, min(100, diem_cuoi)))


def score_all(profile: dict, universities: list[dict], top_n: int = 5) -> list[dict]:
    """Cham diem ca danh sach truong, tra ve top_n sap giam dan theo score.

    universities lay san tu repo.get_all()/repo.search() o noi goi ham nay -
    khong tu query Mongo trong service.
    """
    ket_qua = [
        {
            "university_id": uni.get("id", uni.get("_id")),
            "name": uni.get("name"),
            "score": score(profile, uni),
        }
        for uni in universities
    ]
    ket_qua.sort(key=lambda item: item["score"], reverse=True)
    return ket_qua[:top_n]
