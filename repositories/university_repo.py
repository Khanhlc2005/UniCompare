# -*- coding: utf-8 -*-
"""
university_repo.py - Repository interface DA CHOT trong ARCHITECTURE.md muc 3.
KHONG tu y doi chu ky ham nay - moi thay doi phai hop nhom thong nhat truoc
(xem ARCHITECTURE.md muc 10, rui ro "Hop dong Repository doi giua chung").

fake_repo.py va mongo_repo.py deu phai cai dung interface nay.
"""
from typing import Protocol, Optional


class UniversityRepo(Protocol):
    def get_all(self) -> list[dict]:
        """Tra ve toan bo danh sach truong (dung cho HomeView, Admin list...)."""
        ...

    def get_by_id(self, id: str) -> Optional[dict]:
        """Tra ve 1 truong theo id, hoac None neu khong tim thay (DetailView)."""
        ...

    def search(self, keyword: str = "", country: str | None = None) -> list[dict]:
        """Tim theo tu khoa (ten truong, co dau/khong dau) + loc theo quoc gia.
        Cac bo loc mo rong (hoc phi, IELTS...) xu ly o service layer tren
        ket qua tra ve tu ham nay, KHONG doi chu ky ham (xem ARCHITECTURE.md muc 3)."""
        ...

    def add(self, data: dict) -> str:
        """Them 1 truong moi, tra ve id vua tao (dung cho AdminView)."""
        ...

    def update(self, id: str, data: dict) -> bool:
        """Cap nhat 1 truong theo id, tra ve True/False."""
        ...

    def delete(self, id: str) -> bool:
        """Xoa 1 truong theo id, tra ve True/False."""
        ...
