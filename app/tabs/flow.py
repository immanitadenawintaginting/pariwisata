import json
from html import escape as esc
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from prapemrosesan import bersihkan_flow
from sumber import CATATAN_WISMAN, kutip
from theme import (card, chapter, chips, hero, inject_theme, insight, kpi_card,
                   panel, polish, story_nav)


HTML_PATH = Path(__file__).parent / "chord.html"

SEMUA = "(Semua provinsi)"
LEVEL_PINTU, LEVEL_PROV = "Pintu masuk", "Provinsi"

BLUE, ORANGE, VERM, GREY = "#0072B2", "#E69F00", "#D55E00", "#A0A0A0"
GREEN, PINK = "#009E73", "#CC79A7"

REGION_OF = {
    **{p: "Sumatera" for p in [
        "Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Kepulauan Riau",
        "Jambi", "Sumatera Selatan", "Kepulauan Bangka Belitung", "Bengkulu", "Lampung"]},
    **{p: "Jawa" for p in [
        "DKI Jakarta", "Banten", "Jawa Barat", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur"]},
    **{p: "Bali & Nusa Tenggara" for p in [
        "Bali", "Nusa Tenggara Barat", "Nusa Tenggara Timur"]},
    **{p: "Kalimantan" for p in [
        "Kalimantan Barat", "Kalimantan Tengah", "Kalimantan Selatan",
        "Kalimantan Timur", "Kalimantan Utara"]},
    **{p: "Sulawesi" for p in [
        "Sulawesi Utara", "Gorontalo", "Sulawesi Tengah", "Sulawesi Barat",
        "Sulawesi Selatan", "Sulawesi Tenggara"]},
    **{p: "Maluku & Papua" for p in [
        "Maluku", "Maluku Utara", "Papua", "Papua Barat", "Papua Barat Daya",
        "Papua Pegunungan", "Papua Selatan", "Papua Tengah"]},
}
REGION_ORDER = ["Sumatera", "Jawa", "Bali & Nusa Tenggara",
                "Kalimantan", "Sulawesi", "Maluku & Papua"]
REGION_COLOR = {
    "Sumatera": "#E69F00", "Jawa": "#0072B2", "Bali & Nusa Tenggara": "#009E73",
    "Kalimantan": "#D55E00", "Sulawesi": "#CC79A7", "Maluku & Papua": "#56B4E9",
}


def fmt_id(n) -> str:
    return f"{n:,.0f}".replace(",", ".")


def compact(v) -> str:
    if v >= 1e9:
        return f"{v / 1e9:.1f} miliar".replace(".", ",")
    if v >= 1e6:
        return f"{v / 1e6:.1f} jt".replace(".", ",")
    if v >= 1e3:
        return f"{v / 1e3:.0f} rb"
    return f"{v:.0f}"


def judul(teks, sub):
    return dict(text=f"<b>{teks}</b><br><sup>{sub} · Sumber: BPS</sup>", x=0.01, xanchor="left")


PLOT_CFG = {"displaylogo": False, "modeBarButtonsToRemove": ["select2d", "lasso2d"]}

ICON = {BLUE: "🌏", GREEN: "📍", ORANGE: "🧭", PINK: "🧳", VERM: "🔥"}


def kpi(col, label, value, sub="", color=BLUE):
    kpi_card(col, ICON.get(color, "•"), label, value, sub, color)


def show(fig):
    st.plotly_chart(polish(fig), width="stretch", config=PLOT_CFG)


@st.cache_data
def prep_manca(raw: pd.DataFrame):
    return bersihkan_flow(raw)


def sankey(df: pd.DataFrame, focus_t=()) -> go.Figure:
    focus_t = set(focus_t)
    srcs = df.groupby("Source")["Value"].sum().sort_values(ascending=False).index.tolist()
    tgts = df.groupby("Target")["Value"].sum().sort_values(ascending=False).index.tolist()
    nodes = srcs + tgts
    idx = {n: i for i, n in enumerate(nodes)}

    node_colors = [BLUE] * len(srcs) + [VERM if t in focus_t else ORANGE for t in tgts]
    if focus_t & set(tgts):
        link_colors = [
            "rgba(213,94,0,0.70)" if t in focus_t else "rgba(160,160,160,0.13)"
            for t in df["Target"]]
    else:
        link_colors = ["rgba(0,114,178,0.33)"] * len(df)

    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            label=nodes, color=node_colors, pad=8, thickness=14,
            line=dict(color="white", width=0.5),
            hovertemplate="%{label}<br>Total: %{value:,.0f} kunjungan<extra></extra>"),
        link=dict(
            source=df["Source"].map(idx), target=df["Target"].map(idx),
            value=df["Value"], color=link_colors,
            hovertemplate="%{source.label} → %{target.label}<br>"
                          "%{value:,.0f} kunjungan<extra></extra>"),
    ))
    fig.update_layout(height=min(560, max(420, 12 * len(srcs) + 120)), margin=dict(l=8, r=8, t=56, b=6),
                      font=dict(size=12), separators=",.",
                      title=judul("Aliran wisman: negara asal → tujuan kedatangan",
                                  "Jumlah kunjungan wisatawan mancanegara, 2024"))
    return fig


