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
