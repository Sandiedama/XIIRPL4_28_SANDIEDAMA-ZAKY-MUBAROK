from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout, QDialog, QLineEdit, QComboBox, QMessageBox, QDialogButtonBox
from database.db import get_connection
from PyQt6.QtCore import Qt

class ManajemenUserScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QLabel('Manajemen User')
        header.setStyleSheet('font-size:32px; color:#FF2800; font-weight:bold; margin-bottom:12px;')
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(header)
        # Tombol tambah
        btn_row = QHBoxLayout()
        self.btn_tambah = QPushButton('Tambah User')
        self.btn_tambah.setStyleSheet('background:#FF2800; color:#FFF; font-size:16px; padding:8px 24px; border-radius:8px;')
        self.btn_tambah.clicked.connect(self.tambah_user)
        btn_row.addWidget(self.btn_tambah)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        # Tabel user
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', 'Username', 'Nama', 'Role'])
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header_view.setFixedHeight(44)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        # Tombol edit/hapus
        crud_row = QHBoxLayout()
        self.btn_edit = QPushButton('Edit User')
        self.btn_edit.setStyleSheet('background:#17A2B8; color:#FFF; font-size:16px; padding:8px 24px; border-radius:8px;')
        self.btn_edit.clicked.connect(self.edit_user)
        crud_row.addWidget(self.btn_edit)
        self.btn_hapus = QPushButton('Hapus User')
        self.btn_hapus.setStyleSheet('background:#DC3545; color:#FFF; font-size:16px; padding:8px 24px; border-radius:8px;')
        self.btn_hapus.clicked.connect(self.hapus_user)
        crud_row.addWidget(self.btn_hapus)
        crud_row.addStretch()
        layout.addLayout(crud_row)
        self.setLayout(layout)
        self.setStyleSheet('background:#FFF; font-family: Segoe UI, Arial, sans-serif;')

    def load_data(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT id, username, nama, role FROM users ORDER BY id')
        rows = c.fetchall()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val) if val is not None else ''))
        conn.close()

    def tambah_user(self):
        dialog = UserDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute('INSERT INTO users (username, password, nama, role) VALUES (?, ?, ?, ?)',
                          (data['username'], data['password'], data['nama'], data['role']))
                conn.commit()
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Gagal tambah user: {e}')
            conn.close()
            self.load_data()

    def edit_user(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Pilih User', 'Pilih user yang akan diedit!')
            return
        user_id = int(self.table.item(selected, 0).text())
        username = self.table.item(selected, 1).text()
        nama = self.table.item(selected, 2).text()
        role = self.table.item(selected, 3).text()
        dialog = UserDialog(self, {'id': user_id, 'username': username, 'nama': nama, 'role': role})
        if dialog.exec():
            data = dialog.get_data()
            conn = get_connection()
            c = conn.cursor()
            try:
                if data['password']:
                    c.execute('UPDATE users SET nama=?, password=?, role=? WHERE id=?',
                              (data['nama'], data['password'], data['role'], user_id))
                else:
                    c.execute('UPDATE users SET nama=?, role=? WHERE id=?',
                              (data['nama'], data['role'], user_id))
                conn.commit()
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Gagal edit user: {e}')
            conn.close()
            self.load_data()

    def hapus_user(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Pilih User', 'Pilih user yang akan dihapus!')
            return
        user_id = int(self.table.item(selected, 0).text())
        username = self.table.item(selected, 1).text()
        if username == 'admin':
            QMessageBox.warning(self, 'Error', 'User admin utama tidak boleh dihapus!')
            return
        reply = QMessageBox.question(self, 'Konfirmasi', f'Yakin hapus user {username}?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute('DELETE FROM users WHERE id=?', (user_id,))
                conn.commit()
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Gagal hapus user: {e}')
            conn.close()
            self.load_data()

class UserDialog(QDialog):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.setWindowTitle('User')
        self.setModal(True)
        self.setMinimumWidth(340)
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        self.nama_input = QLineEdit()
        self.nama_input.setPlaceholderText('Nama Lengkap')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password (isi jika ingin ganti)')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.role_combo = QComboBox()
        self.role_combo.addItems(['user', 'admin'])
        layout.addWidget(QLabel('Username:'))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel('Nama Lengkap:'))
        layout.addWidget(self.nama_input)
        layout.addWidget(QLabel('Password:'))
        layout.addWidget(self.password_input)
        layout.addWidget(QLabel('Role:'))
        layout.addWidget(self.role_combo)
        # Tombol Simpan/Batal
        self.button_box = QDialogButtonBox()
        if user:
            self.save_btn = self.button_box.addButton('Simpan', QDialogButtonBox.ButtonRole.AcceptRole)
            self.save_btn.setStyleSheet('background:#17A2B8; color:#FFF; font-size:16px; padding:8px 24px; border-radius:8px;')
        else:
            self.save_btn = self.button_box.addButton('Tambah', QDialogButtonBox.ButtonRole.AcceptRole)
            self.save_btn.setStyleSheet('background:#FF2800; color:#FFF; font-size:16px; padding:8px 24px; border-radius:8px;')
        self.cancel_btn = self.button_box.addButton('Batal', QDialogButtonBox.ButtonRole.RejectRole)
        self.cancel_btn.setStyleSheet('background:#AAA; color:#FFF; font-size:16px; padding:8px 24px; border-radius:8px;')
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addSpacing(8)
        layout.addWidget(self.button_box)
        self.setLayout(layout)
        self.user = user
        if user:
            self.username_input.setText(user['username'])
            self.username_input.setReadOnly(True)
            self.nama_input.setText(user['nama'])
            self.role_combo.setCurrentText(user['role'])

    def validate_and_accept(self):
        if not self.username_input.text().strip():
            QMessageBox.warning(self, 'Validasi', 'Username wajib diisi!')
            return
        if not self.nama_input.text().strip():
            QMessageBox.warning(self, 'Validasi', 'Nama wajib diisi!')
            return
        if not self.user and not self.password_input.text().strip():
            QMessageBox.warning(self, 'Validasi', 'Password wajib diisi!')
            return
        self.accept()

    def get_data(self):
        return {
            'username': self.username_input.text().strip(),
            'nama': self.nama_input.text().strip(),
            'password': self.password_input.text().strip(),
            'role': self.role_combo.currentText()
        } 