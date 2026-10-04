import json
from html import escape as esc
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from scipy.stats import chi2
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from sumber import kutip
from theme import card, chapter, hero, inject_theme, insight, kpi_card, panel, polish, story_nav

from .flow import REGION_COLOR, REGION_OF, REGION_ORDER

HTML_PATH = Path(__file__).parent / "multivariat.html"

METRIK = {
    "TPK": dict(nama="TPK", pendek="TPK", satuan="%", log=False, tema="hunian"),
    "Akomodasi": dict(nama="Jumlah akomodasi", pendek="Akomodasi", satuan="unit", log=True, tema="skala"),
    "Kamar": dict(nama="Jumlah kamar", pendek="Kamar", satuan="unit", log=True, tema="skala"),
    "TempatTidur": dict(nama="Jumlah tempat tidur", pendek="Tempat tidur", satuan="unit", log=True, tema="skala"),
    "LamaInap": dict(nama="Rata-rata lama menginap", pendek="Lama menginap", satuan="malam", log=False, tema="hunian"),
}
JENIS = {"Bintang": "bintang", "NonBintang": "non-bintang"}
VARIABEL = [f"{m}_{j}" for m in METRIK for j in JENIS]
EXTRA = {
    "Wisatawan_Tujuan": dict(nama="Jumlah wisatawan tujuan", pendek="Wisatawan tujuan", satuan="orang",
                             log=True, tema="skala"),
    "Pct_Perempuan": dict(nama="Wisatawan perempuan", pendek="Wisatawan perempuan", satuan="%",
                          log=False, tema="lain"),
}
RENAME = {
    "LamaMenginap_Bintang": "LamaInap_Bintang", "LamaMenginap_NonBintang": "LamaInap_NonBintang",
    "JumlahWisatawanTujuan": "Wisatawan_Tujuan", "Perempuan": "Pct_Perempuan",
}
SPLOM_DEFAULT = ["TPK_Bintang", "TPK_NonBintang", "Kamar_Bintang", "Akomodasi_NonBintang", "LamaInap_Bintang"]

PALET = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00"]
ABU = "#B8B8B8"


def _meta(v):
    if v in EXTRA:
        return EXTRA[v], None
    m, j = v.split("_")
    return METRIK[m], JENIS[j]


def label(v, mode="full"):
    m, j = _meta(v)
    if mode == "axis":
        return f"{m['pendek']}<br>{j}" if j else m["pendek"].replace(" ", "<br>", 1)
    if mode == "short":
        return f"{m['pendek']} {j}" if j else m["pendek"]
    return f"{m['nama']} {j} ({m['satuan']})" if j else f"{m['nama']} ({m['satuan']})"


def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def fmt_val(v, x):
    m, _ = _meta(v)
    return fmt(x, 2 if m["satuan"] in ("%", "malam") else 0)


@st.cache_data
def _muat(raw: pd.DataFrame) -> pd.DataFrame:
    d = raw.loc[:, ~raw.columns.astype(str).str.startswith("Unnamed")].copy()
    d = d.dropna(subset=["Provinsi"]).rename(columns=RENAME)
    d["Provinsi"] = d["Provinsi"].astype(str).str.strip()
    d["Wilayah"] = d["Provinsi"].map(REGION_OF).fillna("Maluku & Papua")
    return d.reset_index(drop=True)


def _transform(df, vars_, log):
    X = df[vars_].astype(float).copy()
    if log:
        for v in vars_:
            if _meta(v)[0]["log"]:
                # jumlah akomodasi/kamar sangat miring ke kanan, di-log biar Jakarta dkk tidak mendominasi
                X[v] = np.log10(X[v])
    return X


