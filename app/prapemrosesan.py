import numpy as np
import pandas as pd

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

# singkatan di data wisman disamakan dengan nama provinsi di chord.csv
ALIAS_PROV = {"NTT": "Nusa Tenggara Timur", "NTB": "Nusa Tenggara Barat", "DIY": "DI Yogyakarta",
              "Kep. Riau": "Kepulauan Riau", "DK Jakarta": "DKI Jakarta"}
# tujuan yang bukan pintu di provinsi tertentu; labelnya dipangkas ke bahasa Indonesia
TUJUAN_KHUSUS = {"Perbatasan Laut Sea Border": "Perbatasan laut",
                 "Perbatasan Darat Land Border": "Perbatasan darat",
                 "Lainnya Others": "Pintu lainnya"}
# salah ketik di tabel sumber
KOREKSI_PINTU = {"Sam Ratalungi": "Sam Ratulangi", "Hassanudin": "Hasanuddin"}


def bersihkan_flow(raw):
    """Sheet Flow (asal, pintu kedatangan, jumlah) -> tabel bersih.
    Mengembalikan (data, jumlah pasangan asal-tujuan yang bernilai 0)."""
    d = raw.iloc[:, :3].copy()
    d.columns = ["Asal", "Tujuan", "Value"]
    # nama negara dwibahasa ("Singapura/Singapore"), ambil bagian Indonesia
    d["Asal"] = d["Asal"].astype(str).str.split("/").str[0].str.strip()
    d["Tujuan"] = d["Tujuan"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    # sel kosong atau "—" artinya tidak ada kunjungan
    d["Value"] = pd.to_numeric(d["Value"], errors="coerce").fillna(0)

    # "Nama pintu, Provinsi" dipecah; spasi setelah koma di sumber tidak konsisten
    khusus = d["Tujuan"].isin(TUJUAN_KHUSUS)
    pecah = d["Tujuan"].str.rsplit(",", n=1, expand=True)
    pintu = pecah[0].str.strip().replace(KOREKSI_PINTU, regex=True)
    prov_raw = pecah[1].fillna("").str.strip()
    d["Pintu"] = np.where(khusus, d["Tujuan"].map(TUJUAN_KHUSUS), pintu)
    d["Provinsi"] = np.where(khusus, d["Tujuan"].map(TUJUAN_KHUSUS), prov_raw.replace(ALIAS_PROV))
    d["Tujuan"] = np.where(khusus, d["Pintu"], pintu + ", " + prov_raw)

    # beberapa baris "Lainnya" ganda, dijumlahkan supaya total tidak berubah
    d = d.groupby(["Asal", "Tujuan", "Pintu", "Provinsi"], as_index=False)["Value"].sum()
    n_kosong = int((d["Value"] == 0).sum())
    d = d[d["Value"] >= 0].copy()
    # "Asean Lainnya" dan sejenisnya itu kelompok negara, bukan satu negara
    d["Kategori"] = np.where(d["Asal"].str.endswith("Lainnya"), "Kelompok", "Negara")
    return d.reset_index(drop=True), n_kosong


def susun_hierarki(geo):
    """Sheet GeoNMulti (satu baris per provinsi) -> dua tabel panjang untuk tab Hierarki."""
    geo = geo.copy()
    geo["Provinsi"] = geo["Provinsi"].astype(str).str.strip()
    geo["Pulau"] = geo["Provinsi"].map(PULAU_DARI).fillna("Lainnya")

    # akomodasi: satu baris per provinsi x jenis (bintang / non-bintang)
    akom = []
    for _, r in geo.iterrows():
        for jenis, s in (("Bintang", "Bintang"), ("Non-Bintang", "NonBintang")):
            akom.append(dict(
                Pulau=r["Pulau"], Provinsi=r["Provinsi"], Jenis=jenis,
                Akomodasi=int(r[f"Akomodasi_{s}"]), Kamar=int(r[f"Kamar_{s}"]),
                TempatTidur=int(r[f"TempatTidur_{s}"]), TPK=float(r[f"TPK_{s}"]),
                Lama=float(r[f"LamaMenginap_{s}"])))

    # wisatawan: total perjalanan ke provinsi dibagi menurut persentase jenis kelamin
    gender = []
    for _, r in geo.iterrows():
        tot = float(r["JumlahWisatawanTujuan"])
        for jk in ("Laki-laki", "Perempuan"):
            gender.append(dict(
                Pulau=r["Pulau"], Provinsi=r["Provinsi"], JK=jk,
                Ukuran=round(tot * float(r[jk]) / 100), Warna=float(r["Perempuan"])))
    return pd.DataFrame(akom), pd.DataFrame(gender)