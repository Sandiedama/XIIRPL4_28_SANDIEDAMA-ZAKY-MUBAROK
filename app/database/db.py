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
        barcode TEXT,
        rop INTEGER DEFAULT 0,
        satuan TEXT
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
        tanggal TEXT,
        remarks TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        nama TEXT,
        role TEXT DEFAULT "user"
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS log_aktivitas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        aksi TEXT,
        tabel TEXT,
        data_id INTEGER,
        waktu TEXT,
        keterangan TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    # Tambah kolom rop & satuan jika belum ada (migrasi dari versi lama)
    c.execute("PRAGMA table_info(barang)")
    columns = [row[1] for row in c.fetchall()]
    if 'rop' not in columns:
        c.execute('ALTER TABLE barang ADD COLUMN rop INTEGER DEFAULT 0')
    if 'satuan' not in columns:
        c.execute('ALTER TABLE barang ADD COLUMN satuan TEXT')

    # Tambah kolom remarks di transaksi_out jika belum ada (migrasi dari versi lama)
    c.execute("PRAGMA table_info(transaksi_out)")
    out_columns = [row[1] for row in c.fetchall()]
    if 'remarks' not in out_columns:
        c.execute('ALTER TABLE transaksi_out ADD COLUMN remarks TEXT')
    
    conn.commit()
    conn.close()

def migrate_tanggal_to_waktu():
    """
    Migrasi opsional: Menambahkan waktu default (00:00:00) ke data lama yang hanya punya tanggal.
    Ini OPSIONAL - sistem sudah bisa menangani kedua format (tanggal saja atau tanggal + waktu).
    """
    conn = get_connection()
    c = conn.cursor()
    updated_in = 0
    updated_out = 0
    
    # Update transaksi_in yang hanya punya tanggal (format YYYY-MM-DD, panjang 10 karakter)
    c.execute("SELECT id, tanggal FROM transaksi_in WHERE LENGTH(tanggal) = 10")
    rows_in = c.fetchall()
    for row_id, tanggal in rows_in:
        # Pastikan formatnya benar (YYYY-MM-DD)
        if len(tanggal) == 10 and tanggal.count('-') == 2:
            tanggal_baru = f"{tanggal} 00:00:00"
            c.execute("UPDATE transaksi_in SET tanggal = ? WHERE id = ?", (tanggal_baru, row_id))
            updated_in += 1
    
    # Update transaksi_out yang hanya punya tanggal (format YYYY-MM-DD, panjang 10 karakter)
    c.execute("SELECT id, tanggal FROM transaksi_out WHERE LENGTH(tanggal) = 10")
    rows_out = c.fetchall()
    for row_id, tanggal in rows_out:
        # Pastikan formatnya benar (YYYY-MM-DD)
        if len(tanggal) == 10 and tanggal.count('-') == 2:
            tanggal_baru = f"{tanggal} 00:00:00"
            c.execute("UPDATE transaksi_out SET tanggal = ? WHERE id = ?", (tanggal_baru, row_id))
            updated_out += 1
    
    conn.commit()
    conn.close()
    
    return updated_in, updated_out

def get_low_stock_items():
    """Mendapatkan barang dengan stok <= ROP"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT partnumber, nama, stok, rop 
        FROM barang 
        WHERE stok <= rop AND rop > 0
        ORDER BY (rop - stok) DESC
    ''')
    items = c.fetchall()
    conn.close()
    return items

def reset_database():
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM transaksi_in')
    c.execute('DELETE FROM transaksi_out')
    # Tambah tabel lain jika ada
    c.execute('DELETE FROM users')
    c.execute('DELETE FROM log_aktivitas')
    # Tambah kolom role jika belum ada
    c.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in c.fetchall()]
    if 'role' not in columns:
        c.execute('ALTER TABLE users ADD COLUMN role TEXT DEFAULT "user"')
    # Tambah user admin default jika belum ada user
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO users (username, password, nama, role) VALUES (?, ?, ?, ?)', ('admin', 'admin', 'Administrator', 'admin'))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    print('Resetting all database data...')
    reset_database()
    print('Database reset complete!') 