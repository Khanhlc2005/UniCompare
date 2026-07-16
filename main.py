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

    # --- Khởi tạo AppShell (Tkinter Window) ---
    from views.app_shell import AppShell

    app = AppShell()
    app.mainloop()


if __name__ == "__main__":
    main()
