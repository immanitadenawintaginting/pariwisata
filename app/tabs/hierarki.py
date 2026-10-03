"""Tab Hierarki -- UAS Visdat 2026 (Lampiran A: data berhierarki).

Hierarki 1 (akomodasi): Indonesia > Pulau > Provinsi > Jenis akomodasi (Bintang / Non-Bintang)
    ukuran = jumlah kamar | akomodasi | tempat tidur (aditif -> induk = jumlah anak)
    warna  = TPK (%) atau rata-rata lama menginap (hari)      -> Treemap + Sunburst
Hierarki 2 (wisatawan): Indonesia > Pulau > Provinsi > Jenis kelamin
    ukuran = jumlah perjalanan wisatawan nusantara, warna = % perempuan -> Icicle
Interaksi: filter Pulau/Provinsi, slider kedalaman, klik drill-down + breadcrumb, tooltip.
Data   : Data_Visdat.xlsx, sheet "GeoNMulti" (BPS)
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from sumber import kutip
from theme import card, chapter, hero, inject_theme, insight, kpi_card, panel, polish, story_nav

PULAU = {
    "Sumatera": ["Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Jambi", "Sumatera Selatan",
                 "Bengkulu", "Lampung", "Kepulauan Bangka Belitung", "Kepulauan Riau"],
    "Jawa": ["DKI Jakarta", "Jawa Barat", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur", "Banten"],
    "Bali & Nusa Tenggara": ["Bali", "Nusa Tenggara Barat", "Nusa Tenggara Timur"],
    "Kalimantan": ["Kalimantan Barat", "Kalimantan Tengah", "Kalimantan Selatan",
                   "Kalimantan Timur", "Kalimantan Utara"],
    "Sulawesi": ["Sulawesi Utara", "Sulawesi Tengah", "Sulawesi Selatan", "Sulawesi Tenggara",
                 "Gorontalo", "Sulawesi Barat"],
    "Maluku": ["Maluku", "Maluku Utara"],
    "Papua": ["Papua Barat", "Papua Barat Daya", "Papua", "Papua Selatan", "Papua Tengah",
              "Papua Pegunungan"],
}
PULAU_DARI = {p: pulau for pulau, ps in PULAU.items() for p in ps}
ROOT = "Indonesia"

UKURAN = {  # label -> (kolom, satuan)
    "Jumlah kamar": ("Kamar", "kamar"),
    "Jumlah akomodasi": ("Akomodasi", "usaha"),
    "Jumlah tempat tidur": ("TempatTidur", "tempat tidur"),
}
WARNA = {  # label -> (kolom, format)
    "TPK (%)": ("TPK", ".1f"),
    "Rata-rata lama menginap (hari)": ("Lama", ".2f"),
}


# ----------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------
@st.cache_data
def siapkan(_load_sheet):
    geo = _load_sheet("GeoNMulti").copy()
    geo["Provinsi"] = geo["Provinsi"].astype(str).str.strip()
    geo["Pulau"] = geo["Provinsi"].map(PULAU_DARI).fillna("Lainnya")

    akom = []
    for _, r in geo.iterrows():
        for jenis, s in (("Bintang", "Bintang"), ("Non-Bintang", "NonBintang")):
            akom.append(dict(
                Pulau=r["Pulau"], Provinsi=r["Provinsi"], Jenis=jenis,
                Akomodasi=int(r[f"Akomodasi_{s}"]), Kamar=int(r[f"Kamar_{s}"]),
                TempatTidur=int(r[f"TempatTidur_{s}"]), TPK=float(r[f"TPK_{s}"]),
                Lama=float(r[f"LamaMenginap_{s}"])))
    akom = pd.DataFrame(akom)

    gender = []
    for _, r in geo.iterrows():
        tot = float(r["JumlahWisatawanTujuan"])
        for jk in ("Laki-laki", "Perempuan"):
            gender.append(dict(
                Pulau=r["Pulau"], Provinsi=r["Provinsi"], JK=jk,
                Ukuran=round(tot * float(r[jk]) / 100), Warna=float(r["Perempuan"])))
    return akom, pd.DataFrame(gender)


def bangun_node(d, levels, fmt_teks, hover_leaf, hover_parent):
    """Tabel node Plotly. Induk = jumlah anak (branchvalues='total');
    warna induk = rata-rata terbobot ukuran."""
    d = d.copy()
    d["_w"] = d["Warna"] * d["Ukuran"]
    rows = [dict(id=ROOT, label=ROOT, parent="", path=ROOT, Ukuran=d["Ukuran"].sum(),
                 Warna=d["_w"].sum() / d["Ukuran"].sum(), leaf=False, info="")]
    for k in range(1, len(levels) + 1):
        g = d.groupby(levels[:k], sort=False).agg(
            Ukuran=("Ukuran", "sum"), w=("_w", "sum"), Warna=("Warna", "mean"),
            info=("Info", "first")).reset_index()
        for _, r in g.iterrows():
            kunci = [r[c] for c in levels[:k]]
            leaf = k == len(levels)
            rows.append(dict(
                id="|".join([ROOT] + kunci), label=kunci[-1], parent="|".join([ROOT] + kunci[:-1]),
                path=" › ".join([ROOT] + kunci), Ukuran=r["Ukuran"],
                Warna=r["Warna"] if leaf else r["w"] / r["Ukuran"], leaf=leaf,
                info=r["info"] if leaf else ""))
    n = pd.DataFrame(rows)
    n["teks"] = [fmt_teks(u) for u in n["Ukuran"]]
    n["hover"] = [(hover_leaf if lf else hover_parent)(u, w) + (f"<br>{i}" if i else "")
                  for u, w, lf, i in zip(n["Ukuran"], n["Warna"], n["leaf"], n["info"])]
    return n


def gambar(jenis, n, skala, warna_label, cmin, cmax, judul, ukuran_label, maxdepth, height):
    marker = dict(
        colors=n["Warna"], colorscale=skala, cmin=cmin, cmax=cmax, line=dict(width=1, color="white"),
        colorbar=dict(title=dict(text=warna_label, side="top"), orientation="h", x=0.5, xanchor="center",
                      y=-0.02, yanchor="top", len=0.75, thickness=12, tickfont=dict(size=11)))
    kw = dict(ids=n["id"], labels=n["label"], parents=n["parent"], values=n["Ukuran"],
              branchvalues="total", marker=marker, maxdepth=maxdepth,
              customdata=np.stack([n["path"], n["teks"], n["hover"]], axis=-1),
              hovertemplate="<b>%{label}</b><br><i>%{customdata[0]}</i><br>%{customdata[2]}<extra></extra>",
              texttemplate="<b>%{label}</b><br>%{customdata[1]}", textfont=dict(size=12))
    if jenis == "Treemap":
        tr = go.Treemap(tiling=dict(pad=3), pathbar=dict(visible=True, thickness=22), **kw)
    elif jenis == "Sunburst":
        tr = go.Sunburst(insidetextorientation="radial", **kw)
    else:
        # vertikal: akar di atas, level turun ke bawah, daun berjajar mendatar (lebih lebar daripada versi horizontal)
        tr = go.Icicle(tiling=dict(orientation="v", pad=2), pathbar=dict(visible=True, thickness=22), **kw)
    fig = go.Figure(tr)
    fig.update_layout(
        height=height, margin=dict(t=58, l=4, r=4, b=62), uniformtext=dict(minsize=9, mode="hide"),
        font=dict(family="system-ui, sans-serif"),
        title=dict(
            text=f"<b>{jenis}: {judul}</b><br><span style='font-size:11px;color:#666'>"
                 f"Ukuran = {ukuran_label} · Warna = {warna_label} · Sumber: BPS</span>",
            x=0.01, xanchor="left", font=dict(size=14)))
    return polish(fig)


# ----------------------------------------------------------------------
# UI
# ----------------------------------------------------------------------
IKON = {"#0072B2": "🏨", "#009E73": "⭐", "#E69F00": "🏠", "#CC79A7": "🧳", "#D55E00": "🔝"}


def _kpi(col, lab, val, sub, color="#0072B2"):
    kpi_card(col, IKON.get(color, "•"), lab, val, sub, color)


def _breadcrumb(pulau, prov):
    b = [ROOT] + ([pulau] if pulau != "Semua pulau" else []) + ([prov] if prov != "Semua provinsi" else [])
    return " › ".join(f"**{x}**" if i == len(b) - 1 else x for i, x in enumerate(b))


def _bagian_akomodasi(akom, d_sel, depth):
    chapter(1, "hr-1", "Treemap dan sunburst", "Bagaimana struktur akomodasi di setiap provinsi?",
            "Luas kotak merepresentasikan ukuran akomodasi yang dipilih, sedangkan warna merepresentasikan "
            "tingkat penghunian kamar atau lama menginap. Treemap dan sunburst menampilkan struktur yang sama "
            "dengan representasi berbeda.")
    with panel("hr_ukuran"):
        c1, c2 = st.columns(2)
        u_label = c1.selectbox("Ukuran (luas) = ", list(UKURAN), key="ukuran")
        w_label = c2.radio("Warna = ", list(WARNA), horizontal=True, key="warna")
    u_col, satuan = UKURAN[u_label]
    w_col, w_fmt = WARNA[w_label]

    def siap(df):
        df = df.copy()
        df["Ukuran"], df["Warna"] = df[u_col], df[w_col]
        df["Info"] = ("Akomodasi: " + df["Akomodasi"].map("{:,}".format) + " · Kamar: "
                      + df["Kamar"].map("{:,}".format) + " · Tempat tidur: " + df["TempatTidur"].map("{:,}".format)
                      + "<br>TPK: " + df["TPK"].map("{:.1f}".format) + "% · Lama menginap: "
                      + df["Lama"].map("{:.2f}".format) + " hari")
        return df

    d = siap(d_sel)
    cmin, cmax = akom[w_col].min(), akom[w_col].max()
    n = bangun_node(
        d, ["Pulau", "Provinsi", "Jenis"], fmt_teks=lambda u: f"{u:,.0f}",
        hover_leaf=lambda u, w: f"{u_label}: <b>{u:,.0f}</b> {satuan}<br>{w_label}: <b>{w:{w_fmt}}</b>",
        hover_parent=lambda u, w: f"Total {u_label.lower()}: <b>{u:,.0f}</b> {satuan}<br>{w_label} (terbobot): {w:{w_fmt}}")
    judul = f"{u_label.lower()} menurut jenis akomodasi"
    col1, col2 = st.columns(2)
    with col1, card("treemap"):
        st.plotly_chart(gambar("Treemap", n, "Viridis", w_label, cmin, cmax, judul, u_label, depth, 400),
                        width="stretch")
    with col2, card("sunburst"):
        st.plotly_chart(gambar("Sunburst", n, "Viridis", w_label, cmin, cmax, judul, u_label, depth, 400),
                        width="stretch")

    # ---- temuan (seluruh Indonesia)
    b, nb = akom[akom["Jenis"] == "Bintang"], akom[akom["Jenis"] == "Non-Bintang"]
    tpk_b = (b["TPK"] * b["Kamar"]).sum() / b["Kamar"].sum()
    tpk_n = (nb["TPK"] * nb["Kamar"]).sum() / nb["Kamar"].sum()
    sh_a = b["Akomodasi"].sum() / akom["Akomodasi"].sum() * 100
    sh_k = b["Kamar"].sum() / akom["Kamar"].sum() * 100
    lebih = (b.set_index("Provinsi")["TPK"] > nb.set_index("Provinsi")["TPK"]).sum()
    top = b.loc[b["TPK"].idxmax()]
    pul = akom.groupby("Pulau")["Kamar"].sum()
    m1, m2, m3 = st.columns(3)
    _kpi(m1, "Total kamar (nasional)", f"{akom['Kamar'].sum():,.0f}".replace(",", "."),
         f"{pul.idxmax()} terbanyak ({pul.max() / pul.sum() * 100:.0f}%)", "#0072B2")
    _kpi(m2, "TPK bintang (terbobot)", f"{tpk_b:.1f}%".replace(".", ","), "seluruh Indonesia", "#009E73")
    _kpi(m3, "TPK non-bintang (terbobot)", f"{tpk_n:.1f}%".replace(".", ","), "seluruh Indonesia", "#E69F00")
    insight(f"Hotel berbintang hanya mencakup {sh_a:.1f}% dari jumlah usaha akomodasi, tetapi menyumbang "
            f"{sh_k:.1f}% dari jumlah kamar. TPK hotel berbintang lebih tinggi daripada non-bintang pada {lebih} dari "
            f"{b['Provinsi'].nunique()} provinsi; TPK hotel berbintang tertinggi tercatat di {top['Provinsi']} "
            f"({top['TPK']:.1f}%).")


def _bagian_gender(gender, d_sel, depth):
    chapter(2, "hr-2", "Icicle", "Bagaimana komposisi wisatawan menurut jenis kelamin?",
            "Perjalanan wisatawan nusantara dipecah menurut jenis kelamin pada setiap provinsi tujuan. "
            "Warna menunjukkan persentase wisatawan menurut jenis kelamin yang dipilih.", "#CC79A7")
    with panel("hr_jk"):
        jk = st.segmented_control("Jenis kelamin", ["Semua", "Laki-laki", "Perempuan"], default="Semua",
                                  key="hr_jk_pilih") or "Semua"
    lk = jk == "Laki-laki"
    kata = "laki-laki" if lk else "perempuan"
    w_label = f"Persentase {kata} (%)"

    def pakai(df):
        df = df.copy()
        if jk != "Semua":
            df = df[df["JK"] == jk]
        if lk:
            df["Warna"] = 100 - df["Warna"]
        return df

    d, g = pakai(d_sel), pakai(gender)
    cmin, cmax = g["Warna"].min(), g["Warna"].max()
    d["Info"] = ""
    n = bangun_node(
        d, ["Pulau", "Provinsi", "JK"], fmt_teks=lambda u: f"{u / 1e6:,.2f} jt",
        hover_leaf=lambda u, w: f"Perjalanan: <b>{u:,.0f}</b><br>% {kata} di provinsi: {w:.1f}%",
        hover_parent=lambda u, w: f"Perjalanan: <b>{u:,.0f}</b><br>% {kata} (terbobot): {w:.1f}%")
    h = 560  # icicle vertikal: butuh tinggi agar level 3-4 terbaca
    ket = "" if jk == "Semua" else f" ({kata})"
    with card("icicle"):
        st.plotly_chart(gambar("Icicle", n, "Cividis", w_label, cmin, cmax,
                               "perjalanan wisatawan nusantara menurut jenis kelamin" + ket,
                               "jumlah perjalanan", depth, h), width="stretch")

    p = gender.drop_duplicates("Provinsi").set_index("Provinsi")["Warna"]
    sex = "Laki-laki" if lk else "Perempuan"
    if lk:
        p = 100 - p
    nas = gender[gender["JK"] == sex]["Ukuran"].sum() / gender["Ukuran"].sum() * 100
    pul = gender.groupby("Pulau").apply(
        lambda x: x[x["JK"] == sex]["Ukuran"].sum() / x["Ukuran"].sum() * 100)
    m1, m2, m3 = st.columns(3)
    _kpi(m1, f"% {kata} nasional", f"{nas:.1f}%".replace(".", ","), "seluruh perjalanan", "#CC79A7")
    _kpi(m2, f"% {kata} tertinggi", f"{p.max():.1f}%".replace(".", ","), p.idxmax(), "#009E73")
    _kpi(m3, f"% {kata} terendah", f"{p.min():.1f}%".replace(".", ","), p.idxmin(), "#D55E00")
    insight(f"Persentase wisatawan {kata} secara nasional sebesar {nas:.1f}% dari seluruh perjalanan. "
            f"Persentase tertinggi tercatat di {p.idxmax()} ({p.max():.1f}%) dan terendah di {p.idxmin()} "
            f"({p.min():.1f}%); menurut pulau, nilai tertinggi berada di {pul.idxmax()} ({pul.max():.1f}%).")


def render(load_sheet):
    inject_theme()
    akom, gender = siapkan(load_sheet)

    hero("", "Struktur berjenjang <em>akomodasi</em> dan wisatawan",
         "Data disajikan secara hierarkis: Indonesia, pulau, provinsi, kemudian jenis akomodasi atau jenis "
         "kelamin wisatawan nusantara.",
         [(akom["Provinsi"].nunique(), "provinsi"), (akom["Akomodasi"].sum(), "usaha akomodasi"),
          (akom["Kamar"].sum(), "kamar"), (gender["Ukuran"].sum(), "perjalanan wisatawan")])
    story_nav([("hr-1", "1 · Struktur akomodasi"), ("hr-2", "2 · Komposisi wisatawan")])

    with panel("hr_filter", "Filter hierarki"):
        c1, c2, c3 = st.columns([1, 1, 1])
        pulau = c1.selectbox("Pulau", ["Semua pulau"] + sorted(akom["Pulau"].unique()), key="pulau")
        prov_opsi = akom if pulau == "Semua pulau" else akom[akom["Pulau"] == pulau]
        prov = c2.selectbox("Provinsi", ["Semua provinsi"] + sorted(prov_opsi["Provinsi"].unique()),
                            key=f"prov_{pulau}")
        depth = c3.slider("Kedalaman level ditampilkan", 2, 4, 3,
                          help="Level 4 (Jenis akomodasi / Jenis kelamin) tampil setelah drill-down atau saat slider = 4.")
        st.markdown("Posisi: " + _breadcrumb(pulau, prov))

    def saring(df):
        if pulau != "Semua pulau":
            df = df[df["Pulau"] == pulau]
        if prov != "Semua provinsi":
            df = df[df["Provinsi"] == prov]
        return df

    _bagian_akomodasi(akom, saring(akom), depth)
    _bagian_gender(gender, saring(gender), depth)

    st.write("")
    with st.expander("Sumber data"):
        for k in ("tpk", "multi", "wisnus_tujuan"):
            st.markdown("- " + kutip(k, True))