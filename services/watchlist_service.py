# watchlist_service.py - Issue 1.6 / #63
# Quan ly danh sach truong da luu (watchlist). Truoc day luu tam trong bo nho
# (list o module-level), gio noi that xuong Mongo collection "watchlist" theo
# ARCHITECTURE.md muc 4 - khong con mat du lieu khi restart app. Giu nguyen 4
# ham public va signature cu (watchlist_page.py, detail_page.py dang goi
# thang cac ham nay) - chi doi phan than ham tu list sang goi watchlist_repo.
#
# Bat loi Mongo (MongoRepositoryError/PyMongoError) ngay o day, giong cach
# recommend_service dang lam voi ai_cache_repo - mat ket noi/thieu MONGO_URI
# thi in canh bao va tra ve gia tri "an toan" (list rong/False), khong crash
# app (CLAUDE.md muc 4: xu ly loi vua du).

from pymongo.errors import PyMongoError

from repositories import watchlist_repo
from repositories.mongo_repo import MongoRepositoryError


def get_watchlist_ids() -> list[str]:
    try:
        return watchlist_repo.get_ids()
    except (MongoRepositoryError, PyMongoError) as exc:
        print(f"[canh bao] Khong doc duoc watchlist tu MongoDB: {exc}")
        return []


def add_to_watchlist(university_id: str) -> bool:
    try:
        return watchlist_repo.add_id(university_id)
    except (MongoRepositoryError, PyMongoError) as exc:
        print(f"[canh bao] Khong luu duoc vao watchlist (MongoDB): {exc}")
        return False


def remove_from_watchlist(university_id: str) -> bool:
    try:
        return watchlist_repo.remove_id(university_id)
    except (MongoRepositoryError, PyMongoError) as exc:
        print(f"[canh bao] Khong bo luu duoc watchlist (MongoDB): {exc}")
        return False


def is_in_watchlist(university_id: str) -> bool:
    try:
        return watchlist_repo.has_id(university_id)
    except (MongoRepositoryError, PyMongoError) as exc:
        print(f"[canh bao] Khong kiem tra duoc watchlist (MongoDB): {exc}")
        return False
