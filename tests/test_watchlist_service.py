"""Test cho watchlist_service (Issue 1.6 / #63).

Truoc day test bang cach clear truc tiep watchlist_service._watchlist_ids
(list o bo nho) - bien nay khong con ton tai nua sau khi noi Mongo that
(#63). Doi sang mock watchlist_repo bang monkeypatch cua pytest: gio
watchlist_service chi la lop mong goi xuong watchlist_repo, nen test o day
gia lap watchlist_repo bang 1 list trong bo nho - khong can MONGO_URI that,
CI van chay xanh (.github/workflows/test.yml khong set bien Mongo nao).
"""

import pytest

from repositories.mongo_repo import MongoRepositoryError
from services import watchlist_service


class FakeWatchlistRepo:
    """Gia lap watchlist_repo bang list trong bo nho, thay cho Mongo that."""

    def __init__(self):
        self._ids: list[str] = []

    def get_ids(self) -> list[str]:
        return list(self._ids)

    def has_id(self, university_id: str) -> bool:
        return university_id in self._ids

    def add_id(self, university_id: str) -> bool:
        if university_id in self._ids:
            return False
        self._ids.append(university_id)
        return True

    def remove_id(self, university_id: str) -> bool:
        if university_id not in self._ids:
            return False
        self._ids.remove(university_id)
        return True


class LoiKetNoiRepo:
    """Gia lap watchlist_repo khi Mongo mat ket noi/thieu MONGO_URI."""

    def get_ids(self):
        raise MongoRepositoryError("gia lap mat ket noi Mongo")

    def has_id(self, university_id):
        raise MongoRepositoryError("gia lap mat ket noi Mongo")

    def add_id(self, university_id):
        raise MongoRepositoryError("gia lap mat ket noi Mongo")

    def remove_id(self, university_id):
        raise MongoRepositoryError("gia lap mat ket noi Mongo")


@pytest.fixture
def fake_repo(monkeypatch):
    repo = FakeWatchlistRepo()
    monkeypatch.setattr(watchlist_service, "watchlist_repo", repo)
    return repo


def test_them_truong_moi_vao_watchlist(fake_repo):
    ok = watchlist_service.add_to_watchlist("1")

    assert ok is True
    assert watchlist_service.is_in_watchlist("1") is True
    assert watchlist_service.get_watchlist_ids() == ["1"]


def test_them_truong_da_co_khong_bi_trung(fake_repo):
    watchlist_service.add_to_watchlist("1")
    ok = watchlist_service.add_to_watchlist("1")  # them lan 2

    assert ok is False
    assert watchlist_service.get_watchlist_ids() == ["1"]


def test_bo_luu_truong_dang_co(fake_repo):
    watchlist_service.add_to_watchlist("1")
    ok = watchlist_service.remove_from_watchlist("1")

    assert ok is True
    assert watchlist_service.is_in_watchlist("1") is False


def test_bo_luu_truong_khong_ton_tai_tra_ve_false(fake_repo):
    ok = watchlist_service.remove_from_watchlist("khong-ton-tai")

    assert ok is False


def test_mat_ket_noi_mongo_khong_crash_tra_ve_gia_tri_an_toan(monkeypatch):
    """Loi Mongo (VD thieu MONGO_URI) phai bi bat lai o service, khong crash
    app - dung tinh than CLAUDE.md muc 4 (xu ly loi vua du, khong log framework)."""
    monkeypatch.setattr(watchlist_service, "watchlist_repo", LoiKetNoiRepo())

    assert watchlist_service.get_watchlist_ids() == []
    assert watchlist_service.is_in_watchlist("1") is False
    assert watchlist_service.add_to_watchlist("1") is False
    assert watchlist_service.remove_from_watchlist("1") is False
