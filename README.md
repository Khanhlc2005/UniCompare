# UniCompare

# Quy trình làm 1 task

1. Mở Issue được giao → bấm "Create a branch" (link ở sidebar phải của Issue) → GitHub tự đặt tên nhánh kiểu 12-them-man-hinh-search và tự liên kết với Issue.
2. Về máy: git fetch && git checkout <tên-nhánh-vừa-tạo>.
3. Code, commit theo chuẩn Conventional Commits:


   git commit -m "feat: them man hinh tim kiem"


4. Push: git push origin <tên-nhánh>.
5. Trên GitHub, bấm Compare & pull request. Trong mô tả PR, ghi dòng:


   Closes #12

(số 12 là số Issue) — dòng này giúp Issue tự đóng và tự chuyển Done khi PR được merge.
6. Nhờ 1 bạn khác review, approve.
7. Chờ CI (Bước 6) chạy xanh → bấm Squash and merge.
8. Xoá nhánh (GitHub tự gợi ý nút "Delete branch" ngay sau khi merge).


# Tạo Issue cho từng task 

Với mỗi dòng trong bảng WBS tuần 1 (VD: "Dev 1: viết fake_repo + schema"):
Issues → New issue, chọn template Task.
Điền acceptance criteria cụ thể cho task đó.
Gắn label đúng (data/ui/ai), gắn Milestone = Sprint 1 - Tuần 1.
Thêm vào Project board