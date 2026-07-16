# NGUON_DU_LIEU.md — Nguon va do tin cay du lieu 22 truong

Theo yeu cau moi: khong bat buoc dung 3 nuoc cu, uu tien quoc gia giao duc
phat trien + du lieu du/de xac minh. Ket qua:

- **Trung Quoc (Mainland): giu nguyen 7 truong** — du lieu day du, co nguon
  ro rang tu trang tuyen sinh quoc te chinh thuc.
- **Nhat Ban: giu nguyen 7 truong** — 3 truong (Tokyo, Kyoto, Osaka) da co
  san du lieu tot; 4 truong con lai (Institute of Science Tokyo, Tohoku,
  Nagoya, Keio) TRUOC DAY thieu ranking, nay da dien bang Times Higher
  Education World Rankings 2026 (khong phai QS - khong tim duoc so QS rieng
  trong thoi gian cho phep, ghi ro trong cot "verified" tung dong).
- **Han Quoc: CHI giu 2 truong da co du lieu tot** (Seoul National University,
  KAIST) - 4 truong con lai (Korea University, Yonsei, POSTECH, SKKU) bi loai
  vi khong tra duoc so lieu chinh xac/co nguon trong thoi gian hop ly.
- **Them moi: Vuong quoc Anh (United Kingdom), 6 truong** (Oxford, Cambridge,
  Imperial College London, UCL, Edinburgh, Manchester) de bu vao cho 4 truong
  Han Quoc da loai - du lieu tuyen sinh Anh rat chuan hoa (IELTS/TOEFL/hoc phi
  cong khai ro rang tren cac trang tong hop uy tin), de xac minh hon.

=> Bo du lieu hien tai la 4 "khoi" quoc gia (Trung Quoc, Nhat Ban, Han Quoc,
Anh) thay vi dung 3 quoc gia tuyet doi, vi 2 truong Han Quoc (SNU, KAIST) da
co san du lieu chat luong tot nen giu lai thay vi bo di uong phi. Neu ban muon
dung dung 3 quoc gia, cach don gian nhat la xoa 2 dong "seoul-national-university"
va "kaist" khoi data/seed_data.json (con 20 truong, 3 quoc gia: Trung Quoc,
Nhat Ban, Anh).

## Bang chi tiet

| #   | Truong                        | Quoc gia         | Ranking | Nguon ranking                       | Do tin cay chung |
| --- | ----------------------------- | ---------------- | ------- | ----------------------------------- | ---------------- |
| 1   | Peking University             | China (Mainland) | 14      | QS 2026                             | mot phan         |
| 2   | Tsinghua University           | China (Mainland) | 17      | QS 2026                             | mot phan         |
| 3   | Fudan University              | China (Mainland) | 30      | QS 2026                             | co               |
| 4   | Shanghai Jiao Tong University | China (Mainland) | 45      | uoc tinh                            | co               |
| 5   | Zhejiang University           | China (Mainland) | 44      | uoc tinh                            | co               |
| 6   | Nanjing University            | China (Mainland) | 103     | QS 2026 (British Council)           | co               |
| 7   | USTC                          | China (Mainland) | 133     | QS 2025, can cap nhat 2026          | co               |
| 8   | The University of Tokyo       | Japan            | 32      | QS 2026                             | co               |
| 9   | Kyoto University              | Japan            | 46      | uoc tinh, can xac nhan              | co (tru ranking) |
| 10  | Osaka University              | Japan            | 68      | uoc tinh, can xac nhan              | mot phan         |
| 11  | Institute of Science Tokyo    | Japan            | 325     | THE 2026 (band 301-350, trung diem) | mot phan         |
| 12  | Tohoku University             | Japan            | 103     | THE 2026 (chinh xac)                | mot phan         |
| 13  | Nagoya University             | Japan            | 225     | THE 2026 (band 201-250, trung diem) | mot phan         |
| 14  | Keio University               | Japan            | 700     | THE 2026 (band 601-800, trung diem) | mot phan         |
| 15  | Seoul National University     | Korea (South)    | 31      | QS 2026                             | co               |
| 16  | KAIST                         | Korea (South)    | 56      | QS 2024, can cap nhat               | co               |
| 17  | University of Oxford          | United Kingdom   | 3       | uoc tinh chung                      | co               |
| 18  | University of Cambridge       | United Kingdom   | 5       | uoc tinh chung                      | co               |
| 19  | Imperial College London       | United Kingdom   | 2       | uoc tinh chung                      | mot phan         |
| 20  | University College London     | United Kingdom   | 9       | uoc tinh chung                      | mot phan         |
| 21  | University of Edinburgh       | United Kingdom   | 27      | uoc tinh chung                      | mot phan         |
| 22  | University of Manchester      | United Kingdom   | 35      | uoc tinh chung                      | mot phan         |

## Luu y quan trong ve ranking

- Ranking cua 22 truong nay tron lan giua QS va THE (2 he thong xep hang
  khac nhau, so khong hoan toan tuong duong). Day la danh doi de dam bao MOI
  truong deu co so (khong de trong/bia), phu hop cho DEMO. Neu bai nop can
  chinh xac tuyet doi theo 1 he thong (vd chi QS nhu du kien ban dau trong
  Tai lieu tong hop du an), nhom nen danh ~30-45 phut tra lai rieng tren
  https://www.topuniversities.com truoc ngay nop.
- Ranking cua 6 truong Anh la uoc tinh chung dua tren nhan biet pho quat
  (Oxford/Cambridge/Imperial/UCL luon trong top 10 QS/THE the gioi nhieu nam
  lien), KHONG phai trich tu 1 bang xep hang cu the nam 2026 - can xac nhan
  lai neu muon con so chinh xac.

## Cach doc cot "Do tin cay chung" (field verified trong seed_data.json)

- "co": IELTS/TOEFL/hoc phi lay truc tiep tu trang tuyen sinh quoc te
  chinh thuc hoac nguon giao duc dang tin cay, tra cuu thang 7/2026.
- "mot phan": it nhat 1 field quan trong (thuong la hoc phi hoac ranking)
  la khoang uoc tinh tu nguon tong hop, chua phai so chinh thuc tu truong.

## Quy trinh nap vao MongoDB

```bash
pip install -r requirements.txt --break-system-packages
cp .env.example .env        # dien MONGO_URI that vao .env
python3 scripts/validate_data.py   # phai thay "HOP LE" (hien tai: 22/22 hop le)
python3 scripts/seed.py            # validate lai + nap vao Mongo (upsert theo "id")
```

seed.py dung update_one(..., upsert=True) theo field id - chay lai nhieu
lan AN TOAN, khong tao du lieu trung.
