"""Test cho recommend_service.score()/score_all() (Issue 3.5).

Cong thuc/trong so bam sat docs/cong_thuc_diem_rule_based.md (Issue 2.10) - moi
test o day gan voi 1 tieu chi rieng (C1..C6), khong gop chung vao 1 test to.

Meo test: moi test chi de 1 truong (uni) co du lieu cho DUNG 1 tieu chi dang xet,
cac tieu chi con lai deu thieu field nen bi "bo" (khong tinh vao mau so) - nho vay
diem cuoi = diem_tieu_chi / trong_so_tieu_chi * 100, de assert hon la phai tinh
tay ca cong thuc tong.
"""
import pytest

from services import recommend_service as rs


# ─── C1 - Chung chi tieng Anh (trong so 30) ─────────────────────
def test_c1_dat_muc_toi_thieu_ielts():
    profile = {"ielts": 6.5}
    uni = {"ielts_min": 6.5}
    assert rs.score(profile, uni) == 100  # chi con C1, dat -> 30/30


def test_c1_ielts_thieu_dung_0_5_van_duoc_nua_diem():
    # ca bien bat buoc: thieu dung 0.5 so voi ielts_min
    profile = {"ielts": 6.0}
    uni = {"ielts_min": 6.5}
    assert rs.score(profile, uni) == 50  # 15/30 * 100


def test_c1_ielts_thieu_nhieu_hon_0_5_thi_0_diem():
    profile = {"ielts": 5.5}
    uni = {"ielts_min": 6.5}
    assert rs.score(profile, uni) == 0


def test_c1_chua_co_chung_chi_ma_truong_co_yeu_cau_thi_0_diem():
    # phan biet voi "truong khong yeu cau gi" (bo tieu chi) - o day truong CO
    # yeu cau, nguoi dung chi la khong nhap -> phai cham 0, khong duoc bo qua
    profile = {}
    uni = {"ielts_min": 6.5}
    assert rs.score(profile, uni) == 0


def test_c1_lay_ket_qua_tot_nhat_giua_ielts_va_toefl():
    # ielts thieu nhieu (0 diem) nhung toefl dat (30 diem) -> lay toefl
    profile = {"ielts": 5.0, "toefl": 100}
    uni = {"ielts_min": 6.5, "toefl_min": 100}
    assert rs.score(profile, uni) == 100


def test_c1_truong_khong_yeu_cau_tieng_anh_thi_bo_tieu_chi():
    # ielts_min/toefl_min deu thieu -> C1 bo, chi con C6 tinh diem
    profile = {"ielts": 3.0}
    uni = {"ranking": 10}
    assert rs.score(profile, uni) == 100  # 5/5 * 100 (chi con C6)


# ─── C2 - GPA (trong so 15) ──────────────────────────────────────
def test_c2_gpa_vua_du_bang_gpa_min():
    # ca bien bat buoc: GPA vua du bang gpa_min
    profile = {"gpa": 3.0}
    uni = {"gpa_min": 3.0}
    assert rs.score(profile, uni) == 100  # 15/15 * 100


def test_c2_gpa_thieu_duoi_0_2_van_duoc_nua_diem():
    profile = {"gpa": 2.85}
    uni = {"gpa_min": 3.0}
    assert rs.score(profile, uni) == round(8 / 15 * 100)


def test_c2_gpa_thieu_qua_0_2_thi_0_diem():
    profile = {"gpa": 2.5}
    uni = {"gpa_min": 3.0}
    assert rs.score(profile, uni) == 0


def test_c2_truong_khong_cong_bo_gpa_min_thi_bo_tieu_chi():
    # 5/7 truong TQ trong seed dang null gpa_min - phai bo, khong cham 0
    profile = {"gpa": 2.0}
    uni = {"ranking": 10}
    assert rs.score(profile, uni) == 100  # chi con C6


