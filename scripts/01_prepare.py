from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

for f in ["chord.csv", "sankey_15_sumber_12_provinsi.csv",
          "heatmap_long_top15_ranking.csv"]:
    if (RAW / f).exists():
        shutil.copy(RAW / f, OUT / f)


print("Selesai.")