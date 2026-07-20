"""university_service.py — Logic nghiệp vụ cho Tìm kiếm & lọc (Issue 1.4, 2.6).

Nguyên tắc (ARCHITECTURE.md mục 3):
- `country` đẩy xuống repo.search() vì repo đã hỗ trợ sẵn.
- `keyword` tự xử lý lại ở đây (thay vì dùng repo.search(keyword=...)) để hỗ trợ
  gõ không dấu vẫn ra kết quả có dấu (repo.search() gốc chỉ lower(), không bỏ dấu).
- Các bộ lọc mở rộng (học phí, IELTS) xử lý hoàn toàn ở service layer, trên kết
  quả trả về từ repo — KHÔNG đổi chữ ký repo.search() (đúng rủi ro đã ghi ở mục 10).
"""
import unicodedata


def _bo_dau(text: str) -> str:
    """Chuyển chuỗi về dạng không dấu + chữ thường, dùng để so khớp gõ tắt.

    VD: "Đại Học Bách Khoa" -> "dai hoc bach khoa"
    """
    if not text:
        return ""
    # "Đ"/"đ" không phải ký tự tổ hợp (combining) nên NFKD không tự tách được,
    # phải thay tay trước khi normalize.
    text = text.replace("Đ", "D").replace("đ", "d")
    nfkd = unicodedata.normalize("NFKD", text)
    khong_dau = "".join(c for c in nfkd if not unicodedata.combining(c))
    return khong_dau.lower()


def search(
    repo,
    keyword: str = "",
    country: str | None = None,
    tuition_max: float | None = None,
    ielts_max: float | None = None,
) -> list[dict]:
    """Tìm kiếm + lọc danh sách trường đại học.

    Args:
        repo: đối tượng tuân thủ UniversityRepo (fake_repo hoặc mongo_repo).
        keyword: từ khóa tìm theo tên trường — không phân biệt hoa/thường,
                 có dấu/không dấu đều khớp.
        country: lọc chính xác theo quốc gia (không phân biệt hoa/thường).
        tuition_max: chỉ lấy trường có học phí <= giá trị này (USD/năm).
        ielts_max: chỉ lấy trường có yêu cầu IELTS <= giá trị này
                   (dùng khi người dùng muốn tìm trường "dễ vào" hơn theo IELTS).

    Returns:
        Danh sách dict trường thỏa tất cả điều kiện đã truyền vào (kết hợp AND).
    """
    # country lọc ở repo (đúng interface); keyword để trống ở đây, tự lọc bên dưới
    results = repo.search(keyword="", country=country)

    if keyword and keyword.strip():
        kw_norm = _bo_dau(keyword.strip())
        results = [
            uni for uni in results
            if kw_norm in _bo_dau(uni.get("name", ""))
        ]

    if tuition_max is not None:
        results = [uni for uni in results if uni.get("tuition", 0) <= tuition_max]

    if ielts_max is not None:
        results = [uni for uni in results if uni.get("ielts", 0) <= ielts_max]

    return results


def get_countries(repo) -> list[str]:
    """Lấy danh sách quốc gia duy nhất từ dữ liệu hiện có, dùng để dựng pill filter.

    Sắp xếp theo alphabet để hiển thị pill ổn định (không nhảy vị trí giữa các lần load).
    """
    countries = {uni.get("country", "") for uni in repo.get_all() if uni.get("country")}
    return sorted(countries)
