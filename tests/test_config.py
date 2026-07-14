"""Test cho config.py (Issue 1.0a).

Lưu ý: CI (.github/workflows/test.yml) chạy pytest khi thấy thư mục tests/.
File này đảm bảo tests/ không rỗng (pytest rỗng trả exit code 5 → CI đỏ)
và xác nhận config không crash khi thiếu .env — đúng ARCHITECTURE.md §7.
"""

import config


def test_config_khong_crash_khi_thieu_env():
    # Trên CI không có .env — import config phải chạy được, giá trị là chuỗi.
    assert isinstance(config.MONGO_URI, str)
    assert isinstance(config.API_KEY, str)


def test_mongo_hint_goi_y_fake_repo():
    assert "fake_repo" in config.mongo_hint()


def test_has_mongo_theo_gia_tri_uri():
    # has_mongo() phản ánh đúng trạng thái MONGO_URI hiện tại.
    assert config.has_mongo() == bool(config.MONGO_URI.strip())
