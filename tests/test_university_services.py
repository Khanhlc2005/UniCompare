"""Test cho university_service.search() (Issue 1.4).

Bám acceptance criteria trong PLAN.md: "Test pass các case: rỗng, không match,
có dấu/không dấu".
"""
import pytest

from repositories.fake_repo import FakeRepo
from services import university_service


@pytest.fixture
def repo():
    return FakeRepo()


class _RepoCoDau:
    """Repo giả lập tối thiểu, chỉ để test riêng khả năng bỏ dấu khi so khớp."""

    def __init__(self, data):
        self._data = data

    def get_all(self):
        return [d.copy() for d in self._data]

    def search(self, keyword: str = "", country: str | None = None):
        results = []
        for uni in self._data:
            match_country = country.lower() == uni["country"].lower() if country else True
            if match_country:
                results.append(uni.copy())
        return results


# ─── Case: rỗng ────────────────────────────────────────────────
def test_keyword_rong_tra_ve_tat_ca(repo):
    ket_qua = university_service.search(repo, keyword="")
    assert len(ket_qua) == len(repo.get_all())


def test_khong_truyen_dieu_kien_nao_tra_ve_tat_ca(repo):
    ket_qua = university_service.search(repo)
    assert len(ket_qua) == len(repo.get_all())


# ─── Case: không match ─────────────────────────────────────────
def test_keyword_khong_ton_tai_tra_ve_rong(repo):
    ket_qua = university_service.search(repo, keyword="truong khong ton tai xyz123")
    assert ket_qua == []


def test_country_khong_ton_tai_tra_ve_rong(repo):
    ket_qua = university_service.search(repo, country="Atlantis")
    assert ket_qua == []


# ─── Case: có dấu / không dấu ──────────────────────────────────
def test_go_khong_dau_van_khop_ten_co_dau():
    repo_vn = _RepoCoDau([
        {"id": "1", "name": "Đại học Bách Khoa Hà Nội", "country": "Vietnam",
         "tuition": 2000, "ielts": 6.0},
    ])
    ket_qua = university_service.search(repo_vn, keyword="dai hoc bach khoa")
    assert len(ket_qua) == 1


def test_go_co_dau_van_khop_binh_thuong():
    repo_vn = _RepoCoDau([
        {"id": "1", "name": "Đại học Bách Khoa Hà Nội", "country": "Vietnam",
         "tuition": 2000, "ielts": 6.0},
    ])
    ket_qua = university_service.search(repo_vn, keyword="Bách Khoa")
    assert len(ket_qua) == 1


def test_go_khong_phan_biet_hoa_thuong(repo):
    ket_qua = university_service.search(repo, keyword="oxford")
    assert len(ket_qua) == 1
    assert ket_qua[0]["name"] == "University of Oxford"# ─── Lọc quốc gia / học phí / IELTS (đẩy thêm cho Issue 2.6) ───
def test_loc_theo_quoc_gia(repo):
    # data thuc trong seed_data.json ghi day du "United Kingdom", khong phai "UK"
    ket_qua = university_service.search(repo, country="United Kingdom")
    assert len(ket_qua) == 6
    assert all(uni["country"] == "United Kingdom" for uni in ket_qua)


def test_loc_theo_hoc_phi_toi_da(repo):
    ket_qua = university_service.search(repo, tuition_max=30000)
    # seed_data.json dung field tuition_per_year -> phai doc qua lay_hoc_phi()
    assert all(university_service.lay_hoc_phi(uni) <= 30000 for uni in ket_qua)
    assert len(ket_qua) > 0


def test_loc_theo_ielts_toi_da(repo):
    ket_qua = university_service.search(repo, ielts_max=6.5)
    assert all(university_service.lay_ielts(uni) <= 6.5 for uni in ket_qua)
    assert len(ket_qua) > 0


def test_ket_hop_ca_3_dieu_kien_pill_cung_luc(repo):
    ket_qua = university_service.search(
        repo, country="United Kingdom", tuition_max=40000, ielts_max=7.5
    )
    assert all(
        uni["country"] == "United Kingdom"
        and university_service.lay_hoc_phi(uni) <= 40000
        and university_service.lay_ielts(uni) <= 7.5
        for uni in ket_qua
    )
    assert len(ket_qua) > 0


