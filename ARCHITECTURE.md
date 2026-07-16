# ARCHITECTURE.md — UniCompare

Ứng dụng desktop so sánh yêu cầu đầu vào các trường đại học nước ngoài.
Tài liệu này cụ thể hóa kiến trúc đã chốt trong **Tài liệu tổng hợp dự án** (mục 4, 5)
và bộ wireframe `University_Browser_Wireframes-print.pdf` (8 màn hình).
Mọi thay đổi kiến trúc phải được thống nhất trong họp nhóm trước khi thực hiện
(xem mục Rủi ro — "Hợp đồng Repository đổi giữa chừng").

---

## 1. Tech stack (đã chốt)

| Thành phần | Công nghệ | Ghi chú |
| --- | --- | --- |
| Ngôn ngữ | Python 3.11 | Khớp CI (`.github/workflows/test.yml`) |
| UI | **tkinter.ttk + ttkbootstrap** | ttk là bắt buộc; ttkbootstrap phủ theme lên trên, code widget vẫn là ttk |
| CSDL | MongoDB (pymongo) | Collection `universities`, `ai_cache`, `watchlist` |
| Biểu đồ | matplotlib (`FigureCanvasTkAgg`) | Nhúng vào màn So sánh |
| AI (optional) | Rule-based scoring (L1) + AI API explanation (L2) | RAG chỉ là stretch goal |
| Test | pytest | Chạy tự động qua GitHub Actions khi mở PR vào `main` |
| Cấu hình | `.env` (python-dotenv) | `MONGO_URI`, `API_KEY` — không commit `.env` |

`requirements.txt` tối thiểu:

```
ttkbootstrap
pymongo
matplotlib
python-dotenv
```

(Thêm `requests` hoặc SDK AI khi Nam Anh làm L2 explanation.)

---

## 2. Kiến trúc phân lớp

Giữ nguyên 3 lớp đã chốt. Quy tắc vàng: **lớp trên chỉ gọi lớp ngay dưới,
không gọi vượt cấp, không gọi ngược lên.** UI không bao giờ chạm pymongo.

```
+---------------------------------------------------------------+
|                      TKINTER UI LAYER (views/)                |
|  HomeView | WatchlistView | SearchView | DetailView           |
|  CompareView (+tab Chart) | ChatbotView | AdminView (riêng)   |
|  AppShell: sidebar điều hướng + quản lý frame                 |
+------------------------------+--------------------------------+
                               v
+---------------------------------------------------------------+
|                     SERVICE LAYER (services/)                 |
|  university_service   : tra cứu, tìm kiếm, chi tiết           |
|  compare_service      : chọn 2–5 trường, dữ liệu bảng/chart   |
|  watchlist_service    : lưu / bỏ lưu trường                   |
|  recommend_service    : L1 rule engine (+ L2 AI explanation)  |
+------------------------------+--------------------------------+
                               v
+---------------------------------------------------------------+
|                   REPOSITORY LAYER (repositories/)            |
|  university_repo (interface)                                  |
|   ├── fake_repo   (tuần 1–2, ~8 trường mẫu)                   |
|   └── mongo_repo  (thật, từ tuần 2 — đổi 1 dòng import)       |
+------------------------------+--------------------------------+
                               v
              MongoDB: universities / ai_cache / watchlist
```

### Cấu trúc thư mục

```
unicompare/
├── main.py                  # entry point: load .env, khởi tạo AppShell
├── app_shell.py             # cửa sổ chính + sidebar + chuyển frame
├── config.py                # đọc MONGO_URI, API_KEY từ .env
├── views/
│   ├── home_view.py
│   ├── watchlist_view.py
│   ├── search_view.py
│   ├── detail_view.py
│   ├── compare_view.py      # gồm 2 tab: bảng + biểu đồ
│   ├── chatbot_view.py
│   ├── admin_view.py
│   └── components/          # widget dùng chung: UniversityCard, PillFilter,
│                            # StatCard, StickyCompareBar, ChatBubble
├── services/
│   ├── university_service.py
│   ├── compare_service.py
│   ├── watchlist_service.py
│   └── recommend_service.py
├── repositories/
│   ├── university_repo.py   # interface (Protocol/ABC)
│   ├── fake_repo.py
│   └── mongo_repo.py
├── data/
│   └── seed_data.json       # 20–30 trường, nạp bằng scripts/seed.py
├── scripts/
│   ├── seed.py              # validate + nạp seed vào Mongo
│   └── validate_data.py     # script validate (mục Rủi ro: dữ liệu nhập tay sai)
└── tests/
    ├── test_fake_repo.py
    ├── test_university_service.py
    └── test_recommend_service.py
```

---

