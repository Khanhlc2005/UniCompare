# -*- coding: utf-8 -*-
"""
scripts/validate_data.py - Issue 1.1 (ARCHITECTURE.md muc 4 + 7):
"Validate bat duoc field thieu / sai kieu so".

Chay: python3 scripts/validate_data.py [duong_dan_file.json]
Mac dinh doc data/seed_data.json. Thoat voi exit code != 0 neu co loi,
de dung trong CI (.github/workflows/test.yml) hoac truoc khi chay seed.py.
"""
import json
import sys
import os

REQUIRED_STRING_FIELDS = ["id", "name", "country", "city", "currency"]
# Cac field SO BAT BUOC theo ARCHITECTURE.md muc 4 (dung de loc/so sanh/cham diem)
REQUIRED_NUMERIC_FIELDS = ["ranking", "tuition_per_year", "ielts_min", "toefl_min"]
# gpa_min duoc phep None (nhieu truong khong cong bo GPA toi thieu ro rang -
# xem ghi chu trong NGUON_DU_LIEU.md), nhung neu co gia tri thi phai la so.
OPTIONAL_NUMERIC_FIELDS = ["gpa_min"]

VALID_CURRENCIES = {"CNY", "JPY", "KRW", "USD", "GBP"}


def validate_university(u: dict, index: int) -> list[str]:
    errors = []
    prefix = f"[#{index}] {u.get('name', '(khong co ten)')}"

    for field in REQUIRED_STRING_FIELDS:
        val = u.get(field)
        if not isinstance(val, str) or not val.strip():
            errors.append(f"{prefix}: thieu hoac sai kieu field bat buoc '{field}' (can string khong rong)")

    if u.get("currency") and u["currency"] not in VALID_CURRENCIES:
        errors.append(f"{prefix}: currency '{u['currency']}' khong nam trong {VALID_CURRENCIES}")

    for field in REQUIRED_NUMERIC_FIELDS:
        val = u.get(field)
        if val is None:
            errors.append(f"{prefix}: thieu field so bat buoc '{field}'")
        elif isinstance(val, bool) or not isinstance(val, (int, float)):
            errors.append(f"{prefix}: field '{field}' phai la so, dang nhan gia tri {val!r} ({type(val).__name__})")
        elif val < 0:
            errors.append(f"{prefix}: field '{field}' khong duoc am (dang la {val})")

    for field in OPTIONAL_NUMERIC_FIELDS:
        val = u.get(field)
        if val is not None and (isinstance(val, bool) or not isinstance(val, (int, float))):
            errors.append(f"{prefix}: field tuy chon '{field}' phai la so hoac null, dang la {val!r}")

    majors = u.get("majors")
    if not isinstance(majors, list) or not all(isinstance(m, str) for m in majors):
        errors.append(f"{prefix}: field 'majors' phai la list[str]")

    if not isinstance(u.get("overview"), str) or not u.get("overview", "").strip():
        errors.append(f"{prefix}: thieu field 'overview' (mo ta ngan)")

    return errors


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(__file__), "..", "data", "seed_data.json"
    )

    if not os.path.exists(path):
        print(f"[loi] Khong tim thay file: {path}")
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[loi] File JSON khong hop le: {e}")
            sys.exit(1)

    if not isinstance(data, list):
        print("[loi] Noi dung file phai la mot list cac truong.")
        sys.exit(1)

    all_errors: list[str] = []
    seen_ids = set()
    for i, u in enumerate(data, start=1):
        all_errors.extend(validate_university(u, i))
        uid = u.get("id")
        if uid in seen_ids:
            all_errors.append(f"[#{i}] id trung lap: '{uid}'")
        seen_ids.add(uid)

    print(f"Kiem tra {len(data)} truong trong {path}")
    if all_errors:
        print(f"\n=> THAT BAI: {len(all_errors)} loi\n")
        for e in all_errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("=> HOP LE: tat ca truong deu dat yeu cau schema.")
        sys.exit(0)


if __name__ == "__main__":
    main()