@st.cache_data(show_spinner=False)
def _analisis(X: pd.DataFrame, k: int):
    Z = StandardScaler().fit_transform(X.values)
    pca = PCA().fit(Z)
    skor = pca.transform(Z)
    komp = pca.components_.copy()
    for c in range(2):
        # tanda PC bisa terbalik tiap dijalankan, dibuat tetap
        if komp[c].sum() < 0:
            komp[c] *= -1
            skor[:, c] *= -1
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(Z)
    # K1 = klaster dengan rata-rata z paling rendah
    urut = np.argsort([Z[km.labels_ == c].mean() for c in range(k)])
    peta = {old: new for new, old in enumerate(urut)}
    klaster = np.array([peta[c] for c in km.labels_])
    sil = float(silhouette_score(Z, klaster))
    m = max(2, int(np.searchsorted(np.cumsum(pca.explained_variance_ratio_), 0.80) + 1))
    # jarak mahalanobis pada PC yang menjelaskan >=80% ragam, dipakai untuk pencilan
    d2 = (skor[:, :m] ** 2 / pca.explained_variance_[:m]).sum(axis=1)
    return dict(Z=Z, ev=pca.explained_variance_ratio_, evar=pca.explained_variance_, komp=komp,
                skor=skor, klaster=klaster, sil=sil, d2=d2, batas=float(chi2.ppf(0.975, df=m)),
                m=m)


def _nama_klaster(Z, klaster, vars_, k):
    tema = np.array([_meta(v)[0]["tema"] for v in vars_])
    nama = []
    for c in range(k):
        mk = klaster == c
        bagian = []
        for t, kata in (("skala", ("kecil", "sedang", "besar")), ("hunian", ("rendah", "sedang", "tinggi"))):
            if (tema == t).any() and mk.any():
                z = Z[mk][:, tema == t].mean()
                bagian.append(f"{'skala' if t == 'skala' else 'hunian'} {kata[0] if z < -0.5 else kata[2] if z > 0.5 else kata[1]}")
        nama.append(f"K{c + 1}: " + ", ".join(bagian) if bagian else f"K{c + 1}")
    return nama


def _ticks_log(lo, hi):
    tv, tt = [], []
    for e in range(int(np.floor(lo)) - 1, int(np.ceil(hi)) + 1):
        for f in (1, 2, 5):
            t = np.log10(f * 10.0 ** e)
            if lo - 0.02 <= t <= hi + 0.02:
                tv.append(round(float(t), 4))
                tt.append(fmt(f * 10.0 ** e))
    return tv, tt


def _tema():
    return dict(fg="#0F172A", muted="#64748B", line="rgba(128,128,128,.30)", grid="#E6E8EC",
                zero="#B8BDC7", bg="#FFFFFF", bgA="rgba(255,255,255,.75)", arrow="#444B5A", grey="#C4C8D0")


def _payload(df, X, A, vars_, splom, k, nama_k, outlier, log):
    n = len(df)
    sk, L = A["skor"][:, :2], A["komp"][:2].T
    ext = np.quantile(np.hypot(sk[:, 0], sk[:, 1]), 0.85)
    s = ext / np.hypot(L[:, 0], L[:, 1]).max()
    ev = A["ev"] * 100
    pca = dict(x=np.round(sk[:, 0], 3).tolist(), y=np.round(sk[:, 1], 3).tolist(),
               xt=f"PC1 ({fmt(ev[0], 1)}%)", yt=f"PC2 ({fmt(ev[1], 1)}%)",
               loadings=[dict(lab=label(v, "short"), x=round(float(L[i, 0] * s), 3), y=round(float(L[i, 1] * s), 3))
                         for i, v in enumerate(vars_)])
    wil = [w for w in REGION_ORDER if (df.Wilayah == w).any()]
    col = {
        "Klaster": dict(names=nama_k, colors=PALET[:k], idx=A["klaster"].tolist()),
        "Wilayah": dict(names=wil, colors=[REGION_COLOR[w] for w in wil],
                        idx=df.Wilayah.map({w: i for i, w in enumerate(wil)}).tolist()),
    }
    vs = []
    for v in vars_:
        m, _ = _meta(v)
        raw = df[v].astype(float).values
        plot = X[v].values
        pad = (plot.max() - plot.min()) * 0.04 or 0.1
        lo, hi = float(plot.min() - pad), float(plot.max() + pad)
        d = dict(key=v, lab=label(v, "axis"), short=label(v, "short"), unit=m["satuan"],
                 log=bool(log and m["log"]), raw=np.round(raw, 3).tolist(), plot=np.round(plot, 4).tolist(),
                 range=[round(lo, 4), round(hi, 4)])
        if d["log"]:
            d["tv"], d["tt"] = _ticks_log(lo, hi)
        vs.append(d)
    hover = []
    for i in range(n):
        baris = [f"<b>{esc(df.Provinsi[i])}</b>", f"{esc(df.Wilayah[i])} · {esc(nama_k[A['klaster'][i]])}"]
        if outlier[i]:
            baris.append("◆ pencilan multivariat")
        baris += [f"{label(v, 'short')}: {fmt_val(v, df[v][i])} {_meta(v)[0]['satuan']}" for v in vars_]
        hover.append("<br>".join(baris))
    return dict(theme=_tema(), proj0="PCA", prov=df.Provinsi.tolist(), outlier=[bool(o) for o in outlier],
                hover=hover, col=col, emb={"PCA": pca}, vars=vs,
                Z=np.round(A["Z"], 3).tolist(),
                splom=[vars_.index(v) for v in splom if v in vars_])