## 3. Hợp đồng Repository (đã chốt — không tự ý đổi)

```python
def get_all() -> list[dict]: ...
def get_by_id(id: str) -> dict | None: ...
def search(keyword: str = "", country: str = None) -> list[dict]: ...
def add(data: dict) -> str: ...
def update(id: str, data: dict) -> bool: ...
def delete(id: str) -> bool: ...
```

- `fake_repo.py` (Nam Anh viết trong 1–2 ngày đầu, ~8 trường mẫu) — cả nhóm dùng ngay từ tuần 1.
- `mongo_repo.py` (Dương) cài đúng interface này; tuần 2 chỉ đổi 1 dòng import ở nơi khởi tạo service.
- Filter mở rộng (học phí, IELTS) xử lý ở **service layer** trên kết quả `search()`,
  để không phải đổi hợp đồng. Nếu về sau cần đẩy filter xuống Mongo vì hiệu năng,
  phải họp nhóm thống nhất trước.

### Khởi tạo (dependency injection thủ công tại `main.py`)

```python
# Tuần 1: repo = FakeRepo()
# Tuần 2: repo = MongoRepo(config.MONGO_URI)   # đổi đúng 1 dòng
uni_service = UniversityService(repo)
```

---

## 4. Schema dữ liệu

### Collection `universities`

Các trường bám theo wireframe (card, bảng so sánh, chi tiết):

```json
{
  "_id": "ObjectId",
  "name": "University of Manchester",
  "country": "Anh",
  "city": "Manchester",
  "ranking": 32,
  "tuition_per_year": 28000,
  "currency": "USD",
  "ielts_min": 6.5,
  "toefl_min": 90,
  "gpa_min": 3.0,
  "deadline": "2026-09-15",
  "scholarship": "Có, tối đa 50%",
  "majors": ["Computer Science", "Business"],
  "overview": "…",
  "admission_detail": "…",
  "tuition_detail": "…",
  "contact": {"website": "…", "email": "…"}
}
```

Quy ước: số liệu dùng để so sánh/lọc/chấm điểm (`tuition_per_year`, `ielts_min`,
`gpa_min`, `ranking`) **bắt buộc là number**, validate bằng `scripts/validate_data.py`
trước khi nạp.

### Collection `ai_cache` (Dương thiết kế — hạ tầng cho recommend_service)

```json
{
  "_id": "ObjectId",
  "profile_hash": "sha256 của hồ sơ người dùng",
  "result": [{"university_id": "…", "score": 87, "explanation": "…"}],
  "created_at": "ISODate"
}
```

Mục đích: cùng một hồ sơ không gọi lại AI API — tiết kiệm quota, phản hồi nhanh.

### Collection `watchlist` *(đề xuất mới — tài liệu tổng hợp chưa chốt nơi lưu)*

App single-user nên chỉ cần lưu danh sách id:
`{"university_id": "…", "saved_at": ISODate}`. Phương án thay thế là file JSON local,
nhưng lưu vào Mongo đồng nhất với repository pattern và thỏa DoD
"không còn hard-code dữ liệu mẫu". **Cần chốt trong họp nhóm tuần 1.**

---

## 5. UI Layer

### 5.1. App Shell & Frame contract (đã chốt)

```python
class SearchView(ttk.Frame):
    def __init__(self, master, controller): ...
```

- `AppShell` tạo cửa sổ chính, sidebar trái, và 1 container; mỗi View là một
  `ttk.Frame` con, hiển thị bằng `tkraise()`.
- `controller` là chính AppShell — cung cấp: `show_frame(name, **kwargs)`
  (VD: `show_frame("detail", university_id=...)`), và các service đã khởi tạo.
- Mỗi View có phương thức `refresh()` được gọi khi frame được đưa lên,
  để dữ liệu luôn mới (VD: Watchlist cập nhật sau khi lưu trường ở màn khác).

### 5.2. Bản đồ wireframe → View (nguồn chân lý cho UI)

| Trang wireframe | View | Điểm chính phải làm đúng |
| --- | --- | --- |
| 1. Trang chủ | `HomeView` | 3 StatCard tổng quan, lối tắt, danh sách trường nổi bật dạng card |
| 2. Quan tâm | `WatchlistView` | PillFilter quốc gia, card có nút bỏ lưu, **StickyCompareBar "X/5 đã chọn"** |
| 3. Tìm kiếm | `SearchView` | Search bar + 3 nhóm pill (Quốc gia / Học phí / IELTS), card grid |
| 4. Chi tiết | `DetailView` | Banner, 4 StatCard nổi bật, mục lục trái + nội dung phải |
| 5–6. So sánh | `CompareView` | Chip trường (bỏ được), bảng highlight giá trị tốt nhất, tab Bảng/Biểu đồ |
| 7. Chatbot | `ChatbotView` | Thanh tiến trình wizard 4 bước + chat bubble + card kết quả kèm % phù hợp |
| 8. Admin | `AdminView` | Treeview + form thêm/sửa cạnh bên, validate input, màn riêng ngoài luồng chính |

