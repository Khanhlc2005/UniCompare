# PLAN.md — UniCompare (4 tuần, 4 người)

Kế hoạch dạng **Issue/task theo từng tuần**, bám đúng WBS (mục 8) và phân việc
(mục 6–7) trong Tài liệu tổng hợp dự án. Mỗi dòng dưới đây = 1 Issue trên GitHub,
tạo bằng template **Task**, gắn label (`data` / `ui` / `ai`), Milestone
`Sprint 1 - Tuần N`, và đưa vào Project board.

Quy trình cho từng Issue: theo README (branch từ Issue → Conventional Commits →
PR ghi `Closes #N` → 1 người review → CI xanh → Squash and merge → xóa nhánh).

**Nguyên tắc đã chốt:**
- Core cá nhân phải xong **trước cuối tuần 2**; optional chỉ bắt đầu sau khi core của mình xong.
- Hợp đồng Repository chỉ đổi khi họp thống nhất.
- UI làm theo wireframe (`University_Browser_Wireframes-print.pdf`) — không tự chế layout.

Ánh xạ Dev ↔ tên: Dev 1 = Dương, Dev 2 = Huy, Dev 3 = Khánh, Dev 4 = Nam Anh.

---

## Tuần 1 — Dựng khung, cả nhóm chạy trên fake_repo

**Mục tiêu tuần:** cuối tuần 1, App Shell mở được và chuyển qua lại các frame;
mọi màn hình core có khung UI chạy trên fake_repo.

### Việc chung ngày 1–2 (làm trước, chặn mọi việc khác)
| # | Issue | Người | Label |
| --- | --- | --- | --- |
| 1.0a | Setup repo: cấu trúc thư mục theo ARCHITECTURE.md, `requirements.txt`, `config.py` đọc `.env` | Khánh (leader) | data |
| 1.0b | Viết `university_repo.py` (interface) + `fake_repo.py` ~8 trường mẫu đủ field theo schema | Nam Anh | data |
| 1.0c | Họp chốt: nơi lưu watchlist (collection Mongo vs JSON local) — ghi kết luận vào ARCHITECTURE.md | Cả nhóm | — |

### Dương (Data + Admin)
| # | Issue | Acceptance criteria chính | Label |
| --- | --- | --- | --- |
| 1.1 | Viết schema `universities` + `ai_cache`, script `validate_data.py` | Validate bắt được field thiếu / sai kiểu số | data |
| 1.2 | Bắt đầu `mongo_repo.py` + kết nối Mongo qua `MONGO_URI` | Kết nối được, `get_all()` chạy | data |
| 1.3 | Khung `AdminView`: Treeview danh sách + form thêm/sửa (theo wireframe 8), chạy trên fake_repo | Thêm/sửa/xóa hiển thị đúng trên Treeview | ui |

### Huy (Tìm kiếm)
| # | Issue | Acceptance criteria chính | Label |
| --- | --- | --- | --- |
| 1.4 | `university_service.search()` : từ khóa + lọc quốc gia trên fake_repo, kèm pytest | Test pass các case: rỗng, không match, có dấu/không dấu | data |
| 1.5 | Khung `SearchView`: search bar + 3 nhóm pill filter + card grid (wireframe 3) | Gõ từ khóa + bấm pill → danh sách card cập nhật | ui |

### Khánh (Watchlist + Compare)
| # | Issue | Acceptance criteria chính | Label |
| --- | --- | --- | --- |
| 1.6 | `watchlist_service` + `compare_service` (state chọn tối đa 5 trường, dùng chung giữa các màn) | Chọn trường thứ 6 bị chặn + có thông báo | data |
| 1.7 | Khung `WatchlistView`: card đã lưu + pill quốc gia + checkbox so sánh (wireframe 2) | Lưu/bỏ lưu phản ánh ngay trên UI | ui |
| 1.8 | Khung `CompareView`: chip trường đã chọn + bảng dữ liệu (wireframe 5, chưa chart, chưa highlight) | Chọn 2–5 trường → bảng render đúng cột | ui |

