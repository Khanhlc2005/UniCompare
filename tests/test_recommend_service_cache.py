"""Test cho recommend_service.profile_hash()/get_explanation() (Issue 3.1).

Khac voi test_recommend_service.py (Issue 3.5, test score/score_all thuan
Python) - file nay test phan noi ai_cache. Dung monkeypatch de gia lap
Mongo/AI thay vi can MONGO_URI that, nen chay duoc tren CI luon, khong bi
skip nhu tests/test_ai_cache_repo.py.
"""
import pytest

from services import recommend_service as rs


def test_profile_hash_on_dinh_du_key_khac_thu_tu():
    # dict tao ra theo 2 thu tu key khac nhau nhung noi dung giong het
    # nhau -> phai ra cung 1 hash (sort_keys) de tra dung cache
    profile_1 = {"gpa": 3.5, "ielts": 6.5, "budget_per_year": 100}
    profile_2 = {"budget_per_year": 100, "ielts": 6.5, "gpa": 3.5}
    assert rs.profile_hash(profile_1) == rs.profile_hash(profile_2)


def test_profile_hash_khac_noi_dung_ra_hash_khac():
    profile_1 = {"gpa": 3.5}
    profile_2 = {"gpa": 3.6}
    assert rs.profile_hash(profile_1) != rs.profile_hash(profile_2)


def test_get_explanation_khong_co_mongo_thi_tra_none_khong_crash(monkeypatch):
    monkeypatch.setattr(rs.config, "has_mongo", lambda: False)
    ket_qua = rs.get_explanation({"gpa": 3.5}, [{"university_id": "a", "score": 90}])
    assert ket_qua is None


def test_get_explanation_chua_noi_ai_that_thi_tra_none_khong_crash(monkeypatch):
    # gia lap co Mongo nhung cache dang rong va _goi_ai_that con la
    # NotImplementedError that (chua bi mock) - dung y nghia hien tai cua
    # Issue 3.1: Issue 3.8 chua lam thi phai tra None, khong duoc crash
    monkeypatch.setattr(rs.config, "has_mongo", lambda: True)
    monkeypatch.setattr(rs.ai_cache_repo, "get_cached_result", lambda ma_hash: None)

    ket_qua = rs.get_explanation({"gpa": 3.5}, [{"university_id": "a", "score": 90}])
    assert ket_qua is None


def test_get_explanation_goi_ai_1_lan_roi_lan_2_lay_tu_cache(monkeypatch):
    """DoD chinh cua Issue 3.1: cung 1 profile goi 2 lan -> lan 2 phai lay
    tu cache, khong duoc goi lai AI lan nua."""
    profile = {"gpa": 3.5, "ielts": 6.5}
    top_n = [{"university_id": "a", "score": 90}]

    monkeypatch.setattr(rs.config, "has_mongo", lambda: True)

    # gia lap collection ai_cache bang 1 dict thuong, khong dung Mongo that
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
        return [{"university_id": "a", "score": 90, "explanation": "phu hop hoc phi + IELTS"}]

    monkeypatch.setattr(rs, "_goi_ai_that", fake_goi_ai_that)

    ket_qua_lan_1 = rs.get_explanation(profile, top_n)
    ket_qua_lan_2 = rs.get_explanation(profile, top_n)

    assert so_lan_goi_ai == 1  # lan 2 khong duoc goi lai AI
    assert ket_qua_lan_1 == ket_qua_lan_2
    assert ket_qua_lan_1[0]["explanation"] == "phu hop hoc phi + IELTS"


def test_get_explanation_2_profile_khac_nhau_deu_phai_goi_ai_rieng(monkeypatch):
    # tranh bug nguoc lai: 2 ho so khac nhau ma lai bi dung chung 1 cache
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
        return [{"university_id": "a", "score": 90, "explanation": f"lan goi thu {so_lan_goi_ai}"}]

    monkeypatch.setattr(rs, "_goi_ai_that", fake_goi_ai_that)

    top_n = [{"university_id": "a", "score": 90}]
    rs.get_explanation({"gpa": 3.5}, top_n)
    rs.get_explanation({"gpa": 4.0}, top_n)

    assert so_lan_goi_ai == 2


def test_get_explanation_khong_tu_goi_lai_score_all(monkeypatch):
    # dam bao get_explanation KHONG dung score_all ben trong - neu co goi se
    # lam sai tinh than tach L1/L2, va co the loi vi thieu tham so universities
    monkeypatch.setattr(rs.config, "has_mongo", lambda: True)
    monkeypatch.setattr(rs.ai_cache_repo, "get_cached_result", lambda ma_hash: None)

    def fail_neu_goi(*args, **kwargs):
        raise AssertionError("get_explanation khong duoc tu goi score_all()")

    monkeypatch.setattr(rs, "score_all", fail_neu_goi)

    # _goi_ai_that chua implement that nen se raise NotImplementedError va
    # get_explanation phai bat lai, tra None - khong duoc dam vao score_all
    ket_qua = rs.get_explanation({"gpa": 3.5}, [{"university_id": "a", "score": 90}])
    assert ket_qua is None
