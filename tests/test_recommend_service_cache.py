"""Test cho recommend_service.profile_hash()/get_explanation() (Issue 3.1 & 3.8 / #52).

Khác với test_recommend_service.py (Issue 3.5, test score/score_all thuần Python) -
file này test phần nối ai_cache và AI API fallback. Dùng monkeypatch để giả lập
Mongo/AI mà không cần MONGO_URI thật.
"""
import pytest

from services import recommend_service as rs


def test_profile_hash_on_dinh_du_key_khac_thu_tu():
    # dict tạo ra theo 2 thứ tự key khác nhau nhưng nội dung giống hệt
    # nhau -> phải ra cùng 1 hash (sort_keys) để trả đúng cache
    profile_1 = {"gpa": 3.5, "ielts": 6.5, "budget_per_year": 100}
    profile_2 = {"budget_per_year": 100, "ielts": 6.5, "gpa": 3.5}
    assert rs.profile_hash(profile_1) == rs.profile_hash(profile_2)


def test_profile_hash_khac_noi_dung_ra_hash_khac():
    profile_1 = {"gpa": 3.5}
    profile_2 = {"gpa": 3.6}
    assert rs.profile_hash(profile_1) != rs.profile_hash(profile_2)


def test_get_explanation_khong_co_key_thi_tra_none_khong_crash(monkeypatch):
    monkeypatch.setattr(rs.config, "API_KEY", "")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    ket_qua = rs.get_explanation({"gpa": 3.5}, [{"university_id": "a", "score": 90}])
    assert ket_qua is None


def test_get_explanation_loi_api_thi_tra_none_khong_crash(monkeypatch):
    monkeypatch.setattr(rs.config, "has_mongo", lambda: True)
    monkeypatch.setattr(rs.ai_cache_repo, "get_cached_result", lambda ma_hash: None)

    def fail_ai(profile, top_n_results):
        raise RuntimeError("Network Error / API 429 Quota Exceeded")

    monkeypatch.setattr(rs, "_goi_ai_that", fail_ai)

    ket_qua = rs.get_explanation({"gpa": 3.5}, [{"university_id": "a", "score": 90}])
    assert ket_qua is None


def test_get_explanation_goi_ai_1_lan_roi_lan_2_lay_tu_cache(monkeypatch):
    """DoD chính của Issue #52: cùng 1 profile gọi 2 lần -> lần 2 phải lấy
    từ cache, không được gọi lại AI lần nữa."""
    profile = {"gpa": 3.5, "ielts": 6.5}
    top_n = [{"university_id": "a", "score": 90}]

    monkeypatch.setattr(rs.config, "has_mongo", lambda: True)

    cache_gia_lap: dict[str, list[dict]] = {}
    monkeypatch.setattr(rs.ai_cache_repo, "get_cached_result", lambda ma_hash: cache_gia_lap.get(ma_hash))

    def fake_save(ma_hash, result):
        cache_gia_lap[ma_hash] = result
        return True

    monkeypatch.setattr(rs.ai_cache_repo, "save_result", fake_save)

    so_lan_goi_ai = 0

    def fake_goi_ai_that(profile, top_n_results):
        nonlocal so_lan_goi_ai
        so_lan_goi_ai += 1
        return [{"university_id": "a", "score": 90, "explanation": "phù hợp học phí + IELTS"}]

    monkeypatch.setattr(rs, "_goi_ai_that", fake_goi_ai_that)

    ket_qua_lan_1 = rs.get_explanation(profile, top_n)
    ket_qua_lan_2 = rs.get_explanation(profile, top_n)

    assert so_lan_goi_ai == 1  # lần 2 không được gọi lại AI
    assert ket_qua_lan_1 == ket_qua_lan_2
    assert ket_qua_lan_1[0]["explanation"] == "phù hợp học phí + IELTS"


def test_get_explanation_2_profile_khac_nhau_deu_phai_goi_ai_rieng(monkeypatch):
    monkeypatch.setattr(rs.config, "has_mongo", lambda: True)

    cache_gia_lap: dict[str, list[dict]] = {}
    monkeypatch.setattr(rs.ai_cache_repo, "get_cached_result", lambda ma_hash: cache_gia_lap.get(ma_hash))

    def fake_save(ma_hash, result):
        cache_gia_lap[ma_hash] = result
        return True

    monkeypatch.setattr(rs.ai_cache_repo, "save_result", fake_save)

    so_lan_goi_ai = 0

    def fake_goi_ai_that(profile, top_n_results):
        nonlocal so_lan_goi_ai
        so_lan_goi_ai += 1
        return [{"university_id": "a", "score": 90, "explanation": f"lần gọi thứ {so_lan_goi_ai}"}]

    monkeypatch.setattr(rs, "_goi_ai_that", fake_goi_ai_that)

    top_n = [{"university_id": "a", "score": 90}]
    rs.get_explanation({"gpa": 3.5}, top_n)
    rs.get_explanation({"gpa": 4.0}, top_n)

    assert so_lan_goi_ai == 2


def test_get_explanation_khong_tu_goi_lai_score_all(monkeypatch):
    monkeypatch.setattr(rs.config, "has_mongo", lambda: True)
    monkeypatch.setattr(rs.ai_cache_repo, "get_cached_result", lambda ma_hash: None)

    def fail_neu_goi(*args, **kwargs):
        raise AssertionError("get_explanation không được tự gọi score_all()")

    monkeypatch.setattr(rs, "score_all", fail_neu_goi)
    monkeypatch.setattr(rs, "_goi_ai_that", lambda p, t: None)

    ket_qua = rs.get_explanation({"gpa": 3.5}, [{"university_id": "a", "score": 90}])
    assert ket_qua is None
