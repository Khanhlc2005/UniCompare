"""scripts/chart_prototype.py — prototype tab Bieu do CompareView, dung theo
quyet dinh muc 5.2.1 (thay wireframe 6, bo dropdown tieu chi):
    Chart 1: Hoc phi/nam quy doi VND       -> bar NGANG (barh)
    Chart 2: Yeu cau ngoai ngu (IELTS/TOEFL) -> grouped bar, 2 truc y (twinx)

Doc du lieu THAT tu data/seed_data.json (khong bia du lieu). KHONG dung
CompareView/compare_page.py that - day la prototype doc lap de validate ky
thuat truoc khi ghep vao Issue 3.3 (ARCHITECTURE.md muc 5.4).

Chay doc lap: python -m scripts.chart_prototype
"""
import json
import random
from pathlib import Path

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import ttkbootstrap as tb

SO_LAN_DOI = 10
DO_TRE_MS = 700  # doi giua moi lan de nhin thay chart cap nhat

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "seed_data.json"

# TY_GIA: tam thoi, chi de prototype chay duoc voi du lieu that.
# seed_data.json luu tuition_per_year theo dung currency cua tung nuoc
# (CNY/JPY/GBP/KRW), CHUA co san tuition_vnd. Quyet dinh 5.2.1 yeu cau
# tuition_vnd la so nguyen VND, ty gia CO DINH tai thoi diem seed va phai
# ghi ro ngay trong NGUON_DU_LIEU.md - viec nay la cua nguoi phu trach
# data, KHONG phai minh tu chon. Ty gia duoi day chi la placeholder de
# chart chay thu, PHAI thay bang so chinh thuc nhom chot truoc khi merge.
TY_GIA_TAM_THOI = {
    "CNY": 3900,
    "JPY": 163,
    "GBP": 35350,
    "KRW": 17.4,
}


def doc_du_lieu_that():
    """Doc data/seed_data.json va tinh tuition_vnd tam thoi tu currency."""
    with open(DATA_PATH, encoding="utf-8") as f:
        raw = json.load(f)

    ds = []
    for uni in raw:
        rate = TY_GIA_TAM_THOI.get(uni.get("currency"))
        tuition_per_year = uni.get("tuition_per_year")
        tuition_vnd = tuition_per_year * rate if (rate and tuition_per_year is not None) else None
        ds.append({
            "name": uni["name"],
            "tuition_vnd": tuition_vnd,
            "ielts_min": uni.get("ielts_min"),
            "toefl_min": uni.get("toefl_min"),
        })
    return ds


TRUONG_MAU = doc_du_lieu_that()


