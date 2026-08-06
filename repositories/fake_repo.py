import uuid
import json
import os
import uuid

_SEED_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "seed_data.json"
)

class FakeRepo:
    def __init__(self):
        # Khởi tạo dữ liệu giả lập (mock data) với 8 trường đại học mẫu[cite: 1]
        try:
            with open(_SEED_PATH, encoding="utf-8") as f:
                self._db = json.load(f)
        except (OSError, json.JSONDecodeError) as err:
            print(f"[FakeRepo] Khong doc duoc {_SEED_PATH}: {err}")
            self._db = []

    # Các phương thức tuân thủ đúng Hợp đồng giao tiếp (Repository interface)[cite: 1]
    
    def get_all(self) -> list[dict]:
        """Trả về toàn bộ danh sách trường[cite: 1]."""
        return [uni.copy() for uni in self._db]

    def get_by_id(self, id: str) -> dict | None:
        """Lấy thông tin chi tiết một trường theo ID[cite: 1]."""
        for uni in self._db:
            if uni["id"] == id:
                return uni.copy()
        return None

    def search(self, keyword: str = "", country: str = None) -> list[dict]:
        """Tìm kiếm theo từ khóa và lọc theo quốc gia[cite: 1]."""
        results = []
        for uni in self._db:
            match_keyword = keyword.lower() in uni["name"].lower() if keyword else True
            match_country = country.lower() == uni["country"].lower() if country else True
            
            if match_keyword and match_country:
                results.append(uni.copy())
        return results

    def add(self, data: dict) -> str:
        """Thêm dữ liệu mới (dành cho màn Admin)[cite: 1]."""
        new_id = str(uuid.uuid4())
        new_uni = data.copy()
        new_uni["id"] = new_id
        self._db.append(new_uni)
        return new_id

    def update(self, id: str, data: dict) -> bool:
        """Cập nhật dữ liệu trường[cite: 1]."""
        for i, uni in enumerate(self._db):
            if uni["id"] == id:
                updated_uni = uni.copy()
                updated_uni.update(data)
                updated_uni["id"] = id 
                self._db[i] = updated_uni
                return True
        return False

    def delete(self, id: str) -> bool:
        """Xóa dữ liệu trường[cite: 1]."""
        initial_len = len(self._db)
        self._db = [uni for uni in self._db if uni["id"] != id]
        return len(self._db) < initial_len