"""Test cho compare_service (Issue 1.6) - AC: chon truong thu 6 phai bi chan."""

import pytest

from services import compare_service


@pytest.fixture(autouse=True)
def reset_compare_state():
    # state la module-level nen phai reset truoc moi test, khong thi test sau
    # bi anh huong boi test truoc
    compare_service.clear_compare()
    yield
    compare_service.clear_compare()


def test_chon_du_5_truong_thi_duoc():
    for uni_id in ["1", "2", "3", "4", "5"]:
        ok, msg = compare_service.toggle_compare(uni_id)
        assert ok is True
        assert msg == ""
    assert compare_service.get_compare_ids() == ["1", "2", "3", "4", "5"]


def test_chon_truong_thu_6_bi_chan_va_co_thong_bao():
    for uni_id in ["1", "2", "3", "4", "5"]:
        compare_service.toggle_compare(uni_id)

    ok, msg = compare_service.toggle_compare("6")

    assert ok is False
    assert msg != ""
    assert len(compare_service.get_compare_ids()) == 5
    assert "6" not in compare_service.get_compare_ids()


def test_bo_1_truong_ra_roi_chon_truong_khac_van_duoc():
    for uni_id in ["1", "2", "3", "4", "5"]:
        compare_service.toggle_compare(uni_id)

    compare_service.toggle_compare("3")  # bo truong "3" ra
    ok, msg = compare_service.toggle_compare("6")  # chon truong moi

    assert ok is True
    assert msg == ""
    assert "6" in compare_service.get_compare_ids()
    assert "3" not in compare_service.get_compare_ids()
    assert len(compare_service.get_compare_ids()) == 5


def test_toggle_lai_truong_da_chon_thi_bo_ra():
    compare_service.toggle_compare("1")
    ok, msg = compare_service.toggle_compare("1")

    assert ok is True
    assert msg == ""
    assert compare_service.get_compare_ids() == []


def test_clear_compare_xoa_het():
    compare_service.toggle_compare("1")
    compare_service.toggle_compare("2")

    compare_service.clear_compare()

    assert compare_service.get_compare_ids() == []


# ---- Issue 2.8: xac_dinh_tot_nhat (highlight gia tri tot nhat moi tieu chi) ----

def test_hoc_phi_thap_hon_duoc_highlight():
    data = [
        {"id": "1", "tuition_per_year": 55000},
        {"id": "2", "tuition_per_year": 35000},
        {"id": "3", "tuition_per_year": 40000},
    ]
    ket_qua = compare_service.xac_dinh_tot_nhat(data)
    assert ket_qua["tuition"] == {"2"}


def test_ranking_so_nho_hon_duoc_highlight():
    # so hang cang nho cang tot (hang 5 tot hon hang 30), khong phai MAX gia tri so
    data = [
        {"id": "1", "ranking": 30},
        {"id": "2", "ranking": 5},
    ]
    ket_qua = compare_service.xac_dinh_tot_nhat(data)
    assert ket_qua["ranking"] == {"2"}


def test_bang_diem_thi_highlight_ca_hai_khong_chon_ngau_nhien_1():
    data = [
        {"id": "1", "gpa_min": 3.8},
        {"id": "2", "gpa_min": 3.8},
        {"id": "3", "gpa_min": 3.9},
    ]
    ket_qua = compare_service.xac_dinh_tot_nhat(data)
    assert ket_qua["gpa"] == {"1", "2"}


def test_ho_tro_ca_schema_chuan_va_schema_cu_fake_repo():
    # id "1" dung field schema cu (tuition/ielts/gpa), id "2" dung field
    # schema chuan (tuition_per_year/ielts_min/gpa_min) - phai doc dung ca 2
    data = [
        {"id": "1", "tuition": 30000, "ielts": 6.0, "gpa": 3.2},
        {"id": "2", "tuition_per_year": 40000, "ielts_min": 7.0, "gpa_min": 3.5},
    ]
    ket_qua = compare_service.xac_dinh_tot_nhat(data)
    assert ket_qua["tuition"] == {"1"}
    assert ket_qua["ielts"] == {"1"}
    assert ket_qua["gpa"] == {"1"}


def test_tieu_chi_thieu_du_lieu_het_thi_tra_ve_set_rong():
    # fake_repo hien tai chua co field ranking - khong duoc crash, cung
    # khong duoc highlight bua truong nao
    data = [{"id": "1", "tuition": 1000}, {"id": "2", "tuition": 2000}]
    ket_qua = compare_service.xac_dinh_tot_nhat(data)
    assert ket_qua["ranking"] == set()


def test_truong_thieu_field_khong_duoc_tinh_la_tot_nhat():
    # truong "2" khong co du lieu hoc phi -> khong duoc am tham la "tot nhat"
    data = [
        {"id": "1", "tuition": 50000},
        {"id": "2"},
    ]
    ket_qua = compare_service.xac_dinh_tot_nhat(data)
    assert ket_qua["tuition"] == {"1"}