class ChartPrototype(tb.Frame):
    def __init__(self, master):
        super().__init__(master)
        self._lan_da_doi = 0
        # mo phong danh sach dang chon tu compare_service (2-5 truong)
        self._danh_sach_dang_chon = TRUONG_MAU[:3]

        # 1 Figure duy nhat, 2 subplot xep doc -> 1 canvas, 1 draw_idle()
        # moi lan ve, khong tao Figure/canvas moi khi doi du lieu
        self._fig = Figure(figsize=(6.5, 7.5), dpi=100)
        self._ax_hoc_phi, self._ax_ielts = self._fig.subplots(2, 1)
        self._ax_toefl = self._ax_ielts.twinx()  # goi 1 lan duy nhat, khong goi lai khi redraw
        print(f"[prototype] id(Figure) ban dau: {id(self._fig)}")
        print(f"[prototype] doc duoc {len(TRUONG_MAU)} truong tu {DATA_PATH}")

        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.get_tk_widget().pack(fill="both", expand=True)

        self._nhan_trang_thai = tb.Label(self, text="Dang hien thi 3 truong mac dinh")
        self._nhan_trang_thai.pack(pady=(8, 0))

        tb.Button(
            self, text=f"Doi danh sach truong {SO_LAN_DOI} lan",
            bootstyle="primary", command=self._bat_dau,
        ).pack(pady=8)

        self._ve()

    # ─── vẽ ───────────────────────────────────────────────
    def _ve(self):
        self._ve_hoc_phi()
        self._ve_ngoai_ngu()
        self._fig.tight_layout()
        self._canvas.draw_idle()

    def _ve_hoc_phi(self):
        ax = self._ax_hoc_phi
        ax.clear()

        co_du_lieu = [t for t in self._danh_sach_dang_chon if t.get("tuition_vnd") is not None]
        thieu = [t["name"] for t in self._danh_sach_dang_chon if t.get("tuition_vnd") is None]

        ten = [t["name"] for t in co_du_lieu]
        trieu_vnd = [t["tuition_vnd"] / 1_000_000 for t in co_du_lieu]

        # bar NGANG vi ten truong dai, bar dung phai xoay nhan kho doc
        ax.barh(ten, trieu_vnd, color="#2F5DFF")
        ax.set_xlabel("Triệu VND / năm")
        ax.set_title("Học phí/năm (quy đổi VND)")
        ax.invert_yaxis()  # truong dau tien trong danh sach nam tren cung
        ax.tick_params(axis="y", labelsize=8)

        if thieu:
            ax.text(
                0.0, -0.18, f"N/A: {', '.join(thieu)}",
                transform=ax.transAxes, fontsize=8, color="#B00020",
            )

    def _ve_ngoai_ngu(self):
        ax1, ax2 = self._ax_ielts, self._ax_toefl
        ax1.clear()
        ax2.clear()

        # truong khong co CA HAI field thi loai het khoi chart nay
        ds = [
            t for t in self._danh_sach_dang_chon
            if t.get("ielts_min") is not None or t.get("toefl_min") is not None
        ]
        thieu_ca_hai = [t["name"] for t in self._danh_sach_dang_chon if t not in ds]

        ten = [t["name"] for t in ds]
        vi_tri = list(range(len(ds)))
        rong = 0.35

        # chi ve cot o vi tri truong CO du lieu field do - tuyet doi khong
        # ve cot cao 0 cho truong thieu field
        vi_tri_ielts = [i for i, t in enumerate(ds) if t.get("ielts_min") is not None]
        gia_tri_ielts = [ds[i]["ielts_min"] for i in vi_tri_ielts]

        vi_tri_toefl = [i for i, t in enumerate(ds) if t.get("toefl_min") is not None]
        gia_tri_toefl = [ds[i]["toefl_min"] for i in vi_tri_toefl]

        ax1.bar([i - rong / 2 for i in vi_tri_ielts], gia_tri_ielts, width=rong, color="#2F5DFF", label="IELTS")
        ax2.bar([i + rong / 2 for i in vi_tri_toefl], gia_tri_toefl, width=rong, color="#00B08C", label="TOEFL")

        ax1.set_xticks(vi_tri)
        ax1.set_xticklabels(ten, rotation=15, ha="right", fontsize=8)
        ax1.set_ylim(0, 9)  # khong de matplotlib tu scale
        ax1.set_ylabel("IELTS (thang 0–9)", color="#2F5DFF")
        ax2.set_ylim(0, 120)
        ax2.set_ylabel("TOEFL iBT (thang 0–120)", color="#00B08C")
        ax1.set_title("Yêu cầu ngoại ngữ tối thiểu")

        ghi_chu = []
        if thieu_ca_hai:
            ghi_chu.append(f"Không có dữ liệu: {', '.join(thieu_ca_hai)}")
        for t in ds:
            if t.get("ielts_min") is None:
                ghi_chu.append(f"Thiếu IELTS: {t['name']}")
            if t.get("toefl_min") is None:
                ghi_chu.append(f"Thiếu TOEFL: {t['name']}")
        if ghi_chu:
            ax1.text(
                0.0, -0.55, " | ".join(ghi_chu),
                transform=ax1.transAxes, fontsize=7, color="#B00020",
            )

    # ─── mô phỏng đổi danh sách trường 10 lần để test không treo/leak ───
    def _bat_dau(self):
        self._lan_da_doi = 0
        self._doi_du_lieu()

    def _doi_du_lieu(self):
        if self._lan_da_doi >= SO_LAN_DOI:
            self._nhan_trang_thai.config(text=f"Xong {SO_LAN_DOI} lần, UI không bị treo")
            print(f"[prototype] id(Figure) sau {SO_LAN_DOI} lần: {id(self._fig)} (phải giống ban đầu)")
            return
        self._lan_da_doi += 1
        so_luong = random.randint(2, 5)  # dung khoang compare_service.MAX_COMPARE cho phep
        self._danh_sach_dang_chon = random.sample(TRUONG_MAU, so_luong)
        self._ve()
        self._nhan_trang_thai.config(
            text=f"Đã đổi lần {self._lan_da_doi}/{SO_LAN_DOI} - đang chọn {so_luong} trường"
        )
        # goi lai qua after() - main thread, KHONG dung threading (ARCHITECTURE.md 5.4)
        self.after(DO_TRE_MS, self._doi_du_lieu)


def main():
    app = tb.Window(themename="flatly", title="Prototype 2 chart CompareView", size=(700, 820))
    ChartPrototype(app).pack(fill="both", expand=True, padx=16, pady=16)
    app.mainloop()


if __name__ == "__main__":
    main()
