"""university_service.py — Logic nghiệp vụ cho Tìm kiếm & lọc (Issue 1.4, 2.6).

Nguyên tắc (ARCHITECTURE.md mục 3):
- `country` đẩy xuống repo.search() vì repo đã hỗ trợ sẵn.
- `keyword` tự xử lý lại ở đây (thay vì dùng repo.search(keyword=...)) để hỗ trợ
  gõ không dấu vẫn ra kết quả có dấu (repo.search() gốc chỉ lower(), không bỏ dấu).
- Các bộ lọc mở rộng (học phí, IELTS) xử lý hoàn toàn ở service layer, trên kết
  quả trả về từ repo — KHÔNG đổi chữ ký repo.search() (đúng rủi ro đã ghi ở mục 10).

Luu y schema (xem CLAUDE.md "Known schema mismatch"): fake_repo.py hien dung
field cu "tuition"/"ielts", con schema chuan trong ARCHITECTURE.md/seed_data.json
dung "tuition_per_year"/"ielts_min". lay_hoc_phi()/lay_ielts() ben duoi doc ca
2 ten field de tranh loi am tham loc sai khi doi sang mongo_repo/du lieu that
(truoc day .get("tuition", 0) mac dinh ve 0 -> record thieu field luon qua
duoc filter <=, coi nhu filter khong co tac dung gi).
"""
import unicodedata


def lay_hoc_phi(uni: dict) -> float | None:
    """Doc hoc phi/nam, uu tien field chuan tuition_per_year, fallback ve
    tuition (schema cu cua fake_repo). Tra None neu khong co field nao."""
    hp = uni.get("tuition_per_year", uni.get("tuition"))
    return hp if isinstance(hp, (int, float)) else None


def lay_ielts(uni: dict) -> float | None:
    """Doc IELTS toi thieu, uu tien field chuan ielts_min, fallback ve ielts."""
    ielts = uni.get("ielts_min", uni.get("ielts"))
    return ielts if isinstance(ielts, (int, float)) else None


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
        # truong thieu du lieu hoc phi thi loai ra, khong am tham cho qua filter
        results = [
            uni for uni in results
            if (hp := lay_hoc_phi(uni)) is not None and hp <= tuition_max
        ]

    if ielts_max is not None:
        results = [
            uni for uni in results
            if (ielts := lay_ielts(uni)) is not None and ielts <= ielts_max
        ]

    return results


def get_countries(repo) -> list[str]:
    """Lấy danh sách quốc gia duy nhất từ dữ liệu hiện có, dùng để dựng pill filter.

    Sắp xếp theo alphabet để hiển thị pill ổn định (không nhảy vị trí giữa các lần load).
    """
    countries = {uni.get("country", "") for uni in repo.get_all() if uni.get("country")}
    return sorted(countries)