# ─── C3 - Ngan sach (trong so 30) ────────────────────────────────
def test_c3_ngan_sach_sat_nut_bang_dung_hoc_phi():
    # ca bien bat buoc: ngan sach == tuition_per_year * ty gia (khong hon khong kem)
    uni = {"tuition_per_year": 30000, "currency": "CNY"}  # 30000 * 3600 = 108tr
    profile = {"budget_per_year": 108_000_000}
    assert rs.score(profile, uni) == 100  # dung >= nen bang van tinh dat


def test_c3_vuot_ngan_sach_duoi_10_phan_tram_van_duoc_nua_diem():
    uni = {"tuition_per_year": 10000, "currency": "JPY"}  # hoc phi = 1.75tr
    profile = {"budget_per_year": 1_700_000}  # vuot (1.75-1.7)/1.7 = 2.9% <=10%
    assert rs.score(profile, uni) == 50  # 15/30 * 100


def test_c3_vuot_ngan_sach_qua_10_phan_tram_thi_0_diem():
    uni = {"tuition_per_year": 60000, "currency": "CNY"}  # hoc phi = 216tr
    profile = {"budget_per_year": 150_000_000}  # vuot (216-150)/150 = 44%
    assert rs.score(profile, uni) == 0


def test_c3_currency_la_khong_co_trong_bang_ty_gia_thi_bo_tieu_chi():
    # currency khong co trong TY_GIA_VND -> coi nhu thieu du lieu hoc phi -> bo C3
    profile = {"budget_per_year": 100}
    uni = {"tuition_per_year": 10000, "currency": "USD", "ranking": 10}
    assert rs.score(profile, uni) == 100  # chi con C6 tinh diem


# ─── C4 - Uu tien quoc gia (trong so 10) ─────────────────────────
def test_c4_quoc_gia_nam_trong_danh_sach_uu_tien():
    profile = {"preferred_countries": ["Japan"]}
    uni = {"country": "Japan"}
    assert rs.score(profile, uni) == 100  # 10/10 * 100


def test_c4_quoc_gia_khong_nam_trong_danh_sach_uu_tien():
    profile = {"preferred_countries": ["Japan"]}
    uni = {"country": "United Kingdom"}
    assert rs.score(profile, uni) == 0


def test_c4_nguoi_dung_khong_chon_uu_tien_thi_bo_tieu_chi():
    profile = {"preferred_countries": []}
    uni = {"country": "Japan", "ranking": 10}
    assert rs.score(profile, uni) == 100  # chi con C6


# ─── C5 - Uu tien nganh (trong so 10) ────────────────────────────
def test_c5_co_it_nhat_1_nganh_trung():
    profile = {"preferred_majors": ["Khoa hoc may tinh"]}
    uni = {"majors": ["Khoa hoc may tinh", "Kinh te hoc"]}
    assert rs.score(profile, uni) == 100


def test_c5_khong_nganh_nao_trung():
    profile = {"preferred_majors": ["Y khoa"]}
    uni = {"majors": ["Khoa hoc may tinh"]}
    assert rs.score(profile, uni) == 0


def test_c5_nguoi_dung_khong_chon_uu_tien_thi_bo_tieu_chi():
    profile = {"preferred_majors": []}
    uni = {"majors": ["Khoa hoc may tinh"], "ranking": 10}
    assert rs.score(profile, uni) == 100  # chi con C6


# ─── C6 - Bonus ranking (trong so 5) ─────────────────────────────
def test_c6_ranking_top_20():
    assert rs.score({}, {"ranking": 20}) == 100


def test_c6_ranking_21_den_50():
    assert rs.score({}, {"ranking": 50}) == 60  # 3/5 * 100


def test_c6_ranking_51_den_100():
    assert rs.score({}, {"ranking": 100}) == 20  # 1/5 * 100


def test_c6_ranking_qua_100_thi_0_diem():
    # can it nhat 1 tieu chi khac de mau so khong bang 0 (o day la C2, dat 15/15)
    assert rs.score({"gpa": 3.5}, {"ranking": 200, "gpa_min": 3.0}) == round(15 / 20 * 100)


def test_c6_ranking_thieu_thi_bo_tieu_chi():
    profile = {"gpa": 3.5}
    uni = {"gpa_min": 3.0}  # khong co ranking
    assert rs.score(profile, uni) == 100  # chi con C2