def heatmap(df: pd.DataFrame, focus_cols=(), log=True) -> go.Figure:
    val = df.pivot_table(index="Y", columns="X", values="Value", aggfunc="sum")
    rnk = df.pivot_table(index="Y", columns="X", values="Rank", aggfunc="min")
    rows = val.sum(axis=1).sort_values(ascending=False).index
    cols = val.sum(axis=0).sort_values(ascending=False).index
    val, rnk = val.loc[rows, cols], rnk.loc[rows, cols]

    z = np.log10(val.clip(lower=1)) if log else val
    short = [str(c).rsplit(",", 1)[0].strip() for c in cols]
    if len(set(short)) < len(short):
        short = [str(c) for c in cols]
    text = [[compact(v) if pd.notna(v) else "" for v in r] for r in val.values]
    custom = np.dstack([val.values, rnk.values])
    n_rank = int(np.nanmax(rnk.values))

    cbar = dict(title="Kunjungan" + (" (skala log)" if log else ""), thickness=14)
    if log:
        lo, hi = int(np.ceil(z.min().min())), int(np.floor(z.max().max()))
        ticks = list(range(lo, hi + 1))
        cbar.update(tickvals=ticks, ticktext=[compact(10 ** p) for p in ticks])

    fig = go.Figure(go.Heatmap(
        z=z.values, x=list(cols), y=list(rows), colorscale="Viridis",
        customdata=custom, text=text, texttemplate="%{text}",
        textfont=dict(size=10), xgap=1, ygap=1, colorbar=cbar,
        hovertemplate="<b>%{y} → %{x}</b><br>%{customdata[0]:,.0f} kunjungan"
                      f"<br>Peringkat #%{{customdata[1]:.0f}} dari {n_rank}<extra></extra>"))
    for c in focus_cols:
        if c in list(cols):
            i = list(cols).index(c)
            fig.add_shape(type="rect", xref="x", yref="paper",
                          x0=i - 0.5, x1=i + 0.5, y0=0, y1=1,
                          line=dict(color=VERM, width=3))
    fig.update_layout(
        height=min(1000, max(640, 30 * len(rows) + 230)), margin=dict(l=8, r=8, t=56, b=6), separators=",.",
        title=judul("Matriks OD: negara asal × tujuan kedatangan",
                    "Kunjungan wisman 2024 · terurut menurut total"),
        xaxis=dict(title=None, tickangle=-90, tickfont=dict(size=11), automargin=True, tickvals=list(cols),
                   ticktext=short, ticklabelstandoff=2),
        yaxis=dict(title=None, autorange="reversed", tickfont=dict(size=11), automargin=True))
    return fig


def pick_nodes(df, top_n, include_self, focus):
    d = df if include_self else df[df["Asal"] != df["Tujuan"]]
    if focus:
        f = d[(d["Asal"] == focus) | (d["Tujuan"] == focus)].copy()
        f["P"] = np.where(f["Asal"] == focus, f["Tujuan"], f["Asal"])
        partners = (f.groupby("P")["Value"].sum().drop(focus, errors="ignore")
                     .nlargest(top_n - 1).index.tolist())
        return [focus] + partners
    tot = d.groupby("Asal")["Value"].sum().add(d.groupby("Tujuan")["Value"].sum(), fill_value=0)
    return tot.nlargest(top_n).index.tolist()


