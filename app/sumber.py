"""Satu tempat untuk seluruh keterangan sumber data (soal poin 2b).

Ubah TAHUN / AKSES di sini; semua tab ikut berubah.
"""
AKSES = "2 Oktober 2026"
TAHUN = "2024"  # PERIKSA: samakan dengan tahun data pada tiap tabel BPS

SUMBER = {
    "tpk": dict(
        isi="TPK hotel bintang dan non-bintang",
        judul="Tingkat Penghunian Kamar Hotel (Persen)", tahun=TAHUN, akses=AKSES,
        url="https://www.bps.go.id/id/statistics-table/2/MjgyIzI=/tingkat-penghunian-kamar-hotel--persen-.html"),
    "wisnus_asal": dict(
        isi="Perjalanan wisatawan nusantara menurut provinsi asal",
        judul="Jumlah Perjalanan Wisatawan Nusantara", tahun=TAHUN, akses=AKSES,
        url="https://www.bps.go.id/id/statistics-table/2/MTE4OSMy/jumlah-perjalanan-wisatawan-nusantara.html"),
    "wisnus_tujuan": dict(
        isi="Perjalanan wisatawan nusantara menurut provinsi tujuan",
        judul="Jumlah Perjalanan Wisatawan Nusantara menurut Provinsi Tujuan (Perjalanan)",
        tahun=TAHUN, akses=AKSES,
        url="https://www.bps.go.id/id/statistics-table/2/MjIwMSMy/jumlah-perjalanan-wisatawan-nusantara-menurut-provinsi-tujuan--perjalanan-.html"),
    "multi": dict(
        isi="Variabel akomodasi (jumlah akomodasi, kamar, tempat tidur, lama menginap) per provinsi",
        judul="Berkas unduhan tabel BPS: variabel analisis multivariat", tahun=TAHUN, akses=AKSES,
        url="https://web-api.bps.go.id/download.php?f=qCKI/A2e88rmwT69+bzz21VvYjNuNDRoV2VuYldVK3huY0Q2aXNiVDdWczJDeUVnVlZIZHVBRE85U1FxTFVHek81dVU4eTZ5NWtQMGxJaGVyYlVjQzk1d3o0MkZkYmVDRnBIKzRod25iL241Uk9hWmI3TURpY3ZudTVkTnIycmFLZk5WNFoxcTNGclRhWHhWaE5ncG5YekRuRS9oZU1tRUZvNUZ4Uy9STnpvWEZuQ0U2cjh3anBzSTBhUEpqaXhwSVpQRzNzc0xSelFWT2p2NXhuVzZhdzk5TXRaQTNYanFrSDVxUTNING11NE5aOU9hS2hBdFhjRkxEc0JEcmhXWm54WVdENzhrdVZvR1IwM1Q="),
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
    """Kalimat sumber (markdown): Sumber: BPS. Judul, tahun. URL (diakses ...)."""
    s = SUMBER[kunci]
    label = "tautan unduhan" if "web-api.bps.go.id" in s["url"] else s["url"]
    awal = f"**{s['isi']}.** " if dengan_isi else ""
    return f"{awal}Sumber: BPS. {s['judul']}, {s['tahun']}. [{label}](<{s['url']}>) (diakses {s['akses']})."