def _judul(teks, sub):
    return dict(text=f"<b>{teks}</b><br><sup>{sub} · Sumber: BPS</sup>", x=0.01, xanchor="left")


def _rgba(h, a):
    return f"rgba({int(h[1:3], 16)},{int(h[3:5], 16)},{int(h[5:7], 16)},{a})"


def fig_radar(A, vars_, k, nama_k):
    th = [label(v, "short") for v in vars_]
    fig = go.Figure()
    for c in range(k):
        mk = A["klaster"] == c
        if not mk.any():
            continue
        r = A["Z"][mk].mean(axis=0)
        fig.add_trace(go.Scatterpolar(
            r=np.r_[r, r[0]], theta=th + th[:1], name=f"{nama_k[c]} ({mk.sum()})", fill="toself", opacity=0.9,
            line=dict(color=PALET[c], width=2), fillcolor=_rgba(PALET[c], 0.18),
            hovertemplate="%{theta}<br>rata-rata z = %{r:.2f}<extra>" + nama_k[c] + "</extra>"))
    lim = float(np.ceil(max(1.5, np.abs(np.vstack([A["Z"][A["klaster"] == c].mean(axis=0) for c in range(k)
                                                  if (A["klaster"] == c).any()])).max())))
    fig.update_layout(
        title=_judul("Radar profil klaster", "Rata-rata z-score; lingkaran 0 = rata-rata nasional"),
        polar=dict(radialaxis=dict(range=[-lim, lim], tickfont=dict(size=9)),
                   angularaxis=dict(tickfont=dict(size=10))),
        height=420, margin=dict(l=60, r=60, t=64, b=50), legend=dict(orientation="h", y=-0.08),
        separators=",.")
    return fig


def fig_scree(A):
    ev = A["ev"] * 100
    x = [f"PC{i + 1}" for i in range(len(ev))]
    fig = go.Figure()
    fig.add_bar(x=x, y=ev, name="Per komponen", marker_color=PALET[0])
    fig.add_scatter(x=x, y=np.cumsum(ev), name="Kumulatif", mode="lines+markers", line=dict(color=PALET[5]))
    fig.update_layout(title=_judul("Scree plot", "Ragam yang dijelaskan tiap komponen utama"),
                      yaxis_title="Ragam dijelaskan (%)", height=320, margin=dict(t=64),
                      legend=dict(orientation="h", y=-0.2), separators=",.")
    return fig


