"""Entry point UniCompare.

Dependency injection thủ công theo ARCHITECTURE.md §3:
- Tuần 1: repo = FakeRepo()                      (Issue 1.0b — Nam Anh)
- Tuần 2: repo = MongoRepo(config.MONGO_URI)      (Issue 2.3 — đổi đúng 1 dòng)
AppShell + sidebar: Issue 1.9 (Nam Anh).
"""

import config


def main() -> None:
    if not config.has_mongo():
        print(config.mongo_hint())

    # --- Khởi tạo repository (đổi 1 dòng ở tuần 2, Issue 2.3) ---
    # from repositories.fake_repo import FakeRepo          # Issue 1.0b
    # repo = FakeRepo()
    # repo = MongoRepo(config.MONGO_URI)                   # Tuần 2

    # --- Khởi tạo service (nhận repo qua constructor) ---
    # uni_service = UniversityService(repo)                # Issue 1.4

    # --- Khởi tạo AppShell (ttkbootstrap Window) ---
    # from app_shell import AppShell                       # Issue 1.9
    # app = AppShell(uni_service, ...)
    # app.mainloop()

    print("UniCompare — setup OK. Chờ Issue 1.0b (fake_repo) và 1.9 (AppShell).")


if __name__ == "__main__":
    main()