### Nam Anh (Chi tiết + App Shell)
| # | Issue | Acceptance criteria chính | Label |
| --- | --- | --- | --- |
| 1.9 | `AppShell`: cửa sổ ttkbootstrap + sidebar (wireframe 1) + `show_frame()` theo Frame contract | Chuyển được giữa các frame rỗng, Admin tách riêng | ui |
| 1.10 | Khung `DetailView`: banner + 4 stat card + mục lục/nội dung (wireframe 4), nhận `university_id` | Mở từ card Search/Watchlist ra đúng trường | ui |

---

## Tuần 2 — Mongo thật, hoàn thiện core (DEADLINE CORE: cuối tuần 2)

**Mục tiêu tuần:** đổi import sang `mongo_repo`, toàn bộ core F1–F6 hoàn chỉnh
chạy dữ liệu thật; Huy đã prototype xong chart (né rủi ro threading).

### Dương
| # | Issue | Acceptance criteria chính | Label |
| --- | --- | --- | --- |
| 2.1 | Hoàn thiện `mongo_repo` đủ 6 hàm interface + pytest | CRUD chạy trên Mongo thật | data |
| 2.2 | `seed_data.json` 20–30 trường (2–3 quốc gia) + `scripts/seed.py` (validate trước khi nạp) | Nạp xong, số lượng đúng, không record sai kiểu | data |
| 2.3 | **Báo cả nhóm đổi import** fake_repo → mongo_repo (1 dòng ở `main.py`) | Cả 4 màn chạy dữ liệu thật | data |
| 2.4 | Hoàn thiện `AdminView`: validate input đầy đủ, thông báo lỗi rõ | Nhập sai kiểu số → chặn + báo đúng field | ui |
| 2.5 | Thiết kế collection `ai_cache` (hạ tầng cho recommend_service) | Schema + hàm get/set cache theo `profile_hash` | ai |

### Huy
| # | Issue | Acceptance criteria chính | Label |
| --- | --- | --- | --- |
| 2.6 | Hoàn thiện filter Tìm kiếm: 3 nhóm pill kết hợp nhau (quốc gia × học phí × IELTS) + phân trang | Kết quả đúng khi bật nhiều pill cùng lúc | ui |
| 2.7 | **Prototype matplotlib riêng**: nhúng `FigureCanvasTkAgg` vào frame test, update chart không đơ | Đổi dữ liệu 10 lần liên tiếp không treo, không leak | ui |

### Khánh
| # | Issue | Acceptance criteria chính | Label |
| --- | --- | --- | --- |
| 2.8 | Hoàn thiện bảng Compare: highlight giá trị tốt nhất mỗi tiêu chí, nút x bỏ trường trên chip | Highlight đúng (min học phí, max ranking…) | ui |
| 2.9 | StickyCompareBar "X/5 đã chọn" dùng chung Watchlist/Search (wireframe 2) | Số đếm đồng bộ giữa các màn | ui |
| 2.10 | Thiết kế công thức chấm điểm rule-based (tài liệu ngắn: tiêu chí, trọng số, thang 0–100) | Được nhóm review công thức trước khi code | ai |

### Nam Anh
| # | Issue | Acceptance criteria chính | Label |
| --- | --- | --- | --- |
| 2.11 | Hoàn thiện `DetailView` với data thật (đủ mục lục: tổng quan, yêu cầu, học phí & học bổng, ngành, liên hệ) | Mọi trường trong seed mở được, không lỗi field thiếu | ui |
| 2.12 | Hoàn thiện `HomeView`: 3 stat card số liệu thật + lối tắt + trường nổi bật (wireframe 1) | Số liệu khớp DB | ui |
| 2.13 | Ghép toàn bộ frame thật vào App Shell, rà `refresh()` khi chuyển màn | Đi hết luồng chính không gặp frame rỗng | ui |

**☑ Checkpoint cuối tuần 2 (họp nhóm):** demo core F1–F6 end-to-end trên Mongo thật.
Ai chưa xong core → cả nhóm dồn hỗ trợ, **hoãn optional của người đó**.

---

## Tuần 3 — Optional: chart + chatbot

