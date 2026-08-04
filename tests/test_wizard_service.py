# -*- coding: utf-8 -*-
"""Unit tests cho wizard_service.py (Issue 3.6)."""

import pytest

from services import recommend_service, wizard_service


def test_parse_gpa():
    # Valid GPA scale 4
    ok, val, _ = wizard_service.parse_gpa("3.5")
    assert ok and val == 3.5

    # Valid GPA scale 10 (converts to scale 4: 8.5 / 2.5 = 3.4)
    ok, val, _ = wizard_service.parse_gpa("8.5")
    assert ok and val == 3.4

    # GPA = 0 - bien duoi, van hop le (0.0 <= 0.0 <= 10.0)
    ok, val, _ = wizard_service.parse_gpa("0")
    assert ok and val == 0.0

    # Invalid GPA - am
    ok, val, msg = wizard_service.parse_gpa("-1.0")
    assert not ok and "0.0 đến 10.0" in msg

    # Invalid GPA - vuot thang toi da
    ok, val, msg = wizard_service.parse_gpa("12.0")
    assert not ok and "0.0 đến 10.0" in msg

    # Invalid GPA - khong phai so
    ok, val, msg = wizard_service.parse_gpa("abc")
    assert not ok and "con số" in msg

    # Invalid GPA - bo trong
    ok, val, msg = wizard_service.parse_gpa("")
    assert not ok and val is None


def test_parse_ielts():
    # Valid IELTS
    ok, val, _ = wizard_service.parse_ielts("6.5")
    assert ok and val == 6.5

    # No IELTS / 0 - duoc phep de trong (chon "chua co chung chi")
    ok, val, _ = wizard_service.parse_ielts("chưa có")
    assert ok and val == 0.0

    ok, val, _ = wizard_service.parse_ielts("0")
    assert ok and val == 0.0

    ok, val, _ = wizard_service.parse_ielts("")
    assert ok and val == 0.0

    # Invalid IELTS - am
    ok, val, msg = wizard_service.parse_ielts("-1.0")
    assert not ok and "0.0 đến 9.0" in msg

    # Invalid IELTS - vuot thang toi da
    ok, val, msg = wizard_service.parse_ielts("10.0")
    assert not ok and "0.0 đến 9.0" in msg

    # Invalid IELTS - khong phai so (khac voi cac tu khoa "chua co" duoc chap nhan o tren)
    ok, val, msg = wizard_service.parse_ielts("abc")
    assert not ok and "con số" in msg


def test_parse_budget():
    # Number string
    ok, val, _ = wizard_service.parse_budget("200000000")
    assert ok and val == 200000000.0

    # "tr" / "triệu" string
    ok, val, _ = wizard_service.parse_budget("200tr")
    assert ok and val == 200000000.0

    ok, val, _ = wizard_service.parse_budget("150 triệu")
    assert ok and val == 150000000.0

    # Ngan sach = 0 / bo trong - hop le, coi nhu chua ro ngan sach
    ok, val, _ = wizard_service.parse_budget("0")
    assert ok and val == 0.0

    ok, val, _ = wizard_service.parse_budget("")
    assert ok and val == 0.0

    # Invalid budget - am
    ok, val, msg = wizard_service.parse_budget("-5000")
    assert not ok and "không được là số âm" in msg

    # Invalid budget - khong phai so
    ok, val, msg = wizard_service.parse_budget("abc")
    assert not ok and val is None


def test_parse_budget_khong_gioi_han_khac_voi_0():
    # "khong gioi han" phai la 1 gia tri rat lon, khac han 0.0 cua case
    # "bo trong/thieu du lieu" (2 case nay mang y nghia nguoc nhau o C3)
    for text in ["không giới hạn", "khong gioi han", "vô hạn", "unlimited"]:
        ok, val, _ = wizard_service.parse_budget(text)
        assert ok
        assert val == wizard_service.NGAN_SACH_KHONG_GIOI_HAN
        assert val != 0.0


def test_wizard_state_flow():
    w = wizard_service.WizardState()
    assert w.step == 1

    # Step 1
    ok, _ = w.set_gpa("3.2")
    assert ok and w.step == 2

    # Step 2
    ok, _ = w.set_english("7.0")
    assert ok and w.step == 3

    # Step 3
    ok, _ = w.set_budget("300 triệu")
    assert ok and w.step == 4

    # Step 4
    ok, _ = w.set_preferences(["Anh"], ["Business"])
    assert ok and w.is_complete()

    prof = w.get_profile()
    assert prof["gpa"] == 3.2
    assert prof["ielts"] == 7.0
    assert prof["budget_per_year"] == 300000000.0
    assert prof["preferred_countries"] == ["Anh"]
    assert prof["preferred_majors"] == ["Business"]


def test_wizard_khong_nhap_gi_o_buoc_uu_tien_van_qua_duoc():
    # Buoc 4 la optional - bo trong (khong truyen gi) phai duoc cho qua binh thuong
    w = wizard_service.WizardState()
    w.set_gpa("3.2")
    w.set_english("7.0")
    w.set_budget("300 triệu")

    ok, _ = w.set_preferences()
    assert ok and w.is_complete()

    prof = w.get_profile()
    assert prof["preferred_countries"] == []
    assert prof["preferred_majors"] == []


def test_wizard_sai_input_khong_cho_qua_buoc_tiep_theo():
    # GPA am -> khong duoc tang step, phai dung lai o buoc 1
    w = wizard_service.WizardState()
    ok, _ = w.set_gpa("-1.0")
    assert not ok
    assert w.step == 1

    # Sua lai GPA hop le moi qua duoc buoc 2, roi IELTS ngoai thang khong cho qua buoc 3
    w.set_gpa("3.2")
    ok, _ = w.set_english("15.0")
    assert not ok
    assert w.step == 2


def test_wizard_khong_gioi_han_ngan_sach_duoc_cham_diem_toi_da_o_c3():
    # End-to-end: gia tri wizard tra ve cho "khong gioi han" phai duoc
    # recommend_service.score() cham DAT C3 (30/30).
    ok, budget, _ = wizard_service.parse_budget("không giới hạn")
    assert ok

    uni = {"tuition_per_year": 100000, "currency": "GBP"}  # hoc phi quy doi rat lon
    diem = recommend_service.score({"budget_per_year": budget}, uni)
    assert diem == 100  # chi con C3 tinh diem, phai dat toi da


def test_wizard_ho_so_day_du_dung_dinh_dang_cho_recommend_service():
    # Dict tra ve phai dung ten field ma recommend_service.score() dang doc
    # (gpa, ielts, toefl, budget_per_year, preferred_countries, preferred_majors)
    w = wizard_service.WizardState()
    w.set_gpa("3.2")
    w.set_english("7.0")
    w.set_budget("300 triệu")
    w.set_preferences(["Japan"], ["Khoa hoc may tinh"])

    prof = w.get_profile()
    assert set(prof.keys()) == {
        "gpa", "ielts", "toefl", "budget_per_year",
        "preferred_countries", "preferred_majors",
    }
    assert isinstance(prof["gpa"], float)
    assert isinstance(prof["ielts"], float)
    assert isinstance(prof["budget_per_year"], float)
    assert isinstance(prof["preferred_countries"], list)
    assert isinstance(prof["preferred_majors"], list)