def fig_loading(A, vars_):
    th = [label(v, "short") for v in vars_]
    fig = go.Figure()
    for c, wr in ((0, PALET[0]), (1, PALET[1])):
        fig.add_bar(y=th, x=A["komp"][c], orientation="h", name=f"PC{c + 1} ({A['ev'][c] * 100:.1f}%)".replace(".", ","),
                    marker_color=wr)
    fig.update_layout(barmode="group", title=_judul("Loading komponen utama", "Bobot variabel pada PC1 dan PC2"),
                      yaxis=dict(autorange="reversed"), xaxis_title="Loading", height=320, margin=dict(t=64),
                      legend=dict(orientation="h", y=-0.2), separators=",.")
    return fig


def _tafsir_pc(L, vars_):
    w = L ** 2
    tema = np.array([_meta(v)[0]["tema"] for v in vars_])
    sh = {t: w[tema == t].sum() / w.sum() for t in set(tema)}
    top = np.argsort(-np.abs(L))[:3]
    daftar = ", ".join(f"{label(vars_[i], 'short')} ({'+' if L[i] > 0 else '−'}{abs(L[i]):.2f})".replace(".", ",")
                       for i in top)
    if sh.get("skala", 0) >= 0.6:
        judul = "skala akomodasi (jumlah usaha, kamar, tempat tidur)"
    elif sh.get("hunian", 0) >= 0.6:
        judul = "kinerja hunian (TPK dan lama menginap)"
    else:
        judul = "campuran skala dan kinerja hunian"
    return judul, daftar


def _profil(Z, mk, vars_):
    z = pd.Series(Z[mk].mean(axis=0), index=vars_)
    tinggi = [label(v, "short") for v in z[z > 0.5].sort_values(ascending=False).index[:3]]
    rendah = [label(v, "short") for v in z[z < -0.5].sort_values().index[:3]]
    s = ("tinggi pada " + ", ".join(tinggi)) if tinggi else "tidak ada variabel yang menonjol tinggi"
    s += ("; rendah pada " + ", ".join(rendah) + ".") if rendah else "."
    return s


IKON = {"#0072B2": "🗺️", "#009E73": "📈", "#E69F00": "🧩", "#D55E00": "🚩"}


def _kpi(col, lab, val, sub="", color="#0072B2"):
    kpi_card(col, IKON.get(color, "•"), lab, val, sub, color)


