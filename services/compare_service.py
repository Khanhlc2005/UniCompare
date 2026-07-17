# compare_service.py - Issue 1.6
# State "dang chon de so sanh", dung chung cho Home/Search/Watchlist/Detail
# (ARCHITECTURE.md muc 5.2) - toi da 5 truong. Cung la list module-level nhu
# watchlist_service, khong bay them state manager rieng.

MAX_COMPARE = 5
_compare_ids: list[str] = []


def get_compare_ids() -> list[str]:
    return _compare_ids


def toggle_compare(university_id: str) -> tuple[bool, str]:
    """Tra ve (thanh_cong, thong_bao) de UI hien canh bao khi bi chan."""
    if university_id in _compare_ids:
        _compare_ids.remove(university_id)
        return True, ""
    if len(_compare_ids) >= MAX_COMPARE:
        return False, f"Chi duoc chon toi da {MAX_COMPARE} truong de so sanh"
    _compare_ids.append(university_id)
    return True, ""


def clear_compare() -> None:
    _compare_ids.clear()
