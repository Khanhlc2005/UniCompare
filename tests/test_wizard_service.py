# -*- coding: utf-8 -*-
"""Unit tests cho wizard_service.py (Issue 3.6)."""

import pytest

from services import wizard_service


def test_parse_gpa():
    # Valid GPA scale 4
    ok, val, _ = wizard_service.parse_gpa("3.5")
    assert ok and val == 3.5

    # Valid GPA scale 10 (converts to scale 4: 8.5 / 2.5 = 3.4)
    ok, val, _ = wizard_service.parse_gpa("8.5")
    assert ok and val == 3.4

    # Invalid GPA
    ok, val, msg = wizard_service.parse_gpa("-1.0")
    assert not ok and "0.0 đến 10.0" in msg

    ok, val, msg = wizard_service.parse_gpa("12.0")
    assert not ok and "0.0 đến 10.0" in msg

    ok, val, msg = wizard_service.parse_gpa("abc")
    assert not ok and "con số" in msg


def test_parse_ielts():
    # Valid IELTS
    ok, val, _ = wizard_service.parse_ielts("6.5")
    assert ok and val == 6.5

    # No IELTS / 0
    ok, val, _ = wizard_service.parse_ielts("chưa có")
    assert ok and val == 0.0

    # Invalid IELTS
    ok, val, msg = wizard_service.parse_ielts("10.0")
    assert not ok and "0.0 đến 9.0" in msg


def test_parse_budget():
    # Number string
    ok, val, _ = wizard_service.parse_budget("200000000")
    assert ok and val == 200000000.0

    # "tr" / "triệu" string
    ok, val, _ = wizard_service.parse_budget("200tr")
    assert ok and val == 200000000.0

    ok, val, _ = wizard_service.parse_budget("150 triệu")
    assert ok and val == 150000000.0

    # Invalid budget
    ok, val, msg = wizard_service.parse_budget("-5000")
    assert not ok and "không được là số âm" in msg


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
