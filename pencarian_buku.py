"""
Tugas 1 - Analisis Algoritma
Sistem Pencarian Data Buku Perpustakaan Digital: Linear Search vs Binary Search
Kunci pencarian: judul buku (string). Dataset: Kaggle "15k books across 100 categories".

Cara pakai:  python pencarian_buku.py data_buku.csv
"""
import csv
import sys
import time
from dataclasses import dataclass, field
from typing import List, Optional


# =====================================================================
# 1. MODEL INPUT  (kelas Buku)  -> dipakai untuk menyimpan 1 baris dataset
# =====================================================================
@dataclass
class Buku:
    judul: str
    penulis: str = "-"
    kategori: str = "-"
    harga: str = "-"
    rating: str = "-"


# =====================================================================
# 2. MODEL OUTPUT (kelas HasilPencarian) -> dikembalikan oleh kedua algoritma
# =====================================================================
@dataclass
class HasilPencarian:
    algoritma: str
    kata_kunci: str
    ditemukan: bool
    indeks: int                      # posisi di list, -1 jika tidak ada
    buku: Optional[Buku]             # None jika tidak ditemukan
    jumlah_perbandingan: int
    waktu_us: float = 0.0            # mikrodetik, diisi saat pengujian


# =====================================================================
# 3. MEMBACA DATASET
# =====================================================================
def normalisasi(teks: str) -> str:
    """Huruf kecil + hapus spasi berlebih agar pencarian tidak sensitif huruf besar/kecil."""
    return " ".join(teks.lower().split())


def cari_kolom(header: List[str], kandidat: List[str]) -> Optional[str]:
    peta = {h.strip().lower(): h for h in header}
    for k in kandidat:
        if k in peta:
            return peta[k]
    return None


def baca_dataset(path: str) -> List[Buku]:
    daftar, sudah_ada = [], set()
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        h = reader.fieldnames
        k_judul = cari_kolom(h, ["title", "book_title", "book title", "name", "book"])
        k_penulis = cari_kolom(h, ["author", "authors", "book_author"])
        k_kategori = cari_kolom(h, ["category", "categories", "genre", "genres"])
        k_harga = cari_kolom(h, ["price", "list_price", "harga"])
        k_rating = cari_kolom(h, ["rating", "average_rating", "user rating"])
        if k_judul is None:
            raise ValueError(f"Kolom judul tidak ditemukan. Kolom yang ada: {h}")
        for baris in reader:
            judul = (baris[k_judul] or "").strip()
            kunci = normalisasi(judul)
            if not kunci or kunci in sudah_ada:      # buang kosong & judul ganda
                continue
            sudah_ada.add(kunci)
            daftar.append(Buku(
                judul=judul,
                penulis=baris[k_penulis] if k_penulis else "-",
                kategori=baris[k_kategori] if k_kategori else "-",
                harga=baris[k_harga] if k_harga else "-",
                rating=baris[k_rating] if k_rating else "-",
            ))
    return daftar


# =====================================================================
# 4. LINEAR SEARCH  (buatan sendiri, tanpa in / index())
# =====================================================================
def linear_search(data: List[Buku], kata_kunci: str) -> HasilPencarian:
    kunci = normalisasi(kata_kunci)
    perbandingan = 0
    for i in range(len(data)):
        perbandingan += 1                       # 1 operasi dasar = 1 perbandingan judul
        if normalisasi(data[i].judul) == kunci:
            return HasilPencarian("Linear Search", kata_kunci, True, i, data[i], perbandingan)
    return HasilPencarian("Linear Search", kata_kunci, False, -1, None, perbandingan)


# =====================================================================
# 5. BINARY SEARCH (buatan sendiri; data WAJIB sudah terurut berdasarkan judul)
# =====================================================================
def urutkan_data(data: List[Buku]) -> List[Buku]:
    return sorted(data, key=lambda b: normalisasi(b.judul))


def binary_search(data_terurut: List[Buku], kata_kunci: str) -> HasilPencarian:
    kunci = normalisasi(kata_kunci)
    kiri, kanan = 0, len(data_terurut) - 1
    perbandingan = 0
    while kiri <= kanan:
        tengah = (kiri + kanan) // 2
        judul_tengah = normalisasi(data_terurut[tengah].judul)
        perbandingan += 1                       # 1 iterasi = 1 perbandingan tiga arah (==, <, >)
        if kunci == judul_tengah:
            return HasilPencarian("Binary Search", kata_kunci, True, tengah, data_terurut[tengah], perbandingan)
        elif kunci < judul_tengah:
            kanan = tengah - 1
        else:
            kiri = tengah + 1
    return HasilPencarian("Binary Search", kata_kunci, False, -1, None, perbandingan)


