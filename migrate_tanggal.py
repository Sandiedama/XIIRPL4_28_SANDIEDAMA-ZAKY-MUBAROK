

import sys
import os

# Tambahkan path aplikasi ke sys.path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

from app.database.db import migrate_tanggal_to_waktu

if __name__ == '__main__':
    print("=" * 60)
    print("MIGRASI TANGGAL KE WAKTU (OPSIONAL)")
    print("=" * 60)
    print()
    print("Script ini akan menambahkan waktu default (00:00:00) ke data lama.")
    print("Data yang sudah punya waktu tidak akan diubah.")
    print()
    
    response = input("Lanjutkan migrasi? (y/n): ").strip().lower()
    if response != 'y':
        print("Migrasi dibatalkan.")
        sys.exit(0)
    
    print()
    print("Memulai migrasi...")
    try:
        updated_in, updated_out = migrate_tanggal_to_waktu()
        print()
        print("=" * 60)
        print("MIGRASI SELESAI!")
        print("=" * 60)
        print(f"Transaksi IN yang diupdate: {updated_in}")
        print(f"Transaksi OUT yang diupdate: {updated_out}")
        print()
        print("Data lama sekarang sudah punya format tanggal + waktu.")
        print("Contoh: 2024-01-15 -> 2024-01-15 00:00:00")
    except Exception as e:
        print()
        print("=" * 60)
        print("ERROR!")
        print("=" * 60)
        print(f"Terjadi kesalahan: {e}")
        print("Pastikan database tidak sedang digunakan aplikasi lain.")
        sys.exit(1)

