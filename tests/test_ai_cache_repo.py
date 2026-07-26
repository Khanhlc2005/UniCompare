"""
Test cho ai_cache_repo (Issue 2.5).

Test nay noi truc tiep vao Mongo Atlas that (dung MONGO_URI trong .env cua
tung nguoi) nen tren CI (chua co secret MONGO_URI) se tu skip, khong lam do
pipeline. Chay local: pytest tests/test_ai_cache_repo.py
(cung chay truc tiep duoc bang python tests/test_ai_cache_repo.py)
"""
import os
import sys

# them thu muc goc du an vao sys.path - can khi chay file nay truc tiep
# bang `python tests/test_ai_cache_repo.py` (luc do repositories/ khong
# nam trong sys.path mac dinh). Khong anh huong khi chay qua pytest.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()  # doc MONGO_URI tu .env truoc, khong thi skipif ben duoi luon la True

import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("MONGO_URI"),
    reason="Can MONGO_URI that de test ai_cache_repo (local .env), tam skip tren CI",
)

from repositories import ai_cache_repo


def test_save_and_get_cache_roundtrip():
    profile_hash = "test_hash_khong_ton_tai_xxx"

    # don dep truoc, phong khi lan chay truoc bi loi giua chung
    ai_cache_repo.clear_cache(profile_hash)
    assert ai_cache_repo.get_cached_result(profile_hash) is None

    fake_result = [
        {"university_id": "abc123", "score": 87, "explanation": "phu hop ve hoc phi va IELTS"}
    ]
    ai_cache_repo.save_result(profile_hash, fake_result)

    cached = ai_cache_repo.get_cached_result(profile_hash)
    assert cached == fake_result

    # goi lai save_result lan 2 phai ghi de, khong tao document moi
    fake_result_v2 = [{"university_id": "abc123", "score": 90, "explanation": "cap nhat lai"}]
    ai_cache_repo.save_result(profile_hash, fake_result_v2)
    assert ai_cache_repo.get_cached_result(profile_hash) == fake_result_v2

    # don dep sau khi test xong
    ai_cache_repo.clear_cache(profile_hash)
    assert ai_cache_repo.get_cached_result(profile_hash) is None


if __name__ == "__main__":
    # cho phep chay truc tiep file nay (VD nut Run trong IDE) de xem ket qua
    # ngay, khong bat buoc phai go lenh pytest
    if not os.getenv("MONGO_URI"):
        print("[SKIP] Khong tim thay MONGO_URI (.env) - bo qua test.")
    else:
        test_save_and_get_cache_roundtrip()
        print("[PASS] test_save_and_get_cache_roundtrip")