# =====================================================================
# 6. TAMPILAN HASIL
# =====================================================================
def tampilkan(hasil: HasilPencarian) -> None:
    print(f"[{hasil.algoritma}] kata kunci: '{hasil.kata_kunci}'")
    if hasil.ditemukan:
        b = hasil.buku
        print("  Status      : DITEMUKAN")
        print(f"  Posisi      : indeks ke-{hasil.indeks}")
        print(f"  Judul       : {b.judul}")
        print(f"  Penulis     : {b.penulis}")
        print(f"  Kategori    : {b.kategori}")
        print(f"  Harga       : {b.harga}")
        print(f"  Rating      : {b.rating}")
    else:
        print(f"  Status      : TIDAK DITEMUKAN - buku '{hasil.kata_kunci}' tidak ada di dataset")
    print(f"  Perbandingan: {hasil.jumlah_perbandingan}\n")


# =====================================================================
# 7. PENGUJIAN: n = 100, 1.000, 10.000 x 4 skenario x 2 algoritma
# =====================================================================
def ukur(fungsi, data, kunci, ulang) -> HasilPencarian:
    hasil = fungsi(data, kunci)                 # hasil + jumlah perbandingan
    mulai = time.perf_counter_ns()
    for _ in range(ulang):
        fungsi(data, kunci)
    rata2_ns = (time.perf_counter_ns() - mulai) / ulang
    hasil.waktu_us = rata2_ns / 1000
    return hasil


def jalankan_pengujian(semua: List[Buku], ukuran=(100, 1000, 10000), ulang=200):
    baris_tabel = []
    for n in ukuran:
        if n > len(semua):
            print(f"(dilewati: n={n} > jumlah data {len(semua)})")
            continue
        subset = urutkan_data(semua[:n])        # data SAMA & terurut dipakai kedua algoritma
        skenario = {
            "Awal":   subset[0].judul,
            "Tengah": subset[(n - 1) // 2].judul,
            "Akhir":  subset[-1].judul,
            "Tidak ditemukan": "judul buku yang pasti tidak ada zzz",
        }
        for nama, kunci in skenario.items():
            for fungsi in (linear_search, binary_search):
                h = ukur(fungsi, subset, kunci, ulang)
                baris_tabel.append((n, h.algoritma, nama, h.jumlah_perbandingan, h.waktu_us))
    return baris_tabel


def cetak_tabel(baris_tabel) -> None:
    print(f"{'n':>7} | {'Algoritma':<14} | {'Skenario':<16} | {'Perbandingan':>12} | {'Waktu (us)':>11}")
    print("-" * 72)
    for n, alg, sk, p, w in baris_tabel:
        print(f"{n:>7} | {alg:<14} | {sk:<16} | {p:>12} | {w:>11.2f}")


def simpan_csv_dan_grafik(baris_tabel) -> None:
    with open("hasil_pengujian.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["n", "algoritma", "skenario", "perbandingan", "waktu_us"])
        w.writerows(baris_tabel)
    print("\nTabel disimpan ke hasil_pengujian.csv")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib belum terpasang, grafik dilewati (pip install matplotlib)")
        return
    ukuran = sorted({r[0] for r in baris_tabel})
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for alg in ("Linear Search", "Binary Search"):
        y_p = [next(r[3] for r in baris_tabel if r[0] == n and r[1] == alg and r[2] == "Tidak ditemukan") for n in ukuran]
        y_w = [next(r[4] for r in baris_tabel if r[0] == n and r[1] == alg and r[2] == "Tidak ditemukan") for n in ukuran]
        ax[0].plot(ukuran, y_p, marker="o", label=alg)
        ax[1].plot(ukuran, y_w, marker="o", label=alg)
    ax[0].set_title("Jumlah perbandingan (worst case)")
    ax[1].set_title("Waktu eksekusi (worst case)")
    ax[1].set_ylabel("mikrodetik")
    for a in ax:
        a.set_xlabel("n"); a.set_xscale("log"); a.set_yscale("log"); a.legend(); a.grid(True, alpha=.3)
    plt.tight_layout()
    plt.savefig("grafik_pengujian.png", dpi=150)
    print("Grafik disimpan ke grafik_pengujian.png")


# =====================================================================
# MAIN
# =====================================================================
if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data_buku.csv"
    semua = baca_dataset(path)
    print(f"Jumlah buku (judul unik) terbaca: {len(semua)}\n")

    data_terurut = urutkan_data(semua)
    contoh = data_terurut[len(data_terurut) // 3].judul

    print("=== Demo: data DITEMUKAN ===")
    tampilkan(linear_search(semua, contoh))
    tampilkan(binary_search(data_terurut, contoh))

    print("=== Demo: data TIDAK DITEMUKAN ===")
    tampilkan(linear_search(semua, "Buku Fiktif Tidak Ada 12345"))
    tampilkan(binary_search(data_terurut, "Buku Fiktif Tidak Ada 12345"))

    print("=== Hasil pengujian ===")
    tabel = jalankan_pengujian(semua)
    cetak_tabel(tabel)
    simpan_csv_dan_grafik(tabel)
