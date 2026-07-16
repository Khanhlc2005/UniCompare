# -*- coding: utf-8 -*-
"""
scripts/seed.py - Issue 2.2 (PLAN.md tuan 2): "seed_data.json 20-30 truong +
scripts/seed.py (validate truoc khi nap)".

Chay: python3 scripts/seed.py
Can .env voi MONGO_URI (xem .env.example / config.py). Se validate
data/seed_data.json truoc, CHI nap khi validate sach - dung script rieng
validate_data.py de tai su dung logic kiem tra.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config  # noqa: E402
from scripts.validate_data import validate_university  # noqa: E402

SEED_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "seed_data.json")


def load_and_validate() -> list[dict]:
    with open(SEED_PATH, encoding="utf-8") as f:
        data = json.load(f)

    errors = []
    for i, u in enumerate(data, start=1):
        errors.extend(validate_university(u, i))

    if errors:
        print(f"[loi] {len(errors)} loi validate - DUNG nap, sua data/seed_data.json truoc:\n")
        for e in errors:
            print(f"  - {e}")
        print(
            "\nGoi y: nhieu loi 'ranking'/'gpa_min' thieu la do du lieu chua duoc"
            " nhom xac minh (xem NGUON_DU_LIEU.md, cot 'verified'). Hay dien so"
            " lieu that truoc khi nap vao Mongo - KHONG dien dai bang so bia."
        )
        sys.exit(1)

    print(f"[ok] {len(data)} truong hop le, tien hanh nap vao MongoDB...")
    return data


def seed_mongo(data: list[dict]) -> None:
    config.warn_if_missing_mongo_uri()
    if not config.has_mongo_uri():
        print("[dung] Khong the nap vi thieu MONGO_URI. Xem huong dan phia tren.")
        sys.exit(1)

    from pymongo import MongoClient

    client = MongoClient(config.MONGO_URI)
    db = client[config.DB_NAME]
    coll = db[config.COLLECTION_UNIVERSITIES]

    inserted, updated = 0, 0
    for u in data:
        doc = dict(u)
        result = coll.update_one({"id": doc["id"]}, {"$set": doc}, upsert=True)
        if result.upserted_id is not None:
            inserted += 1
        elif result.modified_count > 0:
            updated += 1

    total = coll.count_documents({})
    print(
        f"[xong] {inserted} truong moi, {updated} truong duoc cap nhat. "
        f"Collection '{config.COLLECTION_UNIVERSITIES}' hien co {total} truong."
    )
    client.close()


if __name__ == "__main__":
    universities = load_and_validate()
    seed_mongo(universities)
