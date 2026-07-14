"""Cấu hình ứng dụng UniCompare.

Đọc biến môi trường từ file `.env` (xem `.env.example`).
Theo ARCHITECTURE.md §7: thiếu MONGO_URI thì KHÔNG crash khó hiểu —
in thông báo rõ ràng và gợi ý dùng fake_repo.
"""

import os

from dotenv import load_dotenv

load_dotenv()

MONGO_URI: str = os.getenv("MONGO_URI", "")
API_KEY: str = os.getenv("API_KEY", "")


def has_mongo() -> bool:
    """True nếu đã cấu hình MONGO_URI (dùng được mongo_repo)."""
    return bool(MONGO_URI.strip())


def has_ai() -> bool:
    """True nếu đã cấu hình API_KEY (dùng được L2 AI explanation)."""
    return bool(API_KEY.strip())


def mongo_hint() -> str:
    """Thông báo hướng dẫn khi thiếu MONGO_URI."""
    return (
        "Chưa cấu hình MONGO_URI trong file .env — app sẽ chạy với fake_repo "
        "(8 trường mẫu). Để dùng dữ liệu thật: copy .env.example thành .env "
        "và điền MONGO_URI (xem ARCHITECTURE.md §1)."
    )
