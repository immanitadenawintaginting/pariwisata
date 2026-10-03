"""Pra-pemrosesan tab Multivariat -> data/processed/multivariat_provinsi.csv
Jalankan dari akar proyek: python scripts/01b_multivariat.py
Sumber : sheet 'GeoNMulti' pada Data_Visdat*.xlsx (data/raw/), bersumber dari BPS.
Keluaran: Provinsi, Wilayah, dan 10 variabel numerik (Bintang & Non-Bintang).
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

VARIABEL = [
    "TPK_Bintang", "TPK_NonBintang",
    "Akomodasi_Bintang", "Akomodasi_NonBintang",
    "Kamar_Bintang", "Kamar_NonBintang",
    "TempatTidur_Bintang", "TempatTidur_NonBintang",
    "LamaInap_Bintang", "LamaInap_NonBintang",
]
# Nama kolom di Excel -> nama kolom kontrak
RENAME = {"LamaMenginap_Bintang": "LamaInap_Bintang",
          "LamaMenginap_NonBintang": "LamaInap_NonBintang"}

# Pengelompokan wilayah (untuk pewarnaan; dipakai sebagai pembanding klaster)
WILAYAH = {
    "Sumatera": ["Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Jambi",
                 "Sumatera Selatan", "Bengkulu", "Lampung",
                 "Kepulauan Bangka Belitung", "Kepulauan Riau"],
    "Jawa": ["DKI Jakarta", "Jawa Barat", "Jawa Tengah", "DI Yogyakarta",
             "Jawa Timur", "Banten"],
    "Bali & Nusa Tenggara": ["Bali", "Nusa Tenggara Barat", "Nusa Tenggara Timur"],
    "Kalimantan": ["Kalimantan Barat", "Kalimantan Tengah", "Kalimantan Selatan",
                   "Kalimantan Timur", "Kalimantan Utara"],
    "Sulawesi": ["Sulawesi Utara", "Sulawesi Tengah", "Sulawesi Selatan",
                 "Sulawesi Tenggara", "Gorontalo", "Sulawesi Barat"],
    "Maluku & Papua": ["Maluku", "Maluku Utara", "Papua Barat", "Papua Barat Daya",
                       "Papua", "Papua Selatan", "Papua Tengah", "Papua Pegunungan"],
}
PROV2WIL = {p: w for w, ps in WILAYAH.items() for p in ps}


def main():
    files = sorted(RAW.glob("Data_Visdat.xlsx"))
    if not files:
        raise SystemExit("Letakkan Data_Visdat*.xlsx di data/raw/")
    df = pd.read_excel(files[0], sheet_name="GeoNMulti").rename(columns=RENAME)
    df["Provinsi"] = df["Provinsi"].astype(str).str.strip()
    df = df[["Provinsi"] + VARIABEL].dropna(how="all", subset=VARIABEL)
    df["Wilayah"] = df["Provinsi"].map(PROV2WIL)
    tak_terpetakan = df.loc[df["Wilayah"].isna(), "Provinsi"].tolist()
    assert not tak_terpetakan, f"Provinsi belum masuk WILAYAH: {tak_terpetakan}"
    assert df[VARIABEL].notna().all().all(), "Ada nilai kosong pada variabel"
    df = df[["Provinsi", "Wilayah"] + VARIABEL]
    df.to_csv(OUT / "multivariat_provinsi.csv", index=False)
    print(f"multivariat_provinsi.csv: {df.shape[0]} provinsi x {len(VARIABEL)} variabel")


if __name__ == "__main__":
    main()