def test_get_countries_tra_ve_danh_sach_khong_trung(repo):
    countries = university_service.get_countries(repo)
    assert len(countries) == len(set(countries))
    # seed_data.json hien tai khong co truong nao o USA, dung 1 quoc gia co that
    assert "Japan" in countries


# ─── Fallback schema chuan (tuition_per_year/ielts_min) - tranh loi am tham
# loc sai khi doi sang mongo_repo/du lieu that (xem CLAUDE.md schema mismatch) ─
class _RepoSchemaChuan:
    """Repo gia lap tra du lieu theo schema ARCHITECTURE.md/seed_data.json,
    khong con field tuition/ielts cu."""

    def __init__(self, data):
        self._data = data

    def get_all(self):
        return [d.copy() for d in self._data]

    def search(self, keyword: str = "", country: str | None = None):
        results = []
        for uni in self._data:
            match_country = country.lower() == uni["country"].lower() if country else True
            if match_country:
                results.append(uni.copy())
        return results


def test_loc_hoc_phi_theo_schema_chuan_tuition_per_year():
    repo_chuan = _RepoSchemaChuan([
        {"id": "1", "name": "A", "country": "Japan", "tuition_per_year": 10000},
        {"id": "2", "name": "B", "country": "Japan", "tuition_per_year": 50000},
    ])
    ket_qua = university_service.search(repo_chuan, tuition_max=20000)
    assert [uni["id"] for uni in ket_qua] == ["1"]


def test_loc_ielts_theo_schema_chuan_ielts_min():
    repo_chuan = _RepoSchemaChuan([
        {"id": "1", "name": "A", "country": "Japan", "ielts_min": 6.0},
        {"id": "2", "name": "B", "country": "Japan", "ielts_min": 7.5},
    ])
    ket_qua = university_service.search(repo_chuan, ielts_max=6.5)
    assert [uni["id"] for uni in ket_qua] == ["1"]


def test_loc_hoc_phi_loai_truong_thieu_du_lieu_thay_vi_am_tham_cho_qua():
    """Truoc fix: uni.get("tuition", 0) mac dinh 0 -> record thieu field
    van luon qua duoc filter <=. Gio phai loai ra vi khong xac dinh duoc."""
    repo_chuan = _RepoSchemaChuan([
        {"id": "1", "name": "A", "country": "Japan"},
    ])
    ket_qua = university_service.search(repo_chuan, tuition_max=100)
    assert ket_qua == []
# ─── Phân trang cho SearchView (Issue 2.6) ──────────────────────
def test_phan_trang_it_hon_1_trang_tra_ve_tat_ca():
    ket_qua, trang, tong = university_service.phan_trang(list(range(5)), page=1, page_size=9)
    assert ket_qua == list(range(5))
    assert trang == tong == 1


def test_phan_trang_cat_dung_trang_2():
    du_lieu = list(range(20))
    ket_qua, trang, tong = university_service.phan_trang(du_lieu, page=2, page_size=9)
    assert ket_qua == du_lieu[9:18]
    assert (trang, tong) == (2, 3)


def test_phan_trang_trang_cuoi_thieu_phan_tu():
    du_lieu = list(range(20))
    ket_qua, _, _ = university_service.phan_trang(du_lieu, page=3, page_size=9)
    assert ket_qua == du_lieu[18:20]


def test_phan_trang_page_vuot_qua_tong_trang_bi_clamp_ve_cuoi():
    du_lieu = list(range(20))
    ket_qua, trang, tong = university_service.phan_trang(du_lieu, page=99, page_size=9)
    assert (trang, tong) == (3, 3)
    assert ket_qua == du_lieu[18:20]


def test_phan_trang_ket_qua_rong():
    ket_qua, trang, tong = university_service.phan_trang([], page=1, page_size=9)
    assert ket_qua == []
    assert trang == tong == 1