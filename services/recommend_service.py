"""recommend_service.py — L1 rule engine + noi L2 cache cho chatbot goi y truong.

Cong thuc/trong so (score/score_all, Issue 3.5) lay DUNG theo
docs/cong_thuc_diem_rule_based.md (Issue 2.10, nhom da review) - KHONG tu doi
trong so/tieu chi o day. Xem file do de biet ly do chon trong so va cac case
bien da chot. score_all() nhan san list universities (da lay tu
repo.get_all()/search() o noi goi ham), khong tu query Mongo trong nay.

profile_hash()/get_explanation() (Issue 3.1) noi L1 voi ai_cache_repo - CHUA
goi AI that (do la Issue 3.8 cua Nam Anh, can API_KEY/SDK), chi chua san diem
noi _goi_ai_that() va logic cache. Khong import requests/AI SDK o day.
"""

import hashlib
import json
import os
import re
import urllib.error
import urllib.request

from pymongo.errors import PyMongoError

import config
from repositories import ai_cache_repo
from repositories.mongo_repo import MongoRepositoryError

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


def profile_hash(profile: dict) -> str:
    """Hash sha256 cua 1 ho so, dung lam key cache trong ai_cache.

    sort_keys=True de cung 1 profile (du dict duoc tao theo thu tu key khac
    nhau) luon ra dung 1 chuoi -> dung 1 hash, khong bi cache trung ho so.
    """
    chuoi_on_dinh = json.dumps(profile, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(chuoi_on_dinh.encode("utf-8")).hexdigest()


def _goi_ai_that(profile: dict, top_n_results: list[dict]) -> list[dict] | None:
    """Gọi AI API (Google Gemini / OpenAI) để sinh lời giải thích ngắn cho top N kết quả.

    Tự động thử các model khả dụng (gemini-flash-latest, gemini-2.0-flash...) và fallback
    an toàn (trả về None) nếu:
    - Không có API_KEY / GEMINI_API_KEY trong .env / config
    - Mất kết nối mạng / timeout
    - Hết quota / API error (HTTP 429, 401, 500)
    """
    api_key = config.API_KEY or os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    prompt_data = {
        "profile": profile,
        "top_universities": top_n_results,
    }

    prompt = (
        "Bạn là chuyên gia tư vấn du học của UniCompare. "
        "Dựa vào hồ sơ học sinh và danh sách Top trường đại học dưới đây:\n"
        f"{json.dumps(prompt_data, ensure_ascii=False)}\n\n"
        "Hãy viết 1-2 câu ngắn gọn giải thích lý do trường đó phù hợp (hoặc chưa phù hợp) "
        "với hồ sơ. Trả về đúng 1 JSON array dạng: "
        '[{"university_id": "...", "score": 85, "explanation": "Lời giải thích ngắn 1-2 câu..."}, ...]'
    )

    models_to_try = ["gemini-flash-latest", "gemini-2.0-flash", "gemini-pro-latest", "gemma-4-26b-a4b-it"]

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.3
            }
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                raw_body = resp.read().decode("utf-8")
                data = json.loads(raw_body)
                content_text = data["candidates"][0]["content"]["parts"][0]["text"]

                json_match = re.search(r"\[.*\]", content_text, re.DOTALL)
                raw_json = json_match.group(0) if json_match else content_text
                parsed_list = json.loads(raw_json)

                if isinstance(parsed_list, list) and len(parsed_list) > 0:
                    explanation_map = {
                        str(item.get("university_id")): item.get("explanation", "")
                        for item in parsed_list if isinstance(item, dict)
                    }

                    output = []
                    for item in top_n_results:
                        uid = str(item.get("university_id"))
                        item_copy = dict(item)
                        item_copy["explanation"] = explanation_map.get(
                            uid, f"Điểm phù hợp {item.get('score')}% dựa trên tiêu chí GPA, IELTS và ngân sách."
                        )
                        output.append(item_copy)
                    return output
        except Exception:
            continue

    return None


def get_explanation(profile: dict, top_n_results: list[dict]) -> list[dict] | None:
    """L2 - lấy explanation đã cache, chưa có thì mới gọi AI thật (Issue 3.8 / #52).

    Bất cứ lỗi Mongo/AI nào (thiếu MONGO_URI, mất mạng, chưa có key, hết quota...)
    đều trả về None thay vì raise - đúng tinh thần fallback L1 ở ARCHITECTURE.md mục 6.
    """
    ma_hash = profile_hash(profile)

    # 1. Thử lấy từ Mongo Cache (nếu có Mongo)
    if config.has_mongo():
        try:
            da_cache = ai_cache_repo.get_cached_result(ma_hash)
            if da_cache is not None:
                return da_cache  # Có cache -> trả về ngay, không gọi AI
        except (MongoRepositoryError, PyMongoError):
            pass

    # 2. Chưa có cache -> Gọi AI API
    try:
        ket_qua_ai = _goi_ai_that(profile, top_n_results)
    except Exception:
        return None  # AI lỗi -> fallback L1, không crash app

    if ket_qua_ai is None:
        return None

    # 3. Lưu cache vào Mongo nếu có Mongo
    if config.has_mongo():
        try:
            ai_cache_repo.save_result(ma_hash, ket_qua_ai)
        except (MongoRepositoryError, PyMongoError):
            pass

    return ket_qua_ai


def chat_with_ai(user_question: str, profile: dict, all_unis: list[dict]) -> str:
    """Cho phép người dùng hỏi đáp trực tiếp với Gemini AI về các trường đại học trong hệ thống."""
    api_key = config.API_KEY or os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return "⚠️ Chưa có GEMINI_API_KEY trong file .env. Vui lòng bổ sung API Key để sử dụng tính năng trò chuyện AI."

    unis_info = []
    for u in all_unis[:15]:
        unis_info.append({
            "name": u.get("name"),
            "country": u.get("country"),
            "city": u.get("city"),
            "gpa_min": u.get("gpa_min"),
            "ielts_min": u.get("ielts_min"),
            "tuition": f"{u.get('tuition_per_year')} {u.get('currency', 'USD')}/năm",
            "majors": u.get("majors", [])[:5] if isinstance(u.get("majors"), list) else u.get("majors", "")
        })

    prompt_system = (
        "Bạn là Trợ lý AI tư vấn du học thông minh của UniCompare. "
        f"Hồ sơ người dùng hiện tại: GPA {profile.get('gpa')}, IELTS {profile.get('ielts')}, Ngân sách {profile.get('budget_per_year', 0):,.0f} VNĐ/năm.\n\n"
        f"Danh sách các trường đại học trong hệ thống UniCompare:\n{json.dumps(unis_info, ensure_ascii=False)}\n\n"
        f"Câu hỏi của sinh viên: '{user_question}'\n\n"
        "Hãy trả lời bằng tiếng Việt thân thiện, rõ ràng (2-4 câu hoặc gạch đầu dòng), tư vấn dựa trên thông tin trường và hồ sơ sinh viên."
    )

    models_to_try = ["gemini-flash-latest", "gemini-2.0-flash", "gemma-4-26b-a4b-it"]

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt_system}]}],
            "generationConfig": {"temperature": 0.5}
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text.strip()
        except Exception:
            continue

    return "⚠️ Hiện không thể kết nối tới AI API (vui lòng kiểm tra lại mạng hoặc quota API Key)."
