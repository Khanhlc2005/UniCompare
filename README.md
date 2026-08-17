# UniCompare

UniCompare là ứng dụng desktop hỗ trợ tìm kiếm, lưu và so sánh các trường đại
học quốc tế. Ứng dụng tổng hợp thông tin học thuật, học phí, yêu cầu đầu vào và
trình bày dữ liệu dưới dạng bảng cùng biểu đồ để người dùng đưa ra lựa chọn phù
hợp hơn.

Ứng dụng được viết bằng Python, sử dụng Tkinter/ttkbootstrap cho giao diện,
MongoDB cho dữ liệu và Matplotlib cho phần trực quan hóa.

## Tính năng chính

- Tìm kiếm trường theo tên, quốc gia, học phí và yêu cầu IELTS.
- Xem thông tin chi tiết, ngành học, học bổng và thời hạn nộp hồ sơ.
- Lưu các trường quan tâm và chọn tối đa 5 trường để so sánh.
- So sánh chỉ số bằng bảng, biểu đồ học phí và biểu đồ IELTS/TOEFL.
- Gợi ý trường bằng hệ thống chấm điểm rule-based theo hồ sơ người dùng.
- Tạo phần giải thích bằng Gemini API khi có API key.
- Quản lý dữ liệu trường qua màn hình Admin.

## Yêu cầu hệ thống

- Python 3.11 trở lên.
- Tkinter, thường được cài sẵn cùng Python trên Windows và macOS.
- MongoDB local hoặc MongoDB Atlas nếu muốn sử dụng dữ liệu và watchlist lâu
  dài. MongoDB không bắt buộc để chạy thử ứng dụng.

Trên Ubuntu/Debian, cài Tkinter nếu hệ thống chưa có:

```bash
sudo apt install python3-tk
```

## Cài đặt

Tạo môi trường ảo tại thư mục dự án:

```bash
python -m venv .venv
```

Kích hoạt môi trường trên Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Trên macOS hoặc Linux:

```bash
source .venv/bin/activate
```

Cài các thư viện cần thiết:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Cấu hình

Ứng dụng vẫn chạy được khi không có file `.env`. Trong trường hợp đó, dữ liệu
mẫu từ `data/seed_data.json` được đọc qua `FakeRepo` và tính năng gợi ý vẫn hoạt
động bằng rule engine.

Để sử dụng MongoDB hoặc phần giải thích AI, tạo `.env` từ file mẫu:

```powershell
Copy-Item .env.example .env
```

Trên macOS hoặc Linux:

```bash
cp .env.example .env
```

Các biến cấu hình hỗ trợ:

```dotenv
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=unicompare
GEMINI_API_KEY=
```

- `MONGO_URI`: chuỗi kết nối MongoDB local hoặc MongoDB Atlas.
- `MONGO_DB_NAME`: tên database, mặc định là `unicompare`.
- `GEMINI_API_KEY`: khóa API dùng cho phần giải thích và hội thoại AI. Có thể
  dùng tên `API_KEY` thay thế.

File `.env` đã được loại khỏi Git và không nên được commit.

## Nạp dữ liệu vào MongoDB

Sau khi cấu hình `MONGO_URI`, kiểm tra và nạp dữ liệu mẫu bằng lệnh:

```bash
python scripts/seed.py
```

Script sẽ kiểm tra schema trước khi ghi và dùng upsert theo `id`, vì vậy có thể
chạy lại để cập nhật dữ liệu hiện có.

Nếu MongoDB không kết nối được, ứng dụng tự chuyển sang `FakeRepo` để tiếp tục
chạy. Các thay đổi trong chế độ này chỉ có hiệu lực trong phiên làm việc hiện
tại.

## Chạy ứng dụng

```bash
python main.py
```

Luồng sử dụng cơ bản:

1. Mở trang Tìm kiếm để tra cứu và lọc trường.
2. Lưu trường vào danh sách Quan tâm hoặc chọn trường để so sánh.
3. Mở trang So sánh để xem bảng chỉ số và biểu đồ.
4. Mở mục Gợi ý để nhập hồ sơ và nhận danh sách trường phù hợp.
5. Mở `Quản trị > Mở màn Quản trị` để thêm, sửa hoặc xóa dữ liệu trường.

## Chạy kiểm thử

Cài `pytest` nếu môi trường chưa có:

```bash
python -m pip install pytest
```

Chạy toàn bộ test:

```bash
python -m pytest -q
```

## Cấu trúc dự án

```text
UniCompare/
├── main.py              Điểm khởi chạy ứng dụng
├── config.py            Đọc cấu hình từ môi trường
├── views/               Giao diện Tkinter và các component
├── services/            Tìm kiếm, so sánh, watchlist và gợi ý
├── repositories/        FakeRepo và MongoDB repository
├── data/                Dữ liệu trường mẫu
├── scripts/             Validate và seed dữ liệu
├── tests/               Bộ kiểm thử pytest
└── docs/                Tài liệu nghiệp vụ và kỹ thuật
```

Thiết kế tổng thể được mô tả trong `ARCHITECTURE.md`; kế hoạch phát triển và
phạm vi tính năng nằm trong `PLAN.md`.

## Xử lý lỗi thường gặp

`python` không được nhận diện:

- Kiểm tra Python đã được thêm vào `PATH` hoặc sử dụng `py -3.11` trên Windows.

Ứng dụng báo không kết nối được MongoDB:

- Kiểm tra `MONGO_URI`, tài khoản, mật khẩu và danh sách IP được phép truy cập
  trên MongoDB Atlas. Ứng dụng vẫn có thể chạy bằng dữ liệu mẫu.

Giao diện không khởi động trên Linux:

- Cài gói `python3-tk` và chạy lại ứng dụng trong môi trường có desktop.

Phần giải thích AI không hoạt động:

- Kiểm tra `GEMINI_API_KEY` hoặc `API_KEY` trong `.env` và kết nối mạng.
