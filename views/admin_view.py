from __future__ import annotations

import importlib
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, ttk
from typing import Any, Protocol


Document = dict[str, Any]


class UniversityRepository(Protocol):
    def get_all(self) -> list[Document]: ...
    def add(self, data: Document) -> str: ...
    def update(self, university_id: str, data: Document) -> bool: ...
    def delete(self, university_id: str) -> bool: ...


@dataclass(frozen=True)
class FormField:
    key: str
    label: str
    required: bool = False


FORM_FIELDS = (
    FormField("name", "Tên trường", True),
    FormField("country", "Quốc gia", True),
    FormField("city", "Thành phố"),
    FormField("university_type", "Loại hình"),
    FormField("qs_rank", "Xếp hạng QS"),
    FormField("tuition_usd", "Học phí/năm (USD)"),
    FormField("ielts_min", "IELTS tối thiểu"),
    FormField("employment_rate", "Tỷ lệ việc làm (%)"),
    FormField("application_deadline", "Hạn nộp hồ sơ"),
)


class AdminView(ttk.Frame):
    """Frame quản trị dữ liệu trường đại học."""

    TREE_COLUMNS = (
        "name",
        "country",
        "qs_rank",
        "tuition_usd",
        "ielts_min",
    )

    def __init__(
        self,
        master: tk.Misc,
        repository: UniversityRepository | Any,
    ) -> None:
        super().__init__(master, padding=18)
        self.repository = repository
        self.selected_id: str | None = None
        self._documents_by_id: dict[str, Document] = {}
        self.form_vars: dict[str, tk.StringVar] = {
            field.key: tk.StringVar() for field in FORM_FIELDS
        }
        self.status_var = tk.StringVar(value="Sẵn sàng")

        self._configure_style()
        self._build_ui()
        self.refresh_tree()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _configure_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Admin.TFrame", background="#F5F7FB")
        style.configure(
            "Header.TLabel",
            background="#F5F7FB",
            foreground="#1A237E",
            font=("Segoe UI", 18, "bold"),
        )
        style.configure(
            "Subheader.TLabel",
            background="#F5F7FB",
            foreground="#5F6675",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Card.TLabelframe",
            background="#FFFFFF",
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "Card.TLabelframe.Label",
            background="#FFFFFF",
            foreground="#1A237E",
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "Card.TFrame",
            background="#FFFFFF",
        )
        style.configure(
            "Form.TLabel",
            background="#FFFFFF",
            foreground="#20242E",
            font=("Segoe UI", 9),
        )
        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 9, "bold"),
            foreground="#FFFFFF",
            background="#008080",
            padding=(12, 8),
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#006C6C"), ("pressed", "#005B5B")],
        )
        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 9),
            padding=(12, 8),
        )
        style.configure(
            "Danger.TButton",
            font=("Segoe UI", 9, "bold"),
            foreground="#FFFFFF",
            background="#9D2A2A",
            padding=(12, 8),
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#7F1F1F"), ("pressed", "#681919")],
        )
        style.configure(
            "Treeview",
            rowheight=30,
            font=("Segoe UI", 9),
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            foreground="#1A237E",
        )

        self.configure(style="Admin.TFrame")

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)

        ttk.Label(self, text="Quản trị trường đại học", style="Header.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            self,
            text="Thêm, sửa và xóa dữ liệu. Thay đổi được phản ánh ngay trên danh sách.",
            style="Subheader.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 14))

        self._build_tree_panel()
        self._build_form_panel()

        status = ttk.Label(
            self,
            textvariable=self.status_var,
            anchor="w",
            foreground="#5F6675",
        )
        status.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def _build_tree_panel(self) -> None:
        panel = ttk.LabelFrame(
            self,
            text="Danh sách trường",
            style="Card.TLabelframe",
            padding=12,
        )
        panel.grid(row=2, column=0, sticky="nsew", padx=(0, 10))
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(panel, style="Card.TFrame")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        toolbar.columnconfigure(0, weight=1)

        ttk.Label(
            toolbar,
            text="Chọn một dòng để sửa hoặc xóa.",
            style="Form.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(
            toolbar,
            text="Làm mới",
            style="Secondary.TButton",
            command=self.refresh_tree,
        ).grid(row=0, column=1, sticky="e")

        tree_container = ttk.Frame(panel, style="Card.TFrame")
        tree_container.grid(row=1, column=0, sticky="nsew")
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            tree_container,
            columns=self.TREE_COLUMNS,
            show="headings",
            selectmode="browse",
        )

        headings = {
            "name": "Tên trường",
            "country": "Quốc gia",
            "qs_rank": "QS",
            "tuition_usd": "Học phí",
            "ielts_min": "IELTS",
        }
        widths = {
            "name": 260,
            "country": 120,
            "qs_rank": 70,
            "tuition_usd": 105,
            "ielts_min": 70,
        }

        for column in self.TREE_COLUMNS:
            self.tree.heading(column, text=headings[column])
            self.tree.column(
                column,
                width=widths[column],
                minwidth=60,
                anchor="w" if column in {"name", "country"} else "center",
            )

        y_scroll = ttk.Scrollbar(
            tree_container, orient="vertical", command=self.tree.yview
        )
        x_scroll = ttk.Scrollbar(
            tree_container, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
        )

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _build_form_panel(self) -> None:
        panel = ttk.LabelFrame(
            self,
            text="Thông tin trường",
            style="Card.TLabelframe",
            padding=14,
        )
        panel.grid(row=2, column=1, sticky="nsew", padx=(10, 0))
        panel.columnconfigure(0, weight=1)

        form = ttk.Frame(panel, style="Card.TFrame")
        form.grid(row=0, column=0, sticky="nsew")
        form.columnconfigure(0, weight=1)

        for row_index, field in enumerate(FORM_FIELDS):
            label = field.label + (" *" if field.required else "")
            ttk.Label(form, text=label, style="Form.TLabel").grid(
                row=row_index * 2,
                column=0,
                sticky="w",
                pady=(0 if row_index == 0 else 8, 3),
            )
            ttk.Entry(
                form,
                textvariable=self.form_vars[field.key],
            ).grid(
                row=row_index * 2 + 1,
                column=0,
                sticky="ew",
            )

        button_bar = ttk.Frame(panel, style="Card.TFrame")
        button_bar.grid(row=1, column=0, sticky="ew", pady=(16, 0))
        for index in range(2):
            button_bar.columnconfigure(index, weight=1)

        ttk.Button(
            button_bar,
            text="Thêm mới",
            style="Primary.TButton",
            command=self.add_university,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=(0, 6))

        ttk.Button(
            button_bar,
            text="Cập nhật",
            style="Secondary.TButton",
            command=self.update_university,
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=(0, 6))

        ttk.Button(
            button_bar,
            text="Xóa",
            style="Danger.TButton",
            command=self.delete_university,
        ).grid(row=1, column=0, sticky="ew", padx=(0, 5))

        ttk.Button(
            button_bar,
            text="Xóa form",
            style="Secondary.TButton",
            command=self.clear_form,
        ).grid(row=1, column=1, sticky="ew", padx=(5, 0))

    # ------------------------------------------------------------------
    # Repository helpers
    # ------------------------------------------------------------------
    def _call_repo(self, method_name: str, *args: Any) -> Any:
        method = getattr(self.repository, method_name, None)
        if not callable(method):
            raise AttributeError(
                f"Repository chưa có hàm {method_name}(). "
                "Hãy kiểm tra repository contract."
            )
        return method(*args)

    @staticmethod
    def _document_id(document: Document) -> str:
        value = document.get("_id", document.get("id", ""))
        return str(value).strip()

    @staticmethod
    def _display_value(value: Any) -> str:
        if value is None:
            return ""
        return str(value)

    @staticmethod
    def _format_tuition(value: Any) -> str:
        if value in (None, ""):
            return ""
        try:
            return f"${float(value):,.0f}"
        except (TypeError, ValueError):
            return str(value)

    # ------------------------------------------------------------------
    # Tree operations
    # ------------------------------------------------------------------
    def refresh_tree(self, select_id: str | None = None) -> None:
        try:
            documents = self._call_repo("get_all")
            if documents is None:
                documents = []
            if not isinstance(documents, list):
                documents = list(documents)

            for item_id in self.tree.get_children():
                self.tree.delete(item_id)

            self._documents_by_id.clear()
            selected_item: str | None = None

            for index, document in enumerate(documents):
                if not isinstance(document, dict):
                    continue

                document_id = self._document_id(document)
                if not document_id:
                    # Fake repo cũ đôi khi không có id; vẫn cho phép hiển thị.
                    document_id = f"row-{index}"

                self._documents_by_id[document_id] = dict(document)

                item_id = self.tree.insert(
                    "",
                    "end",
                    values=(
                        self._display_value(
                            document.get("name", document.get("university_name", ""))
                        ),
                        self._display_value(document.get("country", "")),
                        self._display_value(
                            document.get("qs_rank", document.get("rank", ""))
                        ),
                        self._format_tuition(
                            document.get("tuition_usd", document.get("tuition", ""))
                        ),
                        self._display_value(
                            document.get("ielts_min", document.get("ielts", ""))
                        ),
                    ),
                    tags=(document_id,),
                )

                if select_id and document_id == str(select_id):
                    selected_item = item_id

            if selected_item:
                self.tree.selection_set(selected_item)
                self.tree.focus(selected_item)
                self.tree.see(selected_item)

            self.status_var.set(f"Đã tải {len(self._documents_by_id)} trường.")
        except Exception as exc:
            self.status_var.set("Không thể tải dữ liệu.")
            messagebox.showerror("Lỗi tải dữ liệu", str(exc), parent=self.winfo_toplevel())

    def _selected_document_id(self) -> str | None:
        selection = self.tree.selection()
        if not selection:
            return None
        tags = self.tree.item(selection[0], "tags")
        return str(tags[0]) if tags else None

    def _on_tree_select(self, _event: tk.Event[Any] | None = None) -> None:
        document_id = self._selected_document_id()
        if not document_id:
            return

        document = self._documents_by_id.get(document_id)
        if not document:
            return

        self.selected_id = document_id

        aliases = {
            "name": ("name", "university_name"),
            "country": ("country",),
            "city": ("city",),
            "university_type": ("university_type", "type"),
            "qs_rank": ("qs_rank", "rank"),
            "tuition_usd": ("tuition_usd", "tuition"),
            "ielts_min": ("ielts_min", "ielts"),
            "employment_rate": ("employment_rate",),
            "application_deadline": ("application_deadline", "deadline"),
        }

        for field_key, possible_keys in aliases.items():
            value = ""
            for possible_key in possible_keys:
                if possible_key in document:
                    value = document.get(possible_key, "")
                    break
            self.form_vars[field_key].set(self._display_value(value))

        self.status_var.set(f"Đang chọn: {self.form_vars['name'].get() or document_id}")

    # ------------------------------------------------------------------
    # Form and validation
    # ------------------------------------------------------------------
    def clear_form(self) -> None:
        for variable in self.form_vars.values():
            variable.set("")
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())
        self.status_var.set("Đã xóa nội dung form.")

    @staticmethod
    def _to_optional_int(raw_value: str, field_label: str) -> int | None:
        value = raw_value.strip()
        if not value:
            return None
        try:
            number = int(value.replace(",", "").replace("#", ""))
        except ValueError as exc:
            raise ValueError(f"{field_label} phải là số nguyên.") from exc
        if number < 0:
            raise ValueError(f"{field_label} không được âm.")
        return number

    @staticmethod
    def _to_optional_float(raw_value: str, field_label: str) -> float | None:
        value = raw_value.strip()
        if not value:
            return None
        try:
            number = float(value.replace(",", ""))
        except ValueError as exc:
            raise ValueError(f"{field_label} phải là số.") from exc
        if number < 0:
            raise ValueError(f"{field_label} không được âm.")
        return number

    def _read_form(self) -> Document:
        name = self.form_vars["name"].get().strip()
        country = self.form_vars["country"].get().strip()

        if not name:
            raise ValueError("Tên trường là trường bắt buộc.")
        if not country:
            raise ValueError("Quốc gia là trường bắt buộc.")

        qs_rank = self._to_optional_int(
            self.form_vars["qs_rank"].get(), "Xếp hạng QS"
        )
        tuition = self._to_optional_float(
            self.form_vars["tuition_usd"].get(), "Học phí"
        )
        ielts = self._to_optional_float(
            self.form_vars["ielts_min"].get(), "IELTS tối thiểu"
        )
        employment = self._to_optional_float(
            self.form_vars["employment_rate"].get(), "Tỷ lệ việc làm"
        )

        if ielts is not None and ielts > 9:
            raise ValueError("IELTS phải nằm trong khoảng 0 đến 9.")
        if employment is not None and employment > 100:
            raise ValueError("Tỷ lệ việc làm phải nằm trong khoảng 0 đến 100.")

        payload: Document = {
            "name": name,
            "country": country,
            "city": self.form_vars["city"].get().strip(),
            "university_type": self.form_vars["university_type"].get().strip(),
            "application_deadline": self.form_vars[
                "application_deadline"
            ].get().strip(),
        }

        optional_values = {
            "qs_rank": qs_rank,
            "tuition_usd": tuition,
            "ielts_min": ielts,
            "employment_rate": employment,
        }
        payload.update(
            {key: value for key, value in optional_values.items() if value is not None}
        )

        # Không lưu các chuỗi tùy chọn rỗng.
        return {
            key: value
            for key, value in payload.items()
            if value not in ("", None)
        }

    # ------------------------------------------------------------------
    # CRUD callbacks
    # ------------------------------------------------------------------
    def add_university(self) -> None:
        try:
            payload = self._read_form()
            new_id = self._call_repo("add", payload)
            self.refresh_tree(select_id=str(new_id))
            self.status_var.set(f"Đã thêm: {payload['name']}")
            messagebox.showinfo(
                "Thành công",
                "Đã thêm trường mới.",
                parent=self.winfo_toplevel(),
            )
        except Exception as exc:
            messagebox.showerror(
                "Không thể thêm",
                str(exc),
                parent=self.winfo_toplevel(),
            )

    def update_university(self) -> None:
        document_id = self.selected_id or self._selected_document_id()
        if not document_id:
            messagebox.showwarning(
                "Chưa chọn dữ liệu",
                "Hãy chọn một trường trên Treeview trước khi cập nhật.",
                parent=self.winfo_toplevel(),
            )
            return
        if document_id.startswith("row-"):
            messagebox.showerror(
                "Thiếu ID",
                "Bản ghi này không có id/_id nên không thể cập nhật. "
                "Hãy bổ sung id trong fake_repo.",
                parent=self.winfo_toplevel(),
            )
            return

        try:
            payload = self._read_form()
            updated = bool(self._call_repo("update", document_id, payload))
            if not updated:
                raise RuntimeError("Repository không tìm thấy bản ghi cần cập nhật.")

            self.refresh_tree(select_id=document_id)
            self.status_var.set(f"Đã cập nhật: {payload['name']}")
            messagebox.showinfo(
                "Thành công",
                "Đã cập nhật dữ liệu.",
                parent=self.winfo_toplevel(),
            )
        except Exception as exc:
            messagebox.showerror(
                "Không thể cập nhật",
                str(exc),
                parent=self.winfo_toplevel(),
            )

    def delete_university(self) -> None:
        document_id = self.selected_id or self._selected_document_id()
        if not document_id:
            messagebox.showwarning(
                "Chưa chọn dữ liệu",
                "Hãy chọn một trường trên Treeview trước khi xóa.",
                parent=self.winfo_toplevel(),
            )
            return
        if document_id.startswith("row-"):
            messagebox.showerror(
                "Thiếu ID",
                "Bản ghi này không có id/_id nên không thể xóa. "
                "Hãy bổ sung id trong fake_repo.",
                parent=self.winfo_toplevel(),
            )
            return

        university_name = self.form_vars["name"].get().strip() or document_id
        confirmed = messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa “{university_name}” không?",
            parent=self.winfo_toplevel(),
        )
        if not confirmed:
            return

        try:
            deleted = bool(self._call_repo("delete", document_id))
            if not deleted:
                raise RuntimeError("Repository không tìm thấy bản ghi cần xóa.")

            self.clear_form()
            self.refresh_tree()
            self.status_var.set(f"Đã xóa: {university_name}")
        except Exception as exc:
            messagebox.showerror(
                "Không thể xóa",
                str(exc),
                parent=self.winfo_toplevel(),
            )


