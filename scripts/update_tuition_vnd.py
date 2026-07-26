# -*- coding: utf-8 -*-
"""
scripts/update_tuition_vnd.py - Issue 2.14

Them field tuition_vnd cho 22 truong. Ly do: tuition_per_year dang luu 4 loai
tien (CNY/JPY/GBP/KRW) nen khong ve chung 1 chart duoc (ARCHITECTURE.md
muc 5.2.1). Quy doi tinh san o day, KHONG quy doi o tang view.

Chay thu (khong ghi gi):   python3 scripts/update_tuition_vnd.py
Ghi that:                  python3 scripts/update_tuition_vnd.py --apply

Script dung update_one, KHONG chay lai seed.py - data that da co tren Atlas.
Chay lai nhieu lan cho ket qua giong nhau (idempotent).
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config  # noqa: E402
from pymongo import MongoClient  # noqa: E402

SEED_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "seed_data.json")

# Ty gia CHOT ngay 25/07/2026, nguon webgia.com - xem NGUON_DU_LIEU.md.
# Sua o day thi phai sua ca NGUON_DU_LIEU.md cho khop.
TY_GIA_VND = {
    "GBP": 34983.66,
    "JPY": 160.31,
    "CNY": 3899.0,
    "KRW": 17.96,
}


def quy_doi(tuition, currency):
    """Doi hoc phi sang VND, lam tron den 1.000 dong."""
    if currency not in TY_GIA_VND:
        return None
    return round(tuition * TY_GIA_VND[currency] / 1000) * 1000


def main():
    apply_that = "--apply" in sys.argv

    if any(v <= 0 for v in TY_GIA_VND.values()):
        print("[loi] Chua dien ty gia trong TY_GIA_VND. Xem NGUON_DU_LIEU.md.")
        sys.exit(1)

    with open(SEED_PATH, encoding="utf-8") as f:
        data = json.load(f)

    loi = []
    for u in data:
        vnd = quy_doi(u["tuition_per_year"], u["currency"])
        if vnd is None:
            loi.append(f"{u['name']}: khong co ty gia cho '{u['currency']}'")
            continue
        u["tuition_vnd"] = vnd
        print(f"{vnd / 1_000_000:9.1f} trieu | {u['name'][:40]:40} "
              f"| goc: {u['tuition_per_year']:>10,} {u['currency']}")

    if loi:
        print("\n[loi] Dung lai, chua ghi gi:")
        for e in loi:
            print(f"  - {e}")
        sys.exit(1)

    print(f"\nTong: {len(data)} truong.")

    if not apply_that:
        print("Day la chay thu. Kiem tra so lieu tren, thay dung thi chay lai "
              "voi --apply de ghi vao seed_data.json va MongoDB.")
        return

    # 1. Ghi lai seed_data.json cho khop voi Atlas
    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[ok] Da cap nhat data/seed_data.json")

    # 2. Cap nhat tung document tren Atlas
    if not config.has_mongo():
        print(f"[canh bao] {config.mongo_hint()}")
        print("Da ghi file JSON nhung CHUA cap nhat Mongo.")
        sys.exit(1)

    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=10000)
    col = client[config.DB_NAME][config.COLLECTION_UNIVERSITIES]

    da_sua = 0
    khong_thay = []
    for u in data:
        kq = col.update_one({"id": u["id"]}, {"$set": {"tuition_vnd": u["tuition_vnd"]}})
        if kq.matched_count == 0:
            khong_thay.append(u["id"])
        else:
            da_sua += 1

    print(f"[ok] Da cap nhat {da_sua}/{len(data)} document tren Mongo")
    if khong_thay:
        print(f"[canh bao] Khong tim thay id tren Mongo: {khong_thay}")
    client.close()


if __name__ == "__main__":
    main()