def build_matrix(df, names, include_self=False, min_val=0, focus=None):
    idx = {n: i for i, n in enumerate(names)}
    m = np.zeros((len(names), len(names)))
    d = df[df["Asal"].isin(names) & df["Tujuan"].isin(names)]
    for a, t, v in d[["Asal", "Tujuan", "Value"]].itertuples(index=False):
        if a == t and not include_self:
            continue
        if v < min_val:
            continue
        if focus and a != focus and t != focus:
            continue
        m[idx[a], idx[t]] = v
    return m


def chord_html(df, focus, top_n, min_val, include_self, use_sqrt):
    names = pick_nodes(df, top_n, include_self, focus)
    m = build_matrix(df, names, include_self, min_val, focus)
    keep = [i for i, n in enumerate(names)
            if m[i].sum() + m[:, i].sum() > 0 or n == focus]
    names = [names[i] for i in keep]
    m = m[np.ix_(keep, keep)]
    if len(names) < 2 or m.sum() == 0:
        return None

    tot = m.sum(0) + m.sum(1)
    order = sorted(range(len(names)), key=lambda i: (
        REGION_ORDER.index(REGION_OF.get(names[i], "Maluku & Papua")), -tot[i]))
    names = [names[i] for i in order]
    m = m[np.ix_(order, order)]
    regs = [REGION_OF.get(n, "Maluku & Papua") for n in names]

    payload = {
        "names": names,
        "colors": [REGION_COLOR[r] for r in regs],
        "raw": m.tolist(),
        "geo": (np.sqrt(m) if use_sqrt else m).tolist(),
        "legend": [{"region": r, "color": REGION_COLOR[r]} for r in REGION_ORDER if r in regs],
    }
    return HTML_PATH.read_text(encoding="utf-8").replace("__DATA__", json.dumps(payload))


def top_pairs_bar(df, focus, n=10) -> go.Figure:
    d = df[df["Asal"] != df["Tujuan"]]
    if focus:
        d = d[(d["Asal"] == focus) | (d["Tujuan"] == focus)]
    d = d.nlargest(n, "Value").iloc[::-1]
    fig = go.Figure(go.Bar(
        x=d["Value"], y=d["Asal"] + " → " + d["Tujuan"], orientation="h",
        marker_color=[REGION_COLOR[REGION_OF.get(a, "Maluku & Papua")] for a in d["Asal"]],
        text=[compact(v) for v in d["Value"]], textposition="outside", cliponaxis=False,
        hovertemplate="%{y}<br>%{x:,.0f} perjalanan<extra></extra>"))
    fig.update_layout(
        height=660, margin=dict(l=8, r=30, t=56, b=6), separators=",.",
        title=judul("10 aliran antarprovinsi terbesar" + (f" (ke/dari {focus})" if focus else ""),
                    "Jumlah perjalanan, warna = wilayah provinsi asal"),
        xaxis=dict(title="Jumlah perjalanan", range=[0, d["Value"].max() * 1.22]),
        yaxis=dict(automargin=True))
    return fig


def kpi_row(a, c, focus, total_all):
    by_prov = a.groupby("Provinsi")["Value"].sum().sort_values(ascending=False)
    by_cty = a.groupby("Asal")["Value"].sum().sort_values(ascending=False)
    nonself = c[c["Asal"] != c["Tujuan"]]
    k1, k2, k3, k4 = st.columns(4)

    if focus and focus in by_prov.index:
        sub = a[a["Provinsi"] == focus].groupby("Asal")["Value"].sum().sort_values(ascending=False)
        kpi(k1, f"Wisman ke {focus}", fmt_id(by_prov[focus]), "kunjungan (sesuai filter)", BLUE)
        kpi(k2, "Porsi dari seluruh tujuan",
            f"{by_prov[focus] / by_prov.sum():.1%}".replace(".", ","), "pada filter saat ini", GREEN)
        kpi(k3, "Negara asal terbesar", sub.index[0], f"{fmt_id(sub.iloc[0])} kunjungan", ORANGE)
    elif len(by_prov):
        tersaring = a["Value"].sum()
        kpi(k1, "Total kunjungan wisman", fmt_id(total_all),
            "seluruh data" if tersaring >= total_all else
            f"sesuai filter: {fmt_id(tersaring)} ({tersaring / total_all:.0%})", BLUE)
        kpi(k2, "Tujuan terbesar", by_prov.index[0],
            f"{by_prov.iloc[0] / by_prov.sum():.0%} dari total", GREEN)
        kpi(k3, "Negara asal terbesar", by_cty.index[0],
            f"{by_cty.iloc[0] / by_cty.sum():.0%} dari total", ORANGE)
    else:
        kpi(k1, "Total kunjungan wisman", "-", "tidak ada data pada filter ini", BLUE)

    if focus:
        v = nonself[(nonself["Asal"] == focus) | (nonself["Tujuan"] == focus)]["Value"].sum()
        kpi(k4, f"Perjalanan nusantara ke/dari {focus}", compact(v), "perjalanan antarprovinsi", PINK)
    else:
        kpi(k4, "Perjalanan nusantara", compact(nonself["Value"].sum()),
            "perjalanan antarprovinsi", PINK)