def render(load_sheet):
    inject_theme()
    df = _muat(load_sheet("GeoNMulti"))
    kurang = [v for v in VARIABEL + list(EXTRA) if v not in df.columns]
    if kurang:
        st.error(f"Kolom tidak ada di sheet GeoNMulti: {kurang}")
        return

    tot_k = float(df[["Kamar_Bintang", "Kamar_NonBintang"]].sum().sum())
    tot_a = float(df[["Akomodasi_Bintang", "Akomodasi_NonBintang"]].sum().sum())
    hero("", "Kemiripan profil <em>akomodasi</em> antarprovinsi",
         f"Analisis multivariat terhadap {len(df)} provinsi menggunakan {len(VARIABEL)} indikator akomodasi. "
         "Reduksi dimensi (PCA) dan pengelompokan K-Means digunakan untuk mengidentifikasi kemiripan profil "
         "serta provinsi pencilan.",
         [(len(df), "provinsi"), (len(VARIABEL), "variabel inti"), (tot_a, "usaha akomodasi"), (tot_k, "kamar")])
    story_nav([("mv-1", "1 · Kemiripan profil provinsi"), ("mv-2", "2 · Karakteristik kelompok")])

    with panel("mv_filter", "Pengaturan analisis"):
        c1, c2 = st.columns([1, 1], vertical_alignment="center")
        k = c1.slider("Jumlah klaster (K-Means)", 2, 6, 3, key="mv_k",
                      help="Klaster dibentuk dari variabel terstandar. Klaster 1 = profil terendah.")
        log = c2.toggle("Skala log10 untuk variabel jumlah", value=True, key="mv_log",
                        help="Jumlah akomodasi, kamar, dan tempat tidur sangat menjulur ke kanan "
                             "(DKI Jakarta, Jawa Barat, Bali jauh di atas lainnya). Log10 mencegah satu-dua "
                             "provinsi mendominasi PCA dan klaster. Label sumbu tetap dalam satuan asli.")
        with st.expander("Variabel yang dianalisis"):
            vars_ = st.multiselect("Variabel analisis", VARIABEL + list(EXTRA), default=VARIABEL, key="mv_vars",
                                   format_func=label,
                                   help="Dua variabel terakhir (wisatawan tujuan, % perempuan) opsional: bukan "
                                        "indikator akomodasi, sehingga tidak dipilih secara default.")
            pil = [v for v in SPLOM_DEFAULT if v in vars_]
            splom = st.multiselect("Variabel pada scatterplot matrix (2–6)", vars_, default=pil or vars_[:4],
                                   max_selections=6, format_func=lambda v: label(v, "short"), key="mv_splom")
    if len(vars_) < 8:
        st.warning("Pilih minimal 8 variabel numerik (syarat Lampiran A).")
        return
    if len(splom) < 2:
        st.info("Pilih minimal 2 variabel untuk scatterplot matrix.")
        return

    X = _transform(df, vars_, log)
    A = _analisis(X, k)
    outlier = A["d2"] > A["batas"]
    nama_k = _nama_klaster(A["Z"], A["klaster"], vars_, k)
    ev = A["ev"] * 100
    judul1, top1 = _tafsir_pc(A["komp"][0], vars_)
    judul2, top2 = _tafsir_pc(A["komp"][1], vars_)
    prov_out = df.Provinsi[outlier].tolist()

    k1, k2, k3, k4 = st.columns(4)
    _kpi(k1, "Data", f"{len(df)} × {len(vars_)}", "provinsi × variabel numerik")
    _kpi(k2, "Ragam PC1 + PC2", f"{fmt(ev[:2].sum(), 1)}%", f"PC1 {fmt(ev[0], 1)}% · PC2 {fmt(ev[1], 1)}%",
         "#009E73")
    s = A["sil"]
    _kpi(k3, "Kualitas klaster (silhouette)", fmt(s, 2),
         "kuat" if s >= 0.5 else "cukup" if s >= 0.25 else "lemah (batas klaster samar)", "#E69F00")
    _kpi(k4, "Pencilan", ", ".join(prov_out) if prov_out else "Tidak ada",
         f"{len(prov_out)} provinsi · ambang χ² = {fmt(A['batas'], 1)}", "#D55E00")

    klaster_kecil = pd.Series(A["klaster"]).value_counts().idxmin()
    insight(f"Komponen utama pertama (PC1, {fmt(ev[0], 1)}%) terutama membedakan provinsi berdasarkan "
            f"<b>{judul1}</b>, sedangkan PC2 ({fmt(ev[1], 1)}%) berdasarkan <b>{judul2}</b>. "
            + (f"Provinsi pencilan: <b>{esc(', '.join(prov_out))}</b>. " if prov_out else "")
            + f"K-Means membentuk {k} kelompok; kelompok dengan anggota paling sedikit adalah "
              f"<b>{esc(nama_k[klaster_kecil])}</b> ({int((A['klaster'] == klaster_kecil).sum())} provinsi).")

    chapter(1, "mv-1", "Linking dan brushing", "Provinsi mana yang memiliki profil serupa?",
            "Seleksi sekelompok provinsi pada satu grafik untuk melihat posisinya pada grafik lainnya. "
            "Gunakan kotak atau lasso pada biplot dan scatterplot matrix, atau tarik pada sumbu parallel coordinates.")
    html = HTML_PATH.read_text(encoding="utf-8").replace(
        "__DATA__", json.dumps(_payload(df, X, A, vars_, splom, k, nama_k, outlier, log), ensure_ascii=False))
    with card("linked"):
        components.html(html, height=1250, scrolling=False)
    satuan = ("Satuan: TPK (%), akomodasi/kamar/tempat tidur (unit), lama menginap (malam)"
              + (", wisatawan tujuan (orang)" if "Wisatawan_Tujuan" in vars_ else "")
              + (", wisatawan perempuan (%)" if "Pct_Perempuan" in vars_ else "") + ". "
              + ("Sumbu variabel jumlah berskala log10 (label dalam satuan asli). " if log else "")
              + "Warna memakai palet Okabe-Ito (ramah buta warna).")
    st.caption(satuan)
    chapter(2, "mv-2", "Interpretasi", "Apa karakteristik tiap kelompok dan provinsi mana yang menyimpang?",
            "Kelompok dibentuk dengan K-Means pada variabel yang telah distandarkan, sedangkan pencilan "
            "diidentifikasi menggunakan jarak Mahalanobis pada komponen utama.", "#009E73")
    t_k, t_p, t_c = st.tabs(["Kelompok provinsi", "Pencilan", "Komponen utama"])

    with t_k:
        a, b = st.columns([3, 2])
        a.plotly_chart(polish(fig_radar(A, vars_, k, nama_k)), width="stretch", key="mv_radar")
        with b:
            for c in range(k):
                mk = A["klaster"] == c
                if not mk.any():
                    continue
                st.markdown(
                    f'<div class="tile"><b><i style="background:{PALET[c]}"></i>{esc(nama_k[c])} '
                    f'({int(mk.sum())} provinsi)</b><br>{esc(_profil(A["Z"], mk, vars_))}<br>'
                    f'<small>{esc(", ".join(df.Provinsi[mk]))}</small></div>', unsafe_allow_html=True)
        prof = df[vars_].assign(Klaster=[nama_k[c] for c in A["klaster"]]).groupby("Klaster").mean()
        prof.columns = [label(v) for v in vars_]
        prof.insert(0, "Jumlah provinsi", pd.Series([nama_k[c] for c in A["klaster"]]).value_counts()
                    .reindex(prof.index))
        with st.expander("Rata-rata nilai asli per klaster"):
            st.dataframe(prof.round(2), width="stretch")

    with t_p:
        if outlier.any():
            Zdf = pd.DataFrame(A["Z"], columns=vars_)
            baris = []
            for i in np.where(outlier)[0]:
                v = Zdf.iloc[i].abs().idxmax()
                baris.append({"Provinsi": df.Provinsi[i], "Wilayah": df.Wilayah[i],
                              "Jarak Mahalanobis²": round(float(A["d2"][i]), 1),
                              "Variabel paling ekstrem": f"{label(v, 'short')} (z = {Zdf.iloc[i][v]:+.1f})"})
            st.dataframe(pd.DataFrame(baris).sort_values("Jarak Mahalanobis²", ascending=False),
                         width="stretch", hide_index=True)
        else:
            st.write("Tidak ada pencilan pada ambang yang dipakai.")
        st.caption(f"Metode: jarak Mahalanobis pada {A['m']} komponen utama pertama (≥ 80% ragam). Pencilan jika "
                   f"jarak² > χ² (df = {A['m']}, p = 0,975) = {fmt(A['batas'], 1)}. Pencilan di sini bukan "
                   "kesalahan data, melainkan provinsi yang skala akomodasinya jauh berbeda dari mayoritas.")

    with t_c:
        a, b = st.columns(2)
        a.plotly_chart(polish(fig_scree(A)), width="stretch", key="mv_scree")
        b.plotly_chart(polish(fig_loading(A, vars_)), width="stretch", key="mv_load")
        st.markdown(f"**PC1** ({fmt(ev[0], 1)}%): {judul1}. Variabel terkuat: {top1}.")
        st.markdown(f"**PC2** ({fmt(ev[1], 1)}%): {judul2}. Variabel terkuat: {top2}.")
        st.caption(f"PC1–PC{A['m']} menjelaskan {fmt(ev[:A['m']].sum(), 1)}% ragam dan dipakai untuk mendeteksi pencilan.")

    st.write("")
    with st.expander("Sumber data"):
        for k_ in ("multi",):
            st.markdown("- " + kutip(k_, True))