# ─── Ca bien bat buoc (DoD PLAN.md): diem khong am / khong vuot 100 ──
def test_ho_so_khong_dat_tieu_chi_nao_diem_khong_duoc_am():
    profile = {
        "gpa": 1.0,
        "ielts": 1.0,
        "toefl": 1,
        "budget_per_year": 1,
        "preferred_countries": ["Japan"],
        "preferred_majors": ["Y khoa"],
    }
    uni = {
        "gpa_min": 4.0,
        "ielts_min": 9.0,
        "toefl_min": 120,
        "tuition_per_year": 100000,
        "currency": "GBP",
        "country": "United Kingdom",
        "majors": ["Khoa hoc may tinh"],
        "ranking": 500,
    }
    diem = rs.score(profile, uni)
    assert diem == 0
    assert diem >= 0


def test_ho_so_dat_het_tat_ca_tieu_chi_diem_khong_duoc_vuot_100():
    profile = {
        "gpa": 4.0,
        "ielts": 9.0,
        "budget_per_year": 1_000_000_000,
        "preferred_countries": ["Japan"],
        "preferred_majors": ["Khoa hoc may tinh"],
    }
    uni = {
        "gpa_min": 3.0,
        "ielts_min": 6.5,
        "tuition_per_year": 10000,
        "currency": "JPY",
        "country": "Japan",
        "majors": ["Khoa hoc may tinh"],
        "ranking": 1,
    }
    diem = rs.score(profile, uni)
    assert diem == 100
    assert diem <= 100


def test_truong_thieu_sach_du_lieu_va_nguoi_dung_khong_uu_tien_tra_ve_0_khong_crash():
    # moi tieu chi deu bo -> mau so = 0, phai tra 0 chu khong duoc ZeroDivisionError
    profile = {}
    uni = {"name": "Truong thieu du lieu"}
    assert rs.score(profile, uni) == 0


# ─── score_all() - chon top N ────────────────────────────────────
def test_score_all_sap_xep_giam_dan_va_cat_dung_top_n():
    profile = {"gpa": 4.0}
    universities = [
        {"id": "a", "name": "A", "gpa_min": 3.0, "ranking": 200},  # gpa dat, rank te -> C6=0
        {"id": "b", "name": "B", "gpa_min": 3.0, "ranking": 10},  # gpa dat + C6 dat
        {"id": "c", "name": "C", "gpa_min": 4.0 - 0.1},  # gpa dat, khong C6
    ]
    ket_qua = rs.score_all(profile, universities, top_n=2)

    assert len(ket_qua) == 2
    diem = [item["score"] for item in ket_qua]
    assert diem == sorted(diem, reverse=True)
    assert ket_qua[0]["university_id"] == "b"  # dat ca C2 + C6 nen cao nhat
    assert all("university_id" in item and "name" in item and "score" in item for item in ket_qua)


def test_score_all_fallback_ve_id_mongo_khi_khong_co_id_chuan():
    profile = {}
    universities = [{"_id": "507f1f77bcf86cd799439011", "name": "X"}]
    ket_qua = rs.score_all(profile, universities, top_n=5)
    assert ket_qua[0]["university_id"] == "507f1f77bcf86cd799439011"


# ─── chat_with_ai & get_explanation ────────────────────────────────
def test_chat_with_ai_no_api_key(monkeypatch):
    monkeypatch.setattr("config.API_KEY", "")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    res = rs.chat_with_ai("Học phí thế nào?", {}, [])
    assert "⚠️" in res or "Chưa có" in res


def test_get_explanation_returns_list_or_none():
    profile = {"gpa": 3.5, "ielts": 6.5, "budget_per_year": 200000000}
    top_unis = [{"university_id": "1", "name": "Test Uni", "score": 80}]
    res = rs.get_explanation(profile, top_unis)
    if res is not None:
        assert isinstance(res, list)
        assert len(res) == 1
        assert "explanation" in res[0]

