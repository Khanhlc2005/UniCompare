# watchlist_service.py - Issue 1.6
# Quan ly danh sach truong da luu (watchlist). Tuan 1 chua noi Mongo, luu tam
# trong bo nho (list o module-level) - ARCHITECTURE.md da chot noi luu cuoi
# cung la Mongo collection "watchlist", viec noi xuong that la cua tuan 2
# (Issue 2.1-2.3, mongo_repo). Doi id de dung chung 1 list module-level la du,
# app 1 process 1 user, khong can class/singleton gi them.

_watchlist_ids: list[str] = []


def get_watchlist_ids() -> list[str]:
    return _watchlist_ids


def add_to_watchlist(university_id: str) -> bool:
    if university_id in _watchlist_ids:
        return False  # da co roi thi thoi, khong them trung
    _watchlist_ids.append(university_id)
    return True


def remove_from_watchlist(university_id: str) -> bool:
    if university_id not in _watchlist_ids:
        return False
    _watchlist_ids.remove(university_id)
    return True


def is_in_watchlist(university_id: str) -> bool:
    return university_id in _watchlist_ids