Trạng thái "đã chọn để so sánh" là **state dùng chung** (Home, Search, Watchlist,
Detail đều có nút thêm so sánh) → đặt trong `compare_service`
(danh sách tối đa 5 id), các View đọc/ghi qua service, không giữ bản sao riêng.

### 5.3. Quy ước ttkbootstrap

- Theme thống nhất toàn app, khai báo **một chỗ duy nhất** trong `app_shell.py`:
  `ttkbootstrap.Window(themename="flatly")` (nhóm có thể vote theme khác, nhưng đổi 1 dòng).
- Dùng `bootstyle` chuẩn: `primary` cho hành động chính, `success` cho highlight
  giá trị tốt nhất trong bảng so sánh, `secondary/outline` cho pill filter chưa chọn.
- Pill filter = `ttk.Radiobutton`/`Checkbutton` với `bootstyle="toolbutton"` — đúng dáng wireframe.
- Widget lặp lại ở nhiều màn (card trường, stat card, pill, thanh dính đáy, chat bubble)
  bắt buộc viết trong `views/components/` — cấm mỗi người tự vẽ một kiểu.

### 5.4. Nhúng matplotlib (né rủi ro threading — mục 10 tài liệu)

- Chart vẽ bằng `FigureCanvasTkAgg` **trong main thread**. Không dùng `plt.show()`,
  không tạo Figure trong thread phụ.
- Khi đổi tiêu chí/danh sách trường: xóa dữ liệu axes cũ (`ax.clear()`) và
  `canvas.draw_idle()` — không tạo Figure mới liên tục (rò rỉ bộ nhớ).
- Nếu về sau có tác vụ chậm (gọi AI API), chạy trong `threading.Thread` nhưng
  **cập nhật UI qua `widget.after(...)`** — tuyệt đối không đụng widget từ thread phụ.
- Huy prototype riêng phần chart ngay tuần 2, đúng chiến lược né rủi ro đã chốt.

---

## 6. Chatbot gợi ý trường (optional — phạm vi đã chốt)

Kiến trúc 2 tầng, tầng nào hỏng thì fallback tầng dưới:

**L1 — Rule-based scoring (Khánh, luôn chạy nếu bật chatbot):**
Wizard 4 bước thu thập hồ sơ (Học lực → Chứng chỉ → Ngân sách → Ưu tiên) →
`recommend_service.score(profile)` chấm từng trường 0–100 theo trọng số
(VD: đạt IELTS tối thiểu, GPA đủ, học phí trong ngân sách, cộng điểm ưu tiên
quốc gia/ngành) → trả top N kèm % phù hợp. Thuần Python, không cần mạng,
test được bằng pytest.

**L2 — AI explanation (Nam Anh, optional, cần `API_KEY`):**
Nhận top N từ L1, gọi AI API sinh lời giải thích ngắn vì sao trường phù hợp.
Kết quả cache vào `ai_cache` theo `profile_hash`. Lỗi mạng/hết quota →
hiển thị kết quả L1 không kèm giải thích, app không được crash.

**RAG/vector search:** stretch goal, chỉ ghi nhận, **không thiết kế trước** —
tránh rủi ro "optional lấn thời gian core" (mục 10).

---

## 7. Cấu hình, test, CI

- `config.py` đọc `.env` qua python-dotenv; thiếu `MONGO_URI` → thông báo rõ
  và gợi ý dùng fake_repo, không crash khó hiểu.
- Test đặt trong `tests/`, ưu tiên test lớp service + repo (logic thuần, không cần UI):
  fake_repo CRUD, search/filter, công thức chấm điểm rule-based.
- CI (đã có sẵn): mỗi PR vào `main` chạy `pip install -r requirements.txt` + pytest.
  → **Mọi thư viện mới phải vào `requirements.txt` ngay trong PR đó**, nếu không CI đỏ.
- Quy trình Git/Issue/PR theo README: branch từ Issue, Conventional Commits,
  PR ghi `Closes #N`, 1 người review, CI xanh, Squash and merge.

## 8. Definition of Done (nhắc lại từ tài liệu tổng hợp)

1. Chạy được độc lập từ App Shell, không lỗi.
2. Có ít nhất 1 test case / kịch bản test thủ công ghi lại.
3. Được 1 người khác review & approve PR.
4. Không còn hard-code dữ liệu mẫu.