def render(load, load_sheet):
    m, n_kosong = prep_manca(load_sheet("Flow"))
    c = load("chord.csv")
    inject_theme()

    manca_prov = set(m["Provinsi"])
    prov_all = sorted(c["Asal"].unique())
    pintu_all = m.groupby("Tujuan")["Value"].sum().sort_values(ascending=False).index.tolist()

    neg = m[m["Kategori"] == "Negara"]
    by_cty = neg.groupby("Asal")["Value"].sum().sort_values(ascending=False)
    by_pintu = m.groupby("Tujuan")["Value"].sum().sort_values(ascending=False)
    total_m = m["Value"].sum()
    nonself = c[c["Asal"] != c["Tujuan"]]
    self_share = c.loc[c["Asal"] == c["Tujuan"], "Value"].sum() / c["Value"].sum()

    hero("",
         "Pola <em>aliran</em> wisatawan di Indonesia",
         f"Data BPS mencatat {compact(total_m)} kunjungan wisatawan mancanegara dari {by_cty.size} negara melalui "
         f"{len(by_pintu)} pintu kedatangan, serta {compact(nonself['Value'].sum())} perjalanan wisatawan nusantara "
         f"antarprovinsi pada {len(prov_all)} provinsi.",
         [(total_m, "kunjungan wisman"), (by_cty.size, "negara asal"),
          (len(by_pintu), "pintu kedatangan"), (nonself["Value"].sum(), "perjalanan antarprovinsi")])
    story_nav([("bab-1", "1 · Asal wisatawan mancanegara"), ("bab-2", "2 · Pasangan asal-tujuan"),
               ("bab-3", "3 · Perjalanan antarprovinsi")])

    def _atur_chord():
        # begitu provinsi dipilih, chord menampilkan semua provinsi yang terhubung dengannya
        st.session_state["fl_cn"] = 38 if st.session_state.get("fl_fokus", SEMUA) != SEMUA else 20

    box = panel("filter", "Filter bersama: Sankey, Matriks OD, dan KPI")
    with box:
        f1, f2, f3 = st.columns([3, 3, 3])
        pilihan = f1.selectbox(
            "Provinsi fokus", [SEMUA] + prov_all, key="fl_fokus", on_change=_atur_chord,
            format_func=lambda p: p if p == SEMUA or p in manca_prov
            else f"{p} (tanpa data mancanegara)",
            help="Menyorot provinsi yang sama di Sankey, Matriks OD, dan Chord. Pintu di provinsi ini "
                 "selalu ikut ditampilkan, walaupun peringkatnya di luar jumlah teratas.")
        level = f2.segmented_control(
            "Tujuan ditampilkan sebagai", [LEVEL_PINTU, LEVEL_PROV], default=LEVEL_PINTU,
            key="fl_level", help="Pintu masuk = bandara/pelabuhan/perbatasan. "
                                 "Provinsi = pintu digabung per provinsi.") or LEVEL_PINTU
        lain = f3.segmented_control(
            "Kelompok \"…Lainnya\"", ["Sembunyikan", "Tampilkan"], default="Sembunyikan",
            key="fl_lain", help="Mis. Asean Lainnya, Eropa Timur Lainnya: kelompok, bukan satu negara."
        ) or "Sembunyikan"
        pool = m[m["Kategori"] == "Negara"] if lain == "Sembunyikan" else m
        n_pool = int(pool["Asal"].nunique())
        n_tuj = int(pool["Tujuan"].nunique() if level == LEVEL_PINTU else pool["Provinsi"].nunique())
        s1, s2 = st.columns(2)
        top_n = s1.slider("Jumlah negara asal teratas", 5, n_pool, min(15, n_pool), key="fl_topn",
                          help="Negara diurutkan menurut total kunjungan ke tujuan yang ditampilkan. "
                               "Jika provinsi fokus dipilih, negara diurutkan menurut kunjungan ke provinsi fokus.")
        top_t = s2.slider(
            "Jumlah pintu kedatangan teratas" if level == LEVEL_PINTU
            else "Jumlah provinsi tujuan teratas",
            3, n_tuj, min(10, n_tuj), key=f"fl_topt_{level}",
            help="Diurutkan menurut total kunjungan. Diabaikan jika pintu tertentu dipilih "
                 "di Filter lanjutan.")
        with st.expander("Filter lanjutan: pilih negara atau pintu tertentu"):
            h1, h2 = st.columns(2)
            negara_pilih = h1.multiselect(
                "Negara asal tertentu (kosong = pakai negara teratas)",
                sorted(pool["Asal"].unique()), key="fl_negara")
            pintu_pilih = h2.multiselect(
                "Pintu masuk (kosong = semua)", pintu_all, key="fl_pintu")

    focus = None if pilihan == SEMUA else pilihan
    if focus and focus not in manca_prov:
        st.info(f"{focus} bukan lokasi pintu kedatangan mancanegara pada data; "
                "sorotan hanya berlaku pada chord.")
    # provinsi fokus punya pintu kedatangan -> dipastikan tampil di Sankey dan Matriks OD
    fokus_ada = bool(focus) and focus in manca_prov

    d = pool if not negara_pilih else pool[pool["Asal"].isin(negara_pilih)]
    d = d.assign(T=d["Tujuan"] if level == LEVEL_PINTU else d["Provinsi"])
    if pintu_pilih:
        d = d[d["Tujuan"].isin(pintu_pilih)]
    else:
        top_tuj = d.groupby("T")["Value"].sum().nlargest(top_t).index.tolist()
        if fokus_ada:
            # pintu milik provinsi fokus ditambahkan di luar jumlah teratas
            tf = d[d["Provinsi"] == focus].groupby("T")["Value"].sum()
            top_tuj = list(dict.fromkeys(top_tuj + tf[tf > 0].index.tolist()))
        d = d[d["T"].isin(top_tuj)]
    if not negara_pilih:
        tot_neg = d.groupby("Asal")["Value"].sum()
        if fokus_ada:
            # negara diurutkan menurut kunjungan ke provinsi fokus dulu, baru total keseluruhan
            ke_fokus = d[d["Provinsi"] == focus].groupby("Asal")["Value"].sum()
            urut = pd.DataFrame({"f": ke_fokus, "t": tot_neg}).fillna(0).sort_values(
                ["f", "t"], ascending=False)
            top_neg = urut.head(top_n).index
        else:
            top_neg = tot_neg.nlargest(top_n).index
        d = d[d["Asal"].isin(top_neg)]
    agg = d.groupby(["Asal", "T"], as_index=False).agg(
        Value=("Value", "sum"), Provinsi=("Provinsi", "first"))
    focus_t = set(agg.loc[agg["Provinsi"] == focus, "T"]) if focus else set()
    if fokus_ada:
        st.caption(f"Fokus {focus}: pintu di {focus} selalu ditampilkan, negara asal diurutkan menurut kunjungan "
                   f"ke {focus}, dan ambang minimum aliran tidak berlaku untuk aliran ke {focus}.")

    st.write("")
    kpi_row(agg, c, focus, total_m)

    chapter(1, "bab-1", "Sankey", "Dari mana wisatawan mancanegara datang?",
            f"Kunjungan terkonsentrasi pada sejumlah kecil negara asal dan pintu kedatangan. "
            f"<b>{esc(by_cty.index[0])}</b> merupakan negara asal terbesar ({by_cty.iloc[0] / by_cty.sum():.0%} "
            f"dari total kunjungan seluruh negara), sedangkan <b>{esc(by_pintu.index[0])}</b> merupakan pintu "
            "kedatangan dengan kunjungan tertinggi. Ketebalan pita merepresentasikan jumlah kunjungan.", BLUE)
    with card("sankey"):
        cl, cr = st.columns([2, 3], vertical_alignment="center")
        max_v = int(m["Value"].max() // 10_000 + 1) * 10_000
        min_val = cl.slider("Ambang minimum aliran (kunjungan)", 0, max_v, 2000, 1000, key="fl_min",
                            help="Menyembunyikan pita kecil agar aliran besar terbaca.")
        with cr:
            chips([(BLUE, "Negara asal"), (ORANGE, "Tujuan kedatangan")]
                  + ([(VERM, f"Fokus: {focus}")] if focus_t else [])
                  + [(None, "Tebal pita = jumlah kunjungan")])
        # nilai 0 tetap muncul di matriks OD, tapi tidak digambar sebagai pita
        # aliran ke provinsi fokus tidak ikut disembunyikan oleh ambang minimum
        milik_fokus = agg["Provinsi"].eq(focus) if focus else pd.Series(False, index=agg.index)
        s_f = agg[((agg["Value"] >= min_val) | milik_fokus) & (agg["Value"] > 0)].rename(
            columns={"Asal": "Source", "T": "Target"})
        if s_f.empty:
            st.warning("Tidak ada aliran yang memenuhi filter. Pilih negara/pintu lain atau turunkan ambang.")
        else:
            show(sankey(s_f, focus_t))
    st.caption(CATATAN_WISMAN)
    top_neg3 = by_cty.iloc[:3]
    top_lok3 = m.groupby("Provinsi")["Value"].sum().nlargest(3)
    insight(f"Negara asal terbesar adalah <b>{esc(by_cty.index[0])}</b> ({by_cty.iloc[0] / by_cty.sum():.0%}), dan tiga "
            f"negara asal teratas ({esc(', '.join(top_neg3.index))}) menyumbang <b>{top_neg3.sum() / by_cty.sum():.0%}</b> "
            f"kunjungan. Tiga lokasi kedatangan teratas ({esc(', '.join(top_lok3.index))}) menyerap "
            f"<b>{top_lok3.sum() / total_m:.0%}</b>. Kunjungan wisman bertumpu pada sedikit pasar dan pintu, sehingga "
            "perubahan pada satu pasar utama akan terasa langsung pada tujuan yang menjadi pintunya.")
    chapter(2, "bab-2", "Matriks OD", "Pasangan asal-tujuan mana yang paling dominan?",
            "Sankey menampilkan aliran terbesar, sedangkan matriks asal-tujuan (OD) memperlihatkan seluruh "
            "pasangan, termasuk pasangan dengan kunjungan sangat rendah. Sel yang lebih terang menunjukkan "
            "jumlah kunjungan yang lebih tinggi.", GREEN)
    st.markdown("<style>@media(max-width:700px){.js-plotly-plot .heatmaplayer text{display:none}}</style>",
                unsafe_allow_html=True)
    with card("od"):
        cl, cr = st.columns([2, 3], vertical_alignment="center")
        skl = cl.segmented_control(
            "Skala warna", ["Logaritmik", "Linear"], default="Logaritmik", key="fl_skala",
            help="Nilai antar sel sangat timpang (puluhan hingga lebih dari 1 juta); skala log "
                 "menjaga sel kecil tetap terlihat.") or "Logaritmik"
        with cr:
            if focus_t:
                chips([(VERM, f"Kotak merah = {focus}")])
        if agg.empty:
            st.warning("Tidak ada data untuk filter ini.")
        else:
            h = agg.rename(columns={"Asal": "Y", "T": "X"})
            h["Rank"] = h["Value"].rank(ascending=False, method="min")
            show(heatmap(h, focus_t, log=(skl == "Logaritmik")))
    tp = neg.nlargest(1, "Value").iloc[0]
    sh5 = neg.nlargest(5, "Value")["Value"].sum() / neg["Value"].sum()
    kosong = (neg["Value"] == 0).mean()
    insight(f"Pasangan negara-pintu terbesar adalah <b>{esc(tp['Asal'])} → {esc(tp['Tujuan'])}</b> "
            f"({fmt_id(tp['Value'])} kunjungan). Lima pasangan teratas menyumbang <b>{sh5:.0%}</b> dari seluruh "
            f"kunjungan, sedangkan <b>{kosong:.0%}</b> kombinasi negara dan pintu tidak mencatat kunjungan. Pola ini "
            "menunjukkan kedatangan yang terspesialisasi: negara tertentu cenderung memakai pintu tertentu dan tidak "
            "tersebar merata ke semua pintu.")
    chapter(3, "bab-3", "Chord", "Bagaimana pola perjalanan wisatawan antarprovinsi?",
            f"Sebesar <b>{self_share:.0%}</b> perjalanan wisatawan nusantara berlangsung di dalam provinsi yang "
            "sama. Perjalanan dalam provinsi dikeluarkan secara bawaan agar keterkaitan antarprovinsi dapat "
            "diamati dengan jelas.", VERM)
    with panel("cfilter", "Filter chord" + (f" · fokus {focus}" if focus else "")):
        c1, c2, c3, c4 = st.columns([2, 3, 2, 2], vertical_alignment="center")
        top_n_c = c1.slider("Jumlah provinsi teratas", 8, 38, 20, key="fl_cn")
        c_min = c2.slider("Ambang minimum aliran (perjalanan)", 0, 2_000_000, 0, 10_000,
                          key="fl_cmin", help="0 = semua aliran ditampilkan, sehingga semua provinsi asal terlihat.")
        include_self = c3.checkbox("Sertakan perjalanan dalam provinsi", value=False, key="fl_cself")
        use_sqrt = c4.checkbox("Skala akar pita", value=False, key="fl_csqrt",
                               help="Memperjelas aliran kecil. Tooltip tetap menampilkan angka asli.")
    st.write("")
    left, right = st.columns([5, 3])
    with left, card("chord"):
        html = chord_html(c, focus, top_n_c, c_min, include_self, use_sqrt)
        if html is None:
            st.warning("Tidak ada aliran yang memenuhi filter. Turunkan ambang minimum.")
        else:
            components.html(html, height=720, scrolling=False)
    with right, card("bar"):
        show(top_pairs_bar(c, focus))

    masuk = nonself.groupby("Tujuan")["Value"].sum()
    keluar = nonself.groupby("Asal")["Value"].sum()
    neto = masuk.sub(keluar, fill_value=0).sort_values()
    teratas = masuk.nlargest(5)
    pasang = nonself.nlargest(1, "Value").iloc[0]
    reg = nonself.assign(a=nonself["Asal"].map(REGION_OF), t=nonself["Tujuan"].map(REGION_OF))
    sewilayah = reg.loc[reg["a"] == reg["t"], "Value"].sum() / reg["Value"].sum()
    insight(f"Perjalanan dalam provinsi mencapai <b>{self_share:.0%}</b> dari seluruh perjalanan wisatawan nusantara, "
            f"sehingga dikeluarkan secara bawaan. Dari perjalanan antarprovinsi, lima provinsi tujuan teratas "
            f"({esc(', '.join(teratas.index))}) menerima <b>{teratas.sum() / masuk.sum():.0%}</b>, dan "
            f"<b>{sewilayah:.0%}</b> terjadi di dalam wilayah yang sama. Aliran terbesar adalah "
            f"<b>{esc(pasang.Asal)} → {esc(pasang.Tujuan)}</b> ({fmt_id(pasang.Value)} perjalanan). Selisih bersih "
            f"perjalanan masuk dan keluar paling positif di <b>{esc(neto.index[-1])}</b> (+{compact(neto.iloc[-1])}) "
            f"dan paling negatif di <b>{esc(neto.index[0])}</b> (−{compact(abs(neto.iloc[0]))}). Wisatawan nusantara "
            "cenderung bepergian ke wilayah yang dekat, dengan Pulau Jawa sebagai pusat arus.")
    st.write("")
    st.write("")
    with st.expander("Sumber data"):
        st.markdown("- " + kutip("manca", True))
        st.markdown("- " + kutip("od", True))
        st.caption(CATATAN_WISMAN)