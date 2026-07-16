# -*- coding: utf-8 -*-
"""
config.py - doc cau hinh tu .env (python-dotenv), theo ARCHITECTURE.md muc 7:
"config.py doc .env qua python-dotenv; thieu MONGO_URI -> thong bao ro va goi
y dung fake_repo, khong crash kho hieu."
"""
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "").strip()
API_KEY = os.getenv("API_KEY", "").strip()

DB_NAME = os.getenv("MONGO_DB_NAME", "unicompare").strip()
COLLECTION_UNIVERSITIES = "universities"
COLLECTION_AI_CACHE = "ai_cache"
COLLECTION_WATCHLIST = "watchlist"


def has_mongo() -> bool:
    return bool(MONGO_URI)


def mongo_hint() -> str:
    """Goi y khi thieu MONGO_URI, dung chung cho canh bao va thong bao loi."""
    return (
        "Khong tim thay MONGO_URI trong .env.\n"
        "  -> Neu ban dang phat trien UI/logic, hay dung repositories.fake_repo.FakeRepo\n"
        "     thay vi mongo_repo de khong can ket noi Mongo that.\n"
        "  -> Neu ban muon nap du lieu that, tao file .env (xem .env.example) va dien:\n"
        "       MONGO_URI=mongodb://localhost:27017\n"
        "       API_KEY=...\n"
    )


def warn_if_missing_mongo_uri() -> None:
    """Goi o dau main.py / seed.py de bao ro rang thay vi crash kho hieu."""
    if not has_mongo():
        print(f"[canh bao] {mongo_hint()}")