### Dương
| # | Issue | Acceptance criteria chính | Label |
| --- | --- | --- | --- |
| 3.1 | Nối `recommend_service` với Repository + `ai_cache` (đọc trường từ repo, cache kết quả) | Cùng hồ sơ lần 2 lấy từ cache | ai |
| 3.2 | Hỗ trợ debug chung (buffer — nhận việc phát sinh từ checkpoint tuần 2) | — | — |

### Huy
| # | Issue | Acceptance criteria chính | Label |
| --- | --- | --- | --- |
| 3.3 | Tab Biểu đồ trong CompareView: dropdown chọn tiêu chí + bar chart (wireframe 6), từ prototype 2.7 | Đổi tiêu chí/trường → chart cập nhật mượt | ui |
| 3.4 | Hoàn thiện thanh dính đáy trong Compare + đồng bộ với tab | Đúng dáng wireframe | ui |

### Khánh
| # | Issue | Acceptance criteria chính | Label |
| --- | --- | --- | --- |
| 3.5 | Code rule engine theo công thức 2.10 + pytest cho từng rule | Test pass các hồ sơ biên (IELTS thiếu 0.5, ngân sách sát nút…) | ai |
| 3.6 | Wizard 4 bước thu thập hồ sơ (Học lực → Chứng chỉ → Ngân sách → Ưu tiên) — logic + validate từng bước | Không cho qua bước khi input sai | ai |

### Nam Anh
| # | Issue | Acceptance criteria chính | Label |
| --- | --- | --- | --- |
| 3.7 | `ChatbotView`: thanh tiến trình 4 bước + chat bubble + card kết quả kèm % (wireframe 7) | Nối với rule engine của Khánh, hiển thị top N | ui |
| 3.8 | (Nếu kịp) L2 AI explanation: gọi API, cache vào `ai_cache`, fallback khi lỗi mạng | Rớt mạng → vẫn hiện kết quả L1, không crash | ai |

**☑ Checkpoint cuối tuần 3:** chatbot chạy được luồng wizard → kết quả;
chart hiển thị trong Compare. Quyết định go/no-go cho 3.8 và RAG (mặc định: bỏ RAG).

---

## Tuần 4 — Tích hợp, test, đóng gói

| # | Issue | Người | Acceptance criteria chính |
| --- | --- | --- | --- |
| 4.1 | Tích hợp toàn bộ + test end-to-end theo kịch bản (ghi lại kịch bản test thủ công) | Dương | Đi hết 3 luồng: tra cứu→lưu→so sánh; admin CRUD; chatbot |
| 4.2 | Polish UI: thống nhất bootstyle, spacing, edge case (danh sách rỗng, mất kết nối Mongo) | Huy | Màn rỗng có thông báo hướng dẫn, không traceback |
| 4.3 | Test chatbot, sửa bug logic điểm số | Khánh | Không còn case điểm âm/quá 100/chia 0 |
| 4.4 | Tích hợp cuối + viết SRS + slide demo | Nam Anh | SRS đủ yêu cầu chức năng/phi chức năng |
| 4.5 | Freeze code trước deadline ≥2 ngày, chỉ merge bugfix | Cả nhóm | Nhánh `main` luôn demo được |

---

## Bảng rủi ro → hành động trong plan (từ mục 10 tài liệu)

| Rủi ro | Được xử lý ở Issue |
| --- | --- |
| Chart đơ do threading | 2.7 prototype sớm (tuần 2), quy tắc main-thread trong ARCHITECTURE.md §5.4 |
| Đổi hợp đồng Repository giữa chừng | 1.0b khóa interface; mọi thay đổi phải qua họp (ghi ở đầu PLAN) |
| Dữ liệu nhập tay sai định dạng | 1.1 validate_data.py chạy trước 2.2 seed |
| Optional lấn core | Checkpoint cuối tuần 2 + quy tắc "xong core mới làm optional" |

## Definition of Done (áp cho mọi Issue)

1. Chạy được từ App Shell, không lỗi.
2. Có ≥1 test case pytest hoặc kịch bản test thủ công ghi trong PR.
3. 1 người khác review & approve, CI xanh.
4. Không còn hard-code dữ liệu mẫu.
