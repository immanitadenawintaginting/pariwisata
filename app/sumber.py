AKSES = "2 Oktober 2026"
TAHUN = "2025"
CATATAN_WISMAN = ("Data wisatawan mancanegara memakai tahun 2024 karena data 2025 belum tersedia; "
                  "data lainnya memakai tahun 2025.")

SUMBER = {
    "multi": dict(
        isi="Variabel akomodasi (jumlah akomodasi, kamar, tempat tidur, TPK, lama menginap) per provinsi",
        judul="Statistik Indonesia 2026", tahun=TAHUN, akses=AKSES,
        url="https://www.bps.go.id/id/publication/2026/02/27/a43f03f45543dc4e9942f44c/statistik-indonesia-2026.html"),
    "od": dict(
        isi="Perjalanan wisatawan nusantara antarprovinsi (asal-tujuan)",
        judul="Statistik Wisatawan Nusantara 2025", tahun="2025", akses=AKSES,
        url="https://www.bps.go.id/id/publication/2026/04/30/06948320ebe75b7678b09c56/statistik-wisatawan-nusantara-2025.html"),
    "manca": dict(
        isi="Kunjungan wisman menurut pintu kedatangan dan negara asal",
        judul="Statistik Kunjungan Wisatawan Mancanegara 2024", tahun="2024", akses=AKSES,
        url="https://www.bps.go.id/id/publication/2025/03/20/a85d584df19ea65a5e2b3d0b/statistik-kunjungan-wisatawan-mancanegara-2024.html"),
}


def kutip(kunci, dengan_isi=False):
    s = SUMBER[kunci]
    label = s["url"]
    awal = f"**{s['isi']}.** " if dengan_isi else ""
    return f"{awal}Sumber: BPS. {s['judul']}, {s['tahun']}. [{label}](<{s['url']}>) (diakses {s['akses']})."