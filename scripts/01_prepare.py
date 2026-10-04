import shutil
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
from prapemrosesan import bersihkan_flow, susun_hierarki

RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

xlsx = RAW / "Data_Visdat.xlsx"
if not xlsx.exists():
    raise SystemExit("Taruh Data_Visdat.xlsx di data/raw/ dulu")

flow, n_kosong = bersihkan_flow(pd.read_excel(xlsx, sheet_name="Flow"))
flow.to_csv(OUT / "flow_bersih.csv", index=False)

geo = pd.read_excel(xlsx, sheet_name="GeoNMulti")
akom, gender = susun_hierarki(geo)
akom.to_csv(OUT / "akomodasi_long.csv", index=False)
gender.to_csv(OUT / "wisatawan_jk_long.csv", index=False)

# matriks perjalanan antarprovinsi sudah rapi dari sumbernya, cukup disalin
shutil.copy(RAW / "chord.csv", OUT / "chord.csv")

print(f"flow_bersih.csv: {len(flow)} baris ({n_kosong} pasangan bernilai 0)")
print(f"akomodasi_long.csv: {len(akom)} baris, wisatawan_jk_long.csv: {len(gender)} baris")
print("chord.csv disalin")