import sys, os
import sqlite3
from datetime import datetime
import re
from database.db import get_db_path

def resource_path(relative_path):
    """
    Dapatkan path absolut ke resource, kompatibel dengan PyInstaller (_MEIPASS) dan mode development.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', relative_path)

def output_assets_path(*subpaths):
    """
    Dapatkan path absolut ke folder output (assets/barcodes),
    kompatibel dengan PyInstaller (hasil build) dan mode development.
    """
    if hasattr(sys, '_MEIPASS'):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(base, 'assets', *subpaths)

# Session user aktif (global sederhana)
current_user = None
current_log_file_path = None

def _logs_base_path():
    """
    Tentukan folder logs di samping aplikasi (kompatibel dev & PyInstaller).
    """
    if hasattr(sys, '_MEIPASS'):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    logs_dir = os.path.join(base, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir

def _sanitize_filename(name):
    return re.sub(r'[\\/:*?"<>|]+', '_', str(name))

def _start_user_file_log(user_dict):
    """
    Mulai file log per sesi login, nama file mengandung username dan timestamp.
    Simpan path ke global agar bisa dipakai oleh write_user_log / log_aktivitas.
    """
    global current_log_file_path
    username = (user_dict or {}).get('username') or 'user'
    safe_username = _sanitize_filename(username)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{safe_username}_{ts}.log"
    current_log_file_path = os.path.join(_logs_base_path(), filename)
    try:
        with open(current_log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat(sep=' ', timespec='seconds')}] LOGIN username={username}\n")
    except Exception:
        # Jangan blokir aplikasi bila gagal menulis log file
        current_log_file_path = None

def write_user_log(message):
    """
    Tulis baris log bebas ke file log user aktif (jika tersedia).
    """
    global current_log_file_path
    if not current_log_file_path:
        return
    try:
        with open(current_log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat(sep=' ', timespec='seconds')}] {message}\n")
    except Exception:
        pass

def set_current_user(user):
    global current_user
    current_user = user
    # Mulai file log per user login
    try:
        _start_user_file_log(user)
    except Exception:
        pass

def get_current_user():
    global current_user
    return current_user

def is_admin():
    """Cek apakah user saat ini adalah admin"""
    user = get_current_user()
    return user and user.get('role') == 'admin'

def is_user():
    """Cek apakah user saat ini adalah user biasa"""
    user = get_current_user()
    return user and user.get('role') == 'user'

def require_admin(func):
    """Decorator untuk memerlukan hak akses admin"""
    def wrapper(*args, **kwargs):
        if not is_admin():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(None, 'Akses Ditolak', 'Anda tidak memiliki hak akses untuk fitur ini. Hanya admin yang dapat mengakses.')
            return
        return func(*args, **kwargs)
    return wrapper

def log_aktivitas(user_id, aksi, tabel, data_id=None, keterangan=None, conn=None, cursor=None):
    """
    Fungsi pencatatan log aktivitas user ke tabel log_aktivitas.
    Fleksibel: bisa pakai koneksi dari luar (conn, cursor) atau buka sendiri.
    """
    waktu = datetime.now().isoformat(sep=' ', timespec='seconds')
    close_after = False

    if conn is None or cursor is None:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        close_after = True

    cursor.execute('''INSERT INTO log_aktivitas (user_id, aksi, tabel, data_id, waktu, keterangan)
                      VALUES (?, ?, ?, ?, ?, ?)''',
                   (user_id, aksi, tabel, data_id, waktu, keterangan))

    # Tulis juga ke file log per-user jika ada
    try:
        username = (current_user or {}).get('username')
        write_user_log(f"aksi={aksi} tabel={tabel} data_id={data_id} user_id={user_id} username={username} ket={keterangan}")
    except Exception:
        pass

    if close_after:
        conn.commit()
        conn.close()
