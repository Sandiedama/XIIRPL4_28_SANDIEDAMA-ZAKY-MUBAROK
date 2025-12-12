import sqlite3
import requests

API_URL = "https://multidayamitrasinergi.com/api/update_barang.php"
SECRET_KEY = "InventoryAppMMS"

# --- KONEKSI KE DATABASE LOKAL ---
# ⚠️ ganti path ini sesuai lokasi file .db lo
conn = sqlite3.connect(r"C:\Users\USER\Documents\inventoryapp\app\database\inventory.db")
cursor = conn.cursor()

# --- AMBIL DATA DARI TABEL ---
# pastiin tabel punya kolom: partnumber, nama, stok, satuan
cursor.execute("SELECT id, partnumber, nama, stok, satuan FROM barang")
rows = cursor.fetchall()

data = []
for row in rows:
    data.append({
        "id": row[0],           # tambah id
        "partnumber": row[1],
        "nama": row[2],
        "stok": row[3],
        "satuan": row[4]
    })
# --- KIRIM SEKALI KE SERVER ---
try:
    res = requests.post(API_URL, json=data, headers={
        "Authorization": f"Bearer {SECRET_KEY}"
    })
    print("Response:", res.text)
except Exception as e:
    print("Error:", e)

# Tutup koneksi DB
conn.close()
