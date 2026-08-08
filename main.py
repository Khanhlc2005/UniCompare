"""Entry point UniCompare.
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
