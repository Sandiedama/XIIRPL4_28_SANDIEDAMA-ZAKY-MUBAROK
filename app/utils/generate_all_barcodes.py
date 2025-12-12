#!/usr/bin/env python3
"""
Script untuk generate barcode otomatis untuk semua barang yang sudah ada
"""

from database.db import get_connection
from utils.barcode_generator import BarcodeGenerator, update_barcode_in_database
from utils.helpers import resource_path, output_assets_path
import os
from typing import Callable, Optional

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

def generate_all_barcodes(progress_callback: Optional[Callable[[int, int], None]] = None):
    """
    Generate barcode untuk semua barang yang belum memiliki barcode
    progress_callback: fungsi dengan argumen (current, total) untuk update progress bar (misal di GUI)
    """
    print("🚀 Memulai generate barcode otomatis...")
    
    # Buat direktori barcode jika belum ada
    barcode_dir = output_assets_path('barcodes')
    if not os.path.exists(barcode_dir):
        os.makedirs(barcode_dir)
        print(f"📁 Direktori barcode dibuat: {barcode_dir}")
    
    # Ambil semua barang dari database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT partnumber, nama, barcode FROM barang')
    barang_list = cursor.fetchall()
    conn.close()
    
    if not barang_list:
        print("❌ Tidak ada data barang di database")
        return
    
    print(f"📦 Ditemukan {len(barang_list)} barang di database")
    
    # Generate barcode untuk setiap barang
    barcode_gen = BarcodeGenerator()
    success_count = 0
    failed_count = 0
    
    total = len(barang_list)
    iterator = barang_list
    if progress_callback is None and tqdm is not None:
        iterator = tqdm(barang_list, desc="Generate Barcode", unit="barang")
    current = 0
    for partnumber, nama, existing_barcode in iterator:
        if not partnumber:
            continue
            
        # Skip jika sudah ada barcode
        if existing_barcode and os.path.exists(existing_barcode):
            print(f"⏭️  {partnumber} - {nama} (barcode sudah ada)")
            continue
        
        try:
            print(f"🔄 Generating barcode untuk: {partnumber} - {nama}")
            
            # Generate barcode
            barcode_path = barcode_gen.auto_generate_barcode(partnumber)
            
            if barcode_path:
                # Update database
                if update_barcode_in_database(partnumber, barcode_path):
                    print(f"✅ Berhasil: {partnumber} -> {barcode_path}")
                    success_count += 1
                else:
                    print(f"❌ Gagal update database: {partnumber}")
                    failed_count += 1
            else:
                print(f"❌ Gagal generate barcode: {partnumber}")
                failed_count += 1
                
        except Exception as e:
            print(f"❌ Error untuk {partnumber}: {e}")
            failed_count += 1
        current += 1
        if progress_callback:
            progress_callback(current, total)
    
    print(f"\n📊 Hasil Generate Barcode:")
    print(f"✅ Berhasil: {success_count}")
    print(f"❌ Gagal: {failed_count}")
    print(f"📁 File barcode disimpan di: {barcode_dir}")

def generate_barcode_for_partnumber(partnumber, progress_callback: Optional[Callable[[int, int], None]] = None):
    """
    Generate barcode untuk partnumber tertentu
    progress_callback: fungsi dengan argumen (current, total) untuk update progress bar (misal di GUI)
    """
    if not partnumber:
        print("❌ Part number tidak boleh kosong")
        return False
    
    try:
        print(f"🔄 Generating barcode untuk: {partnumber}")
        
        barcode_gen = BarcodeGenerator()
        barcode_path = barcode_gen.auto_generate_barcode(partnumber)
        
        if barcode_path:
            if update_barcode_in_database(partnumber, barcode_path):
                print(f"✅ Berhasil generate barcode: {barcode_path}")
                if progress_callback:
                    progress_callback(1, 1)
                return True
            else:
                print(f"❌ Gagal update database")
                if progress_callback:
                    progress_callback(1, 1)
                return False
        else:
            print(f"❌ Gagal generate barcode")
            if progress_callback:
                progress_callback(1, 1)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        if progress_callback:
            progress_callback(1, 1)
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Generate untuk partnumber tertentu
        partnumber = sys.argv[1]
        generate_barcode_for_partnumber(partnumber)
    else:
        # Generate untuk semua barang
        generate_all_barcodes() 