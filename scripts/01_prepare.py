"""Pra-pemrosesan data BPS -> data/processed/. Jalankan: python scripts/01_prepare.py"""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

# 1) Flow: sudah bersih, cukup disalin
for f in ["chord.csv", "sankey_15_sumber_12_provinsi.csv",
          "heatmap_long_top15_ranking.csv"]:
    if (RAW / f).exists():
        shutil.copy(RAW / f, OUT / f)

# 2) TODO (Orang A): bangun hierarki_long.csv dari tabel BPS
# 3) TODO (Orang B): bangun multivariat_provinsi.csv (34 provinsi x 10 variabel)

print("Selesai.")