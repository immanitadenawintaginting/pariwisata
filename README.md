# Pariwisata Indonesia: Dasbor Visualisasi Data BPS

Dasbor interaktif tentang pariwisata Indonesia: dari mana wisatawan datang, ke mana mereka bepergian, dan bagaimana akomodasi tersebar di 38 provinsi. Dibuat untuk UAS Visualisasi Data dan Informasi (Politeknik Statistika STIS, 2026).

- **Aplikasi:** https://pariwisatavisualisasi.streamlit.app/
- **Repositori:** https://github.com/immanitadenawintaginting/pariwisata
- **Pembuat:** [Immanita Denawinta Ginting] · [222313138] · [3SD1]

## Topik visualisasi

| Topik | Tab | Teknik |
|---|---|---|
| Aliran (flow) | Aliran | Sankey, matriks asal-tujuan (OD), chord diagram, bar 10 aliran terbesar |
| Data berdimensi tinggi | Multivariat | PCA biplot, scatterplot matrix, parallel coordinates, profil klaster (z-score), dengan brushing dan linking |
| Data berhierarki | Hierarki | Treemap, sunburst, icicle dengan drill-down dan breadcrumb |

## Data

Semua data utama dari BPS. Tanggal akses 2 Oktober 2026.

| Isi | Publikasi BPS | Tahun |
|---|---|---|
| Kunjungan wisman menurut pintu kedatangan dan negara asal | [Statistik Kunjungan Wisatawan Mancanegara 2024](https://www.bps.go.id/id/publication/2025/03/20/a85d584df19ea65a5e2b3d0b/statistik-kunjungan-wisatawan-mancanegara-2024.html) | 2024 |
| Perjalanan wisatawan nusantara antarprovinsi (asal-tujuan) | [Statistik Wisatawan Nusantara 2025](https://www.bps.go.id/id/publication/2026/04/30/06948320ebe75b7678b09c56/statistik-wisatawan-nusantara-2025.html) | 2025 |
| Variabel akomodasi (jumlah akomodasi, kamar, tempat tidur, TPK, lama menginap) per provinsi | [Statistik Indonesia 2026](https://www.bps.go.id/id/publication/2026/02/27/a43f03f45543dc4e9942f44c/statistik-indonesia-2026.html) | 2025 |

**Catatan tahun:** data wisatawan mancanegara memakai tahun 2024 karena publikasi 2025 belum tersedia. Data lainnya tahun 2025.

Tab Multivariat memakai sumber akomodasi; tab Hierarki memakai sumber akomodasi dan sumber wisatawan nusantara. Perbandingan lintas sumber perlu dibaca dengan memperhatikan perbedaan ini.

Seluruh keterangan sumber (judul, tahun, URL, tanggal akses) disimpan di satu tempat, `app/sumber.py`, dan setiap visualisasi mencantumkan "Sumber: BPS".

## Pra-pemrosesan

Data mentah ada di `data/raw/` (`Data_Visdat.xlsx` hasil penyusunan dari tabel BPS, dan `chord.csv`). Logika pembersihan ada di `app/prapemrosesan.py` dan dipakai oleh aplikasi maupun skrip.

Sheet `Flow` (wisman):
1. Nama negara dwibahasa ("Singapura/Singapore") diambil bagian Indonesianya.
2. Kolom tujuan berbentuk "Nama pintu, Provinsi" dipecah menjadi pintu dan provinsi; spasi ganda dirapikan.
3. Singkatan provinsi (NTT, NTB, DIY, Kep. Riau, DK Jakarta) disamakan dengan nama baku.
4. Dua salah ketik nama bandara dikoreksi (Sam Ratulangi, Hasanuddin).
5. Tujuan non-pintu ("Perbatasan Laut", "Perbatasan Darat", "Lainnya") dipertahankan dengan label bahasa Indonesia.
6. Sel kosong dianggap tidak ada kunjungan (0). Baris ganda dijumlahkan.
7. Asal berakhiran "Lainnya" diberi kategori *Kelompok*, bukan *Negara*, supaya tidak tercampur saat menghitung jumlah negara.

Sheet `GeoNMulti` (satu baris per provinsi):
1. Provinsi dipetakan ke tujuh kelompok pulau untuk level hierarki.
2. Variabel akomodasi diubah ke bentuk panjang (provinsi x bintang/non-bintang).
3. Jumlah perjalanan per provinsi tujuan dibagi menurut persentase laki-laki dan perempuan.
4. Untuk analisis multivariat, variabel jumlah di-log10, lalu semua variabel distandarkan sebelum PCA dan K-Means.

Untuk menghasilkan versi terolah sebagai berkas CSV:

```
python scripts/01_prepare.py
```

Keluarannya ada di `data/processed/`: `flow_bersih.csv`, `akomodasi_long.csv`, `wisatawan_jk_long.csv`, dan salinan `chord.csv`.

## Menjalankan di komputer sendiri

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/app.py
```

Di Windows bisa juga klik dua kali `jalankan.bat` (setelah `.venv` dibuat).

## Struktur

```
app/
  app.py               titik masuk, tab, pembaca data
  prapemrosesan.py     pembersihan data
  sumber.py            keterangan sumber
  theme.py             gaya dan komponen tampilan
  tabs/                beranda, flow, multivariat, hierarki 
assets/                logo dan video latar beranda
data/raw/              data mentah
data/processed/        data terolah
scripts/01_prepare.py  membuat data terolah
.streamlit/config.toml tema
```

## Interaksi dan rancangan

- Tooltip pada semua grafik; filter provinsi, negara, pintu, dan ambang nilai; drill-down dengan breadcrumb (hierarki); brushing dan linking antar grafik (multivariat); klik busur untuk menyorot (chord).
- Warna kategori memakai palet Okabe-Ito yang ramah buta warna; skala kontinu memakai Viridis dan Cividis.
- Tampilan disesuaikan untuk laptop dan ponsel. Grafik yang padat (parallel coordinates, scatterplot matrix) dapat digeser ke samping di layar sempit, dan angka di dalam sel matriks OD disembunyikan di layar sempit (nilai tetap muncul saat disentuh).

## Keterbatasan

- Data wisman (2024) dan data lainnya (2025) tidak sama tahun.
- Matriks perjalanan antarprovinsi memuat perjalanan dalam provinsi yang sama dalam jumlah besar, sehingga bagian itu dikeluarkan secara bawaan di chord agar pola antarprovinsi terlihat.
- Jumlah perjalanan menurut jenis kelamin dihitung dari persentase, jadi ada pembulatan.
- Klaster dan pencilan bergantung pada pilihan variabel dan transformasi log.

## Kredit dan alat bantu

- Video latar beranda: YouTube.
- Font Plus Jakarta Sans (Google Fonts). Pustaka: Streamlit, Plotly, D3.js, pandas, scikit-learn.
- Alat bantu AI (Claude, Anthropic) dipakai untuk membantu penulisan dan perbaikan kode serta tampilan.