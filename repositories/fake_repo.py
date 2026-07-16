import uuid

class FakeRepo:
    def __init__(self):
        # Khởi tạo dữ liệu giả lập (mock data) với 8 trường đại học mẫu[cite: 1]
        self._db = [
            {
                "id": "1",
                "name": "Massachusetts Institute of Technology (MIT)",
                "country": "USA",
                "gpa": 3.9,
                "ielts": 7.5,
                "tuition": 55000,
                "description": "Viện công nghệ hàng đầu, mạnh về khoa học và kỹ thuật."
            },
            {
                "id": "2",
                "name": "Stanford University",
                "country": "USA",
                "gpa": 3.9,
                "ielts": 7.5,
                "tuition": 56000,
                "description": "Nằm tại Thung lũng Silicon, thế mạnh vượt trội về Khoa học Máy tính."
            },
            {
                "id": "3",
                "name": "University of Oxford",
                "country": "UK",
                "gpa": 3.8,
                "ielts": 7.5,
                "tuition": 35000,
                "description": "Đại học lâu đời nhất thế giới nói tiếng Anh, môi trường học thuật danh giá."
            },
            {
                "id": "4",
                "name": "University of Cambridge",
                "country": "UK",
                "gpa": 3.8,
                "ielts": 7.5,
                "tuition": 34000,
                "description": "Nổi tiếng với các chương trình khoa học tự nhiên và toán học."
            },
            {
                "id": "5",
                "name": "University of Toronto",
                "country": "Canada",
                "gpa": 3.7,
                "ielts": 6.5,
                "tuition": 45000,
                "description": "Trường top đầu Canada với cơ sở vật chất hiện đại."
            },
            {
                "id": "6",
                "name": "University of British Columbia",
                "country": "Canada",
                "gpa": 3.6,
                "ielts": 6.5,
                "tuition": 42000,
                "description": "Trọng tâm vào nghiên cứu và phát triển bền vững."
            },
            {
                "id": "7",
                "name": "National University of Singapore (NUS)",
                "country": "Singapore",
                "gpa": 3.8,
                "ielts": 7.0,
                "tuition": 25000,
                "description": "Đại học số 1 Châu Á, kết nối công nghệ và kinh doanh toàn cầu."
            },
            {
                "id": "8",
                "name": "Nanyang Technological University (NTU)",
                "country": "Singapore",
                "gpa": 3.7,
                "ielts": 6.5,
                "tuition": 24000,
                "description": "Thế mạnh về kỹ thuật và các phòng lab nghiên cứu tiên tiến."
            }
        ]

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