import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

ICON = ROOT / "assets" / "logo-kelapa-icon.png"
LOGO = ROOT / "assets" / "logo-kelapa.png"

st.set_page_config(page_title="Pariwisata Indonesia · Dasbor Visualisasi BPS",
                   page_icon=str(ICON) if ICON.exists() else "🥥", layout="wide")

from theme import brand_bar, data_uri, inject_theme
from tabs import beranda, flow, hierarki, multivariat


@st.cache_data
def load(name: str) -> pd.DataFrame:
    for folder in ("processed", "raw"):
        p = ROOT / "data" / folder / name
        if p.exists():
            return pd.read_csv(p)
    st.error(f"File data tidak ditemukan: {name}")
    st.stop()


@st.cache_data
def load_sheet(sheet: str) -> pd.DataFrame:
    for folder in ("raw", "processed"):
        p = ROOT / "data" / folder / "Data_Visdat.xlsx"
        if p.exists():
            return pd.read_excel(p, sheet_name=sheet)
    st.error("File data tidak ditemukan: Data_Visdat.xlsx (taruh di data/raw/)")
    st.stop()


inject_theme()
brand_bar("Pariwisata Indonesia", "Sumber: BPS", logo=data_uri(LOGO))

tab_b, tab_f, tab_m, tab_h = st.tabs(["Beranda", "Aliran", "Multivariat", "Hierarki"])

with tab_b:
    beranda.render(load, load_sheet)
with tab_f:
    flow.render(load, load_sheet)
with tab_m:
    multivariat.render(load_sheet)
with tab_h:
    hierarki.render(load_sheet)