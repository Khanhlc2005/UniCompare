# Công thức chấm điểm rule-based cho chatbot gợi ý trường

Mục tiêu: `recommend_service.score(profile, university)` chấm mỗi trường **0–100**
(hiển thị thành "% phù hợp" trên ChatbotView), dựa trên hồ sơ thu từ Wizard 4 bước
(Học lực → Chứng chỉ → Ngân sách → Ưu tiên) — đúng mô tả ARCHITECTURE.md §6.
Chỉ dùng field đã có trong schema `universities` (ARCHITECTURE.md §4).

---

## 1. Hồ sơ người dùng (profile) — thu từ Wizard 4 bước

| Bước wizard  | Field trong profile                                     | Kiểu                | Ghi chú                                                                         |
| ------------ | ------------------------------------------------------- | ------------------- | ------------------------------------------------------------------------------- |
| 1. Học lực   | `gpa`                                                   | float, thang 4.0    | bắt buộc nhập                                                                   |
| 2. Chứng chỉ | `ielts` và/hoặc `toefl`                                 | float / int         | được phép chọn "chưa có chứng chỉ"                                              |
| 3. Ngân sách | `budget_per_year`                                       | number, **VND/năm** | học phí tối đa chịu được; code quy đổi học phí trường về VND để so (mục 2 — C3) |
| 4. Ưu tiên   | `preferred_countries` (list), `preferred_majors` (list) | list[str]           | được phép để trống = không có ưu tiên                                           |

Riêng tiêu chí C6 (ranking) không cần người dùng nhập gì — chấm thẳng từ field
`ranking` của trường.

### 1.1. Chuẩn hoá input ở Wizard

Hai xử lý sau nằm ở `wizard_service.py` (bước thu thập, TRƯỚC khi profile được
đưa vào `recommend_service.score()`), không đổi hợp đồng field hay công thức
chấm điểm ở mục 2 — chỉ chuẩn hoá dữ liệu đầu vào cho đúng ý người dùng:

- **GPA thang 10 → thang 4 (bước 1):** nếu người dùng nhập `4.0 < gpa <= 10.0`,
  `parse_gpa()` coi đây là điểm thang 10 và tự quy đổi xấp xỉ về thang 4 bằng
  `gpa_4 = gpa_10 / 2.5`. Đây là công thức ước lượng tuyến tính đơn giản (không
  phải bảng quy đổi chính thức của Bộ GD&ĐT) — đủ dùng cho mục đích gợi ý sơ bộ
  của chatbot, KHÔNG dùng để xét tuyển thật. Nếu `gpa <= 4.0`, giữ nguyên vì đã
  đúng thang 4.
- **Ngân sách "Không giới hạn" (bước 3):** wizard nhận diện các cụm nhập tự do
  "không giới hạn" / "khong gioi han" / "vô hạn" / "unlimited" và gán một số rất
  lớn — hằng số `NGAN_SACH_KHONG_GIOI_HAN = 10**12` trong `wizard_service.py` —
  thay vì `0`. Lý do: `budget_per_year = 0` (bỏ trống/không nhập) đã có ý nghĩa
  riêng ở mục 3.3 dưới đây là "thiếu dữ liệu ngân sách → chấm 0 điểm C3"; nếu
  dùng chung `0` cho cả hai case thì người chọn "không giới hạn" sẽ bị chấm
  *sai* thành 0 điểm ngân sách (tệ nhất có thể) thay vì đạt tối đa.

## 2. Tiêu chí & cách tính điểm từng tiêu chí

6 tiêu chí, mỗi tiêu chí có trọng số riêng, tổng trọng số = **100**.

### C1 — Chứng chỉ tiếng Anh (trọng số **30**)

- Hồ sơ: `ielts` / `toefl` (bước 2) — so với `ielts_min` / `toefl_min` của trường.
- Nếu người dùng có cả 2 chứng chỉ (hoặc trường có cả 2 mức min): so từng cặp
  cùng loại (IELTS với `ielts_min`, TOEFL với `toefl_min`), **lấy kết quả tốt nhất**
  trong các cặp so được — vì trường nào cũng chỉ yêu cầu đạt 1 trong 2.
- Thang điểm (không nhị phân — thiếu ít vẫn còn cơ hội luyện thi lại):

