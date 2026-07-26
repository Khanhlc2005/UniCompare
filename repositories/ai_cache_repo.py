"""
Repository cho collection ai_cache.

Muc dich: cung 1 ho so nguoi dung (profile) thi khong goi lai AI API nua,
lay thang ket qua da luu trong Mongo ra - tiet kiem quota va phan hoi nhanh
hon. File nay CHI lo phan luu/doc du lieu, khong tinh profile_hash va khong
tu goi AI o day (2 viec do la cua recommend_service, Issue 3.1).

Schema 1 document trong collection ai_cache:
{
    "_id": ObjectId(...),
    "profile_hash": "sha256 cua ho so nguoi dung",
    "result": [
        {"university_id": "...", "score": 87, "explanation": "..."},
        ...
    ],
    "created_at": ISODate(...)
}
"""
from datetime import datetime, timezone

from config import COLLECTION_AI_CACHE
from repositories import mongo_repo

# Xai chung 1 MongoClient voi mongo_repo.repository thay vi tu tao client
# rieng - tranh mo 2 connection toi cung 1 Atlas cluster. Lay collection
# lazy (khong connect luc import) de dung format voi mongo_repo va khong
# lam app crash neu thieu MONGO_URI.
_ai_cache_collection = None


def _get_collection():
    global _ai_cache_collection
    if _ai_cache_collection is None:
        _ai_cache_collection = mongo_repo.repository.get_database()[COLLECTION_AI_CACHE]
    return _ai_cache_collection


def get_cached_result(profile_hash: str) -> list[dict] | None:
    """Lay ket qua da cache theo profile_hash. None neu chua tung cache."""
    doc = _get_collection().find_one({"profile_hash": profile_hash})
    if doc is None:
        return None
    return doc.get("result")


def save_result(profile_hash: str, result: list[dict]) -> bool:
    """Luu ket qua AI cho 1 profile_hash. Neu da co thi ghi de (upsert)."""
    res = _get_collection().update_one(
        {"profile_hash": profile_hash},
        {
            "$set": {
                "profile_hash": profile_hash,
                "result": result,
                "created_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )
    return res.acknowledged


def clear_cache(profile_hash: str) -> bool:
    """Xoa 1 cache entry - dung khi test hoac muon ep goi lai AI."""
    res = _get_collection().delete_one({"profile_hash": profile_hash})
    return res.deleted_count > 0