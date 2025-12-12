import sqlite3
import os

def get_db_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'inventory.db')
    return db_path

def get_connection():
    return sqlite3.connect(get_db_path())

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS barang (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        partnumber TEXT,
        nama TEXT,
        kategori TEXT,
        stok INTEGER,
        barcode TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS transaksi_in (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        partnumber TEXT,
        nama TEXT,
        kategori TEXT,
        qty INTEGER,
        penerima TEXT,
        tanggal TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS transaksi_out (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        partnumber TEXT,
        nama TEXT,
        kategori TEXT,
        qty INTEGER,
        pengeluar TEXT,
        penerima TEXT,
        approver TEXT,
        tanggal TEXT
    )''')
    conn.commit()
    conn.close()

def reset_database():
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM transaksi_in')
    c.execute('DELETE FROM transaksi_out')
    # Tambah tabel lain jika ada
    conn.commit()
    conn.close()

if __name__ == '__main__':
    print('Resetting all database data...')
    reset_database()
    print('Database reset complete!') 