| Kết quả so sánh                                       | Điểm                                                         |
| ----------------------------------------------------- | ------------------------------------------------------------ |
| Đạt mức tối thiểu (`>=`)                              | 30                                                           |
| Thiếu ít: IELTS thiếu ≤ 0.5 **hoặc** TOEFL thiếu ≤ 10 | 15                                                           |
| Thiếu nhiều hơn                                       | 0                                                            |
| Người dùng "chưa có chứng chỉ" (trường có yêu cầu)    | 0 — **không** bỏ tiêu chí, vì yêu cầu của trường vẫn tồn tại |

### C2 — GPA (trọng số **15**)

- Hồ sơ: `gpa` (bước 1) — so với `gpa_min` của trường.

| Kết quả          | Điểm |
| ---------------- | ---- |
| `gpa >= gpa_min` | 15   |
| Thiếu ≤ 0.2      | 8    |
| Thiếu nhiều hơn  | 0    |

### C3 — Ngân sách (trọng số **30**)

- Hồ sơ: `budget_per_year` bằng **VND** (bước 3) — so với
  `tuition_per_year` của trường **sau khi quy đổi về VND**.
- Quy đổi: `hoc_phi_vnd = tuition_per_year * TY_GIA_VND[currency]`, trong đó
  `TY_GIA_VND` là **bảng tỷ giá cố định hard-code** trong `recommend_service`
  (1 dict hằng số, ghi rõ ngày lấy tỷ giá trong comment). Tỷ giá tham khảo tại
  thời điểm viết — Issue #3.5 khi code sẽ cập nhật số mới nhất:

| Currency (đủ 4 loại trong seed) | 1 đơn vị ≈ VND |
| ------------------------------- | -------------- |
| CNY                             | 3.600          |
| JPY                             | 175            |
| KRW                             | 19             |
| GBP                             | 34.500         |

- `currency` lạ chưa có trong bảng → coi như trường thiếu dữ liệu học phí → bỏ
  tiêu chí C3 (theo quy tắc mục 3.3), đồng thời log/ghi chú để bổ sung tỷ giá.

| Kết quả                                              | Điểm                                                 |
| ---------------------------------------------------- | ---------------------------------------------------- |
| `budget >= hoc_phi_vnd` (**bằng đúng vẫn tính đạt**) | 30                                                   |
| Học phí vượt ngân sách ≤ 10%                         | 15 — nhiều trường trong seed có học bổng, còn cửa bù |
| Vượt hơn 10%                                         | 0                                                    |

### C4 — Ưu tiên quốc gia (trọng số **10**)

- Hồ sơ: `preferred_countries` (bước 4) — so với `country` của trường.
- Nhị phân: `country` nằm trong danh sách ưu tiên → 10, không → 0.
- So sánh phải khớp đúng giá trị `country` trong DB
  (`"China (Mainland)"`, `"Japan"`, `"Korea (South)"`, `"United Kingdom"`) —
  wizard nên cho **chọn từ danh sách quốc gia có sẵn trong DB**, không cho gõ tay,
  để khỏi lệch chuỗi.

### C5 — Ưu tiên ngành (trọng số **10**)

- Hồ sơ: `preferred_majors` (bước 4) — so với list `majors` của trường.
- Nhị phân: có ít nhất 1 ngành trùng → 10, không → 0.
- Giống C4: wizard cho chọn ngành từ tập ngành có trong DB, tránh so chuỗi gõ tay.

### C6 — Bonus ranking (trọng số **5**)

- Không lấy từ wizard — chấm thẳng từ field `ranking` của trường, để trường thứ
  hạng cao được "cộng nhẹ" khi các điều kiện khác ngang nhau.
- Trọng số cố ý nhỏ nhất (5/100) để ranking **không lấn át** điều kiện cứng:
  một trường rank thấp nhưng đủ tiền + đủ tiếng Anh vẫn phải thắng trường rank
  cao mà người dùng không đủ điều kiện.

| `ranking`    | Điểm                          |
| ------------ | ----------------------------- |
| ≤ 20         | 5                             |
| 21–50        | 3                             |
| 51–100       | 1                             |
| > 100        | 0                             |
| null / thiếu | bỏ tiêu chí (quy tắc mục 3.3) |

### Vì sao chọn trọng số như vậy

- **C1 (30) + C3 (30) cao nhất:** không đủ tiếng Anh hoặc không đủ tiền là gần như
  không đi được — đây là 2 điều kiện "cứng" nhất.
- **C2 (15) thấp hơn C1:** GPA quan trọng nhưng trong seed data rất nhiều trường
  không công bố `gpa_min` (null), và nhiều trường xét hồ sơ tổng thể.
  (Hạ từ 20 xuống 15 để nhường 5 điểm cho C6 mà tổng vẫn đúng 100.)
- **C4/C5 (10 + 10):** chỉ là "ưu tiên", trường tốt ở quốc gia khác vẫn đáng gợi ý —
  trọng số thấp để không lấn át điều kiện cứng.
- **C6 (5):** bonus nhẹ cho thứ hạng, nhỏ nhất trong 6 tiêu chí — đúng tinh thần
  "được cộng nhẹ nhưng không chiếm quá nhiều".

## 3. Xử lý case biên (Issue #3.5 sẽ viết pytest đúng các case này)

1. **Hồ sơ thiếu 1 chỉ số so với yêu cầu** (VD IELTS thiếu 0.5):
   **trừ điểm theo bậc, không loại thẳng** (bảng C1/C2) — vì đây là chatbot _gợi ý_,
   không phải hệ thống xét tuyển; người dùng có thể thi lại/cải thiện.
   _Phương án thay thế nếu nhóm muốn chặt hơn: thiếu chuẩn tiếng Anh → loại khỏi
   top N luôn. Cần nhóm chốt 1 trong 2 khi review._
2. **Ngân sách sát nút** (`budget == hoc_phi_vnd`): **tính đạt** — dùng `>=`.
   Lưu ý khi test: học phí đã qua nhân tỷ giá nên so bằng tuyệt đối dễ lệch số lẻ —
   pytest ở Issue #3.5 nên test case "bằng đúng" bằng số đã nhân sẵn tỷ giá.
3. **Trường thiếu field trong DB** (VD `gpa_min: null` — thực tế 5/7 trường Trung Quốc
   trong seed đang null; `ranking` hoặc `currency` lạ cũng xử lý cùng kiểu):
   **bỏ tiêu chí đó khỏi cả tử số lẫn mẫu số rồi quy đổi lại** (xem công thức mục 4),
   KHÔNG chấm 0 — trường thiếu dữ liệu không có nghĩa là người dùng không đạt.
   - Tương tự, người dùng **để trống bước Ưu tiên** → bỏ C4/C5 khỏi mẫu số.
   - Lưu ý phân biệt: field trường bị thiếu → _bỏ tiêu chí_; người dùng thiếu
     chứng chỉ mà trường có yêu cầu → _chấm 0_ (mục C1).
   - Nếu tổng trọng số còn so được < 50 (trường thiếu quá nhiều dữ liệu), vẫn tính
     điểm nhưng UI nên gắn nhãn "dữ liệu chưa đầy đủ" — tránh trường ít dữ liệu
     nghiễm nhiên điểm cao.
4. **Điểm âm / vượt 100 / chia 0** (DoD tuần 4):
   - Từng tiêu chí bị chặn trong `[0, trọng số]` ngay từ bảng điểm → tổng không
     thể âm hay vượt 100 về mặt thiết kế; vẫn kẹp `max(0, min(100, score))` ở cuối
     cho chắc.
   - Chia 0 chỉ xảy ra khi **mọi** tiêu chí đều bị bỏ (trường thiếu sạch dữ liệu
     và người dùng không có ưu tiên) → quy ước trả **0 điểm** kèm nhãn
     "không đủ dữ liệu để chấm", không đưa vào top N.

## 4. Công thức tổng (giả mã)

```
score(profile, university):
    # quy doi hoc phi ve VND truoc khi cham C3
    neu university.currency co trong TY_GIA_VND:
        hoc_phi_vnd = university.tuition_per_year * TY_GIA_VND[currency]
    nguoc lai: coi nhu thieu du lieu hoc phi (C3 se bi bo)

    tong_diem = 0        # tu so
    tong_trong_so = 0    # mau so — chi cong tieu chi so sanh duoc

    cho tung tieu chi C trong [C1..C6]:
        neu tieu chi bo qua duoc (field truong null / currency la / khong co uu tien):
            bo qua, khong cong gi
        nguoc lai:
            tong_diem += diem_C          # trong [0, trong_so_C]
            tong_trong_so += trong_so_C

    neu tong_trong_so == 0:  tra ve 0 (nhan "khong du du lieu")

    score = tong_diem / tong_trong_so * 100
    tra ve round(max(0, min(100, score)))
```

Top N: sắp theo `score` giảm dần, hiển thị thành "% phù hợp" trên card kết quả.