def open_admin_window(
    parent: tk.Misc,
    repository: UniversityRepository | Any,
) -> tk.Toplevel:
    """Mở Admin trong cửa sổ riêng, tách khỏi điều hướng chính."""
    window = tk.Toplevel(parent)
    window.title("UniCompare — Admin")
    window.geometry("1180x720")
    window.minsize(980, 620)
    window.configure(background="#F5F7FB")

    view = AdminView(window, repository)
    view.pack(fill="both", expand=True)
    return window


# ----------------------------------------------------------------------
# Demo/test thủ công
# ----------------------------------------------------------------------
class MemoryUniversityRepository:
    """Fake repository tối giản để chạy thử riêng file AdminView."""

    def __init__(self) -> None:
        self._next_id = 4
        self._items: list[Document] = [
            {
                "id": "1",
                "name": "National University of Singapore",
                "country": "Singapore",
                "city": "Singapore",
                "university_type": "Công lập",
                "qs_rank": 8,
                "tuition_usd": 22000,
                "ielts_min": 7.5,
                "employment_rate": 96,
                "application_deadline": "2027-02-15",
            },
            {
                "id": "2",
                "name": "University of Melbourne",
                "country": "Australia",
                "city": "Melbourne",
                "university_type": "Công lập",
                "qs_rank": 14,
                "tuition_usd": 28500,
                "ielts_min": 7.0,
                "employment_rate": 88,
                "application_deadline": "2027-01-31",
            },
            {
                "id": "3",
                "name": "University of Toronto",
                "country": "Canada",
                "city": "Toronto",
                "university_type": "Công lập",
                "qs_rank": 21,
                "tuition_usd": 29000,
                "ielts_min": 6.5,
                "employment_rate": 90,
                "application_deadline": "2027-01-15",
            },
        ]

    def get_all(self) -> list[Document]:
        return [dict(item) for item in self._items]

    def add(self, data: Document) -> str:
        new_id = str(self._next_id)
        self._next_id += 1
        self._items.append({"id": new_id, **dict(data)})
        return new_id

    def update(self, university_id: str, data: Document) -> bool:
        for index, item in enumerate(self._items):
            if str(item.get("id")) == str(university_id):
                self._items[index] = {**item, **dict(data)}
                return True
        return False

    def delete(self, university_id: str) -> bool:
        for index, item in enumerate(self._items):
            if str(item.get("id")) == str(university_id):
                del self._items[index]
                return True
        return False


def _load_project_fake_repo() -> Any | None:
    """Tự tìm fake_repo khi chạy trong project.

    Hỗ trợ các vị trí phổ biến:
    - fake_repo.py
    - repositories/fake_repo.py
    - repository/fake_repo.py
    """
    module_names = (
        "fake_repo",
        "repositories.fake_repo",
        "repository.fake_repo",
    )

    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            continue

        # Nếu module có instance repository thì ưu tiên instance.
        repo_object = getattr(module, "repository", module)
        required_methods = ("get_all", "add", "update", "delete")
        if all(callable(getattr(repo_object, name, None)) for name in required_methods):
            return repo_object

    return None


def main() -> None:
    root = tk.Tk()
    root.title("UniCompare — AdminView Test")
    root.geometry("1180x720")
    root.minsize(980, 620)
    root.configure(background="#F5F7FB")

    repository = _load_project_fake_repo() or MemoryUniversityRepository()
    AdminView(root, repository).pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()
