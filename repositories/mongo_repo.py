"""MongoDB repository cho dự án UniCompare.

Biến môi trường cần có trong file .env:
    MONGO_URI=mongodb+srv://<username>:<password>@<cluster-url>/?retryWrites=true&w=majority

Biến tùy chọn:
    MONGO_DB_NAME=unicompare
    MONGO_COLLECTION=universities

Cài thư viện:
    pip install pymongo python-dotenv

Chạy kiểm tra thủ công:
    python mongo_repo.py
"""

from __future__ import annotations

import os
from typing import Any

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConfigurationError, PyMongoError, ServerSelectionTimeoutError

load_dotenv()

Document = dict[str, Any]


class MongoRepositoryError(RuntimeError):
    """Lỗi nghiệp vụ chung của Mongo repository."""


class MongoUniversityRepository:
    """Repository thao tác collection ``universities`` trên MongoDB Atlas.

    Kết nối được khởi tạo theo kiểu lazy: chỉ kết nối khi một hàm truy vấn được gọi.
    Điều này giúp import file từ App Shell mà không làm ứng dụng lỗi ngay lập tức.
    """

    def __init__(
        self,
        uri: str | None = None,
        db_name: str | None = None,
        collection_name: str | None = None,
        timeout_ms: int = 8_000,
    ) -> None:
        self.uri = uri or os.getenv("MONGO_URI", "").strip()
        self.db_name = db_name or os.getenv("MONGO_DB_NAME", "unicompare").strip()
        self.collection_name = collection_name or os.getenv(
            "MONGO_COLLECTION", "universities"
        ).strip()
        self.timeout_ms = timeout_ms

        self._client: MongoClient | None = None
        self._database: Database | None = None
        self._collection: Collection | None = None

    def _connect(self) -> Collection:
        """Kết nối Atlas và trả về collection đang sử dụng."""
        if self._collection is not None:
            return self._collection

        if not self.uri:
            raise MongoRepositoryError(
                "Thiếu MONGO_URI. Hãy tạo file .env và khai báo MONGO_URI trước khi chạy."
            )

        try:
            self._client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=self.timeout_ms,
                connectTimeoutMS=self.timeout_ms,
                socketTimeoutMS=self.timeout_ms,
                retryWrites=True,
            )
            # Ping để phát hiện sai URI, sai mật khẩu hoặc lỗi whitelist sớm.
            self._client.admin.command("ping")
            self._database = self._client[self.db_name]
            self._collection = self._database[self.collection_name]
            return self._collection
        except (ConfigurationError, ServerSelectionTimeoutError, PyMongoError) as exc:
            self.close()
            raise MongoRepositoryError(
                "Không thể kết nối MongoDB Atlas. Kiểm tra MONGO_URI, tài khoản "
                "Database User và Network Access/IP whitelist."
            ) from exc

    @staticmethod
    def _serialize(document: Document | None) -> Document | None:
        """Chuyển ObjectId thành chuỗi để UI/Tkinter dễ sử dụng."""
        if document is None:
            return None

        result = dict(document)
        if isinstance(result.get("_id"), ObjectId):
            result["_id"] = str(result["_id"])
        return result

    @staticmethod
    def _to_object_id(value: str) -> ObjectId | None:
        """Đổi chuỗi sang ObjectId; trả về None nếu chuỗi không hợp lệ."""
        try:
            return ObjectId(value)
        except Exception:
            return None

    def get_all(self) -> list[Document]:
        """Lấy toàn bộ trường đại học từ Atlas."""
        try:
            documents = self._connect().find({})
            return [self._serialize(doc) for doc in documents if doc is not None]
        except PyMongoError as exc:
            raise MongoRepositoryError("Không thể đọc danh sách trường từ MongoDB.") from exc

    def get_by_id(self, university_id: str) -> Document | None:
        """Tìm một trường theo Mongo ``_id`` hoặc trường ``id`` tùy chỉnh."""
        collection = self._connect()
        object_id = self._to_object_id(university_id)

        query: dict[str, Any]
        if object_id is not None:
            query = {"$or": [{"_id": object_id}, {"id": university_id}]}
        else:
            query = {"id": university_id}

        try:
            return self._serialize(collection.find_one(query))
        except PyMongoError as exc:
            raise MongoRepositoryError(
                f"Không thể tìm trường có id={university_id!r}."
            ) from exc

    def search(
        self,
        keyword: str = "",
        country: str | None = None,
    ) -> list[Document]:
        """Tìm trường theo từ khóa và/hoặc quốc gia.

        Từ khóa được dò không phân biệt hoa thường trong các trường phổ biến:
        ``name``, ``university_name``, ``country``, ``city`` và ``programs``.
        """
        filters: list[dict[str, Any]] = []

        keyword = keyword.strip()
        if keyword:
            regex = {"$regex": keyword, "$options": "i"}
            filters.append(
                {
                    "$or": [
                        {"name": regex},
                        {"university_name": regex},
                        {"country": regex},
                        {"city": regex},
                        {"programs": regex},
                    ]
                }
            )

        if country and country.strip():
            filters.append(
                {"country": {"$regex": f"^{country.strip()}$", "$options": "i"}}
            )

        query: dict[str, Any]
        if not filters:
            query = {}
        elif len(filters) == 1:
            query = filters[0]
        else:
            query = {"$and": filters}

        try:
            documents = self._connect().find(query)
            return [self._serialize(doc) for doc in documents if doc is not None]
        except PyMongoError as exc:
            raise MongoRepositoryError("Không thể tìm kiếm dữ liệu trường.") from exc

    def add(self, data: Document) -> str:
        """Thêm một trường mới và trả về id vừa tạo."""
        if not isinstance(data, dict) or not data:
            raise ValueError("data phải là dict và không được rỗng.")

        payload = dict(data)
        payload.pop("_id", None)

        try:
            result = self._connect().insert_one(payload)
            return str(result.inserted_id)
        except PyMongoError as exc:
            raise MongoRepositoryError("Không thể thêm trường vào MongoDB.") from exc

    def update(self, university_id: str, data: Document) -> bool:
        """Cập nhật một trường; trả về True khi có document khớp id."""
        if not isinstance(data, dict) or not data:
            raise ValueError("data cập nhật phải là dict và không được rỗng.")

        payload = dict(data)
        payload.pop("_id", None)

        object_id = self._to_object_id(university_id)
        query: dict[str, Any]
        if object_id is not None:
            query = {"$or": [{"_id": object_id}, {"id": university_id}]}
        else:
            query = {"id": university_id}

        try:
            result = self._connect().update_one(query, {"$set": payload})
            return result.matched_count > 0
        except PyMongoError as exc:
            raise MongoRepositoryError(
                f"Không thể cập nhật trường có id={university_id!r}."
            ) from exc

    def delete(self, university_id: str) -> bool:
        """Xóa một trường; trả về True khi đã xóa được document."""
        object_id = self._to_object_id(university_id)
        query: dict[str, Any]
        if object_id is not None:
            query = {"$or": [{"_id": object_id}, {"id": university_id}]}
        else:
            query = {"id": university_id}

        try:
            result = self._connect().delete_one(query)
            return result.deleted_count > 0
        except PyMongoError as exc:
            raise MongoRepositoryError(
                f"Không thể xóa trường có id={university_id!r}."
            ) from exc

    def close(self) -> None:
        """Đóng MongoClient an toàn."""
        if self._client is not None:
            self._client.close()
        self._client = None
        self._database = None
        self._collection = None

    def __enter__(self) -> "MongoUniversityRepository":
        self._connect()
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()