## 5. Các điểm mở trước đây — đã chốt hướng (Khánh, 25/07/2026)

Vẫn nằm trong phạm vi review chung của nhóm, nhưng không còn là câu hỏi mở:

1. **Tiền tệ — ĐÃ CHỐT: quy đổi tất cả về VND.** Người dùng nhập ngân sách bằng
   VND/năm (quen thuộc nhất với người dùng Việt), code quy đổi `tuition_per_year`
   của trường về VND bằng bảng tỷ giá cố định hard-code (chi tiết ở mục 2 — C3).
   Không gọi API tỷ giá — giữ L1 thuần Python, không cần mạng, test được bằng pytest.
2. **Ranking — ĐÃ CHỐT: có bonus, giữ ở mức nhẹ.** Thêm tiêu chí C6 trọng số 5/100
   (bảng điểm ở mục 2 — C6), lấy 5 điểm từ C2 (GPA 20 → 15) để tổng vẫn là 100.
   Trọng số 5 đủ để tách 2 trường ngang điểm nhưng không bao giờ bù nổi việc
   trượt 1 điều kiện cứng (thiếu tiếng Anh mất 15–30 điểm, thiếu tiền mất 15–30 điểm).
3. **`deadline` và `scholarship` — ĐÃ CHỐT: không tham gia chấm điểm, chỉ hiển thị**
   trên card kết quả. Lý do: `deadline` nói về _thời điểm nộp_ chứ không phải mức độ
   phù hợp của hồ sơ, lại hay bị null trong seed (so ngày với null sẽ đẻ thêm case
   biên vô ích); `scholarship` là text tự do ("Có, tối đa 50%", tên học bổng...)
   không so máy được — nếu ép chấm sẽ thành so chuỗi cảm tính, sai tinh thần
   rule-based. Ảnh hưởng của học bổng đã được phản ánh gián tiếp ở C3
   (vượt ngân sách ≤ 10% vẫn được nửa điểm vì còn cửa học bổng bù).

## 6. Ví dụ minh hoạ — chấm thử 1 hồ sơ với 3 trường trong seed

Hồ sơ mẫu:

- GPA **3.2** · IELTS **6.0** (không có TOEFL) · ngân sách **150 triệu VND/năm**
- Ưu tiên: quốc gia `China (Mainland)`, ngành `Khoa hoc may tinh`

Học phí quy đổi (tỷ giá CNY = 3.600): Peking 30.000 CNY = **108tr** ·
Fudan 60.000 CNY = **216tr** · SJTU 24.800 CNY = **89,3tr**.

| Tiêu chí (trọng số) | Peking (ielts 6.5, gpa null, rank 14, có CS) | Fudan (ielts 6.5, gpa 3.0, rank 30, không CS) | SJTU (ielts 6.0, gpa null, rank 45, có CS) |
| ------------------- | -------------------------------------------- | --------------------------------------------- | ------------------------------------------ |
| C1 tiếng Anh (30)   | thiếu 0.5 → **15**                           | thiếu 0.5 → **15**                            | 6.0 ≥ 6.0 → **30**                         |
| C2 GPA (15)         | `gpa_min` null → **bỏ**                      | 3.2 ≥ 3.0 → **15**                            | `gpa_min` null → **bỏ**                    |
| C3 ngân sách (30)   | 150tr ≥ 108tr → **30**                       | 216tr vượt 44% → **0**                        | 150tr ≥ 89,3tr → **30**                    |
| C4 quốc gia (10)    | **10**                                       | **10**                                        | **10**                                     |
| C5 ngành (10)       | **10**                                       | **0**                                         | **10**                                     |
| C6 ranking (5)      | 14 ≤ 20 → **5**                              | 30 → **3**                                    | 45 → **3**                                 |
| Tử / mẫu            | 70 / 85                                      | 43 / 100                                      | 83 / 85                                    |
| **Điểm cuối**       | **82**                                       | **43**                                        | **98**                                     |

Đọc kết quả: SJTU vẫn dẫn đầu vì hồ sơ đạt đủ mọi tiêu chí so được; bonus ranking
kéo Peking (rank 14) lại gần hơn một chút (82 so với 98, trước khi có C6 là 81 so
với 100) nhưng không đảo được thứ tự — đúng yêu cầu "cộng nhẹ, không chiếm quá
nhiều". Fudan tụt sâu vì học phí vượt ngân sách quá xa + không có ngành ưu tiên.
