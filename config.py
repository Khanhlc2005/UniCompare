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
API_KEY = os.getenv("API_KEY", os.getenv("GEMINI_API_KEY", "")).strip()

DB_NAME = os.getenv("MONGO_DB_NAME", "unicompare").strip()
COLLECTION_UNIVERSITIES = "universities"
COLLECTION_AI_CACHE = "ai_cache"
COLLECTION_WATCHLIST = "watchlist"


def has_mongo() -> bool:
    return bool(MONGO_URI)


def has_api_key() -> bool:
    return bool(API_KEY)


def mongo_hint() -> str:
    """Gợi ý khi thiếu MONGO_URI / API_KEY."""
    return (
        "Không tìm thấy MONGO_URI hoặc API_KEY trong .env.\n"
        "  -> Ứng dụng vẫn hoạt động bình thường với fake_repo (FakeRepo) và L1 Rule Engine.\n"
        "  -> Để dùng tính năng L2 AI Explanation (miễn phí), tạo file .env và điền:\n"
        "       MONGO_URI=mongodb://localhost:27017\n"
        "       GEMINI_API_KEY=AIzaSy... (Lấy free tại https://aistudio.google.com/app/apikey)\n"
    )


def warn_if_missing_mongo_uri() -> None:
    """Goi o dau main.py / seed.py de bao ro rang thay vi crash kho hieu."""
    if not has_mongo():
        print(f"[canh bao] {mongo_hint()}")
