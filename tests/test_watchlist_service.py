"""Test cho watchlist_service (Issue 1.6)."""

import pytest

from services import watchlist_service


@pytest.fixture(autouse=True)
def reset_watchlist_state():
    watchlist_service._watchlist_ids.clear()
    yield
    watchlist_service._watchlist_ids.clear()


def test_them_truong_moi_vao_watchlist():
    ok = watchlist_service.add_to_watchlist("1")

    assert ok is True
    assert watchlist_service.is_in_watchlist("1") is True
    assert watchlist_service.get_watchlist_ids() == ["1"]


def test_them_truong_da_co_khong_bi_trung():
    watchlist_service.add_to_watchlist("1")
    ok = watchlist_service.add_to_watchlist("1")  # them lan 2

    assert ok is False
    assert watchlist_service.get_watchlist_ids() == ["1"]


def test_bo_luu_truong_dang_co():
    watchlist_service.add_to_watchlist("1")
    ok = watchlist_service.remove_from_watchlist("1")

    assert ok is True
    assert watchlist_service.is_in_watchlist("1") is False


def test_bo_luu_truong_khong_ton_tai_tra_ve_false():
    ok = watchlist_service.remove_from_watchlist("khong-ton-tai")

    assert ok is False
