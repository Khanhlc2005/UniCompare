"""
Repository cho collection watchlist (Issue #63).

Muc dich: luu that danh sach truong nguoi dung da luu (watchlist) vao Mongo,
thay cho list o bo nho truoc day - restart app khong con bi mat du lieu.
File nay CHI lo doc/ghi id, khong biet gi ve nghiep vu "da co roi thi khong
them trung" (viec do van la cua watchlist_service goi xuong day).

Schema 1 document trong collection watchlist (ARCHITECTURE.md muc 4):
{
    "_id": ObjectId(...),
    "university_id": "...",
    "saved_at": ISODate(...)
}
"""
from datetime import datetime, timezone

from config import COLLECTION_WATCHLIST
from repositories import mongo_repo

# Xai chung 1 MongoClient voi mongo_repo.repository (giong ai_cache_repo),
# khong tu mo connection rieng. Lay collection lazy - khong connect luc import.
_watchlist_collection = None


def _get_collection():
    global _watchlist_collection
    if _watchlist_collection is None:
        _watchlist_collection = mongo_repo.repository.get_database()[COLLECTION_WATCHLIST]
    return _watchlist_collection


def get_ids() -> list[str]:
    """Lay toan bo university_id dang co trong watchlist."""
    docs = _get_collection().find({})
    return [doc["university_id"] for doc in docs]


def has_id(university_id: str) -> bool:
    """Kiem tra 1 truong da co trong watchlist chua."""
    return _get_collection().find_one({"university_id": university_id}) is not None


def add_id(university_id: str) -> bool:
    """Them 1 truong vao watchlist. Tra ve False neu da co san (khong them trung)."""
    if has_id(university_id):
        return False
    res = _get_collection().insert_one(
        {"university_id": university_id, "saved_at": datetime.now(timezone.utc)}
    )
    return res.acknowledged


def remove_id(university_id: str) -> bool:
    """Bo 1 truong khoi watchlist. Tra ve False neu truoc do chua co."""
    res = _get_collection().delete_one({"university_id": university_id})
    return res.deleted_count > 0
