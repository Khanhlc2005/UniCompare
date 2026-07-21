# compare_service.py - Issue 1.6
# State "dang chon de so sanh", dung chung cho Home/Search/Watchlist/Detail
# (ARCHITECTURE.md muc 5.2) - toi da 5 truong. Cung la list module-level nhu
# watchlist_service, khong bay them state manager rieng.

MAX_COMPARE = 5
_compare_ids: list[str] = []


def get_compare_ids() -> list[str]:
    return _compare_ids


def toggle_compare(university_id: str) -> tuple[bool, str]:
    """Tra ve (thanh_cong, thong_bao) de UI hien canh bao khi bi chan."""
    if university_id in _compare_ids:
        _compare_ids.remove(university_id)
        return True, ""
    if len(_compare_ids) >= MAX_COMPARE:
        return False, f"Chi duoc chon toi da {MAX_COMPARE} truong de so sanh"
    _compare_ids.append(university_id)
    return True, ""


def clear_compare() -> None:
    _compare_ids.clear()


# Issue 2.8: xac dinh tieu chi "tot nhat" de UI to mau bootstyle="success"
# (ARCHITECTURE.md muc 5.3). Doc field uu tien schema chuan (ranking,
# tuition_per_year, gpa_min, ielts_min - ARCHITECTURE.md muc 4), fallback ve
# field cu cua fake_repo (tuition, gpa, ielts - xem CLAUDE.md "Known schema
# mismatch"), giong pattern lay_hoc_phi/lay_ielts trong university_service.py.
#
# Chieu "tot hon" ca 4 tieu chi deu la CANG THAP CANG TOT:
# - ranking: so hang cang nho cang tot (hang 1 tot hon hang 50)
# - tuition: hoc phi cang re cang tot
# - gpa/ielts: day la NGUONG YEU CAU TOI THIEU de dau vao, khong phai diem
#   dat duoc, nen yeu cau cang thap cang de trung tuyen hon = tot hon
CAC_TIEU_CHI_SO = ["ranking", "tuition", "gpa", "ielts"]


def doc_gia_tri_tieu_chi(uni: dict, field: str) -> float | None:
    """Doc gia tri so cua 1 tieu chi so sanh, uu tien field schema chuan,
    fallback field schema cu fake_repo. Tra None neu truong thieu du lieu
    (khong cho truong thieu field am tham thanh "tot nhat"). Public de
    compare_page.py dung chung khi hien thi gia tri trong bang, khoi lap
    lai bang alias field (mot nguon duy nhat cho ca so sanh lan hien thi)."""
    if field == "tuition":
        gia_tri = uni.get("tuition_per_year", uni.get("tuition"))
    elif field == "ielts":
        gia_tri = uni.get("ielts_min", uni.get("ielts"))
    elif field == "gpa":
        gia_tri = uni.get("gpa_min", uni.get("gpa"))
    else:
        gia_tri = uni.get(field)
    return gia_tri if isinstance(gia_tri, (int, float)) else None


def xac_dinh_tot_nhat(data: list[dict]) -> dict[str, set[str]]:
    """Voi danh sach truong dang so sanh (moi dict co "id"), tra ve id cac
    truong dat gia tri tot nhat o tung tieu chi trong CAC_TIEU_CHI_SO.

    Bang diem nhau o 1 tieu chi thi highlight ca hai (khong chon dai 1 truong
    ngau nhien) - tra ve set nen tu dong gom het id bang gia tri nho nhat.

    Return: {"tuition": {"id1", "id3"}, "ranking": {"id2"}, ...}. Tieu chi
    khong truong nao co du lieu thi tra set() rong (UI khong highlight gi).
    """
    ket_qua: dict[str, set[str]] = {}
    for field in CAC_TIEU_CHI_SO:
        gia_tri_theo_id = {
            uni["id"]: gt
            for uni in data
            if (gt := doc_gia_tri_tieu_chi(uni, field)) is not None
        }
        if not gia_tri_theo_id:
            ket_qua[field] = set()
            continue
        tot_nhat = min(gia_tri_theo_id.values())
        ket_qua[field] = {
            uid for uid, gt in gia_tri_theo_id.items() if gt == tot_nhat
        }
    return ket_qua