# Instance dùng chung cho App Shell/service layer.
repository = MongoUniversityRepository()


# Các hàm wrapper giữ đúng repository contract của tài liệu dự án.
def get_all() -> list[Document]:
    return repository.get_all()


def get_by_id(university_id: str) -> Document | None:
    return repository.get_by_id(university_id)


def search(keyword: str = "", country: str | None = None) -> list[Document]:
    return repository.search(keyword=keyword, country=country)


def add(data: Document) -> str:
    return repository.add(data)


def update(university_id: str, data: Document) -> bool:
    return repository.update(university_id, data)


def delete(university_id: str) -> bool:
    return repository.delete(university_id)


def _manual_test() -> None:
    """Kịch bản test thủ công theo Definition of Done.

    Chỉ đọc dữ liệu, không thêm/sửa/xóa document.
    """
    print("[TEST] Đang kết nối MongoDB Atlas...")
    try:
        universities = get_all()
        print(f"[PASS] Kết nối thành công. get_all() trả về {len(universities)} bản ghi.")

        if universities:
            print("[PASS] Dữ liệu mẫu đầu tiên:")
            print(universities[0])
        else:
            print(
                "[WARN] Kết nối thành công nhưng collection đang rỗng. "
                "Hãy kiểm tra tên database/collection hoặc nạp seed data."
            )
    except (MongoRepositoryError, ValueError) as exc:
        print(f"[FAIL] {exc}")
        raise SystemExit(1) from exc
    finally:
        repository.close()


if __name__ == "__main__":
    _manual_test()
