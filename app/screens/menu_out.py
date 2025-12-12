from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout,
    QMessageBox, QSpinBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from datetime import datetime
import re
import sqlite3
import os
from utils.helpers import get_current_user, log_aktivitas
from utils.export_pdf import export_out_pdf
from utils.theme import theme

class MenuOutScreen(QWidget):
    data_changed = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'inventory.db')
        self.init_ui()
        self.load_barang_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header modern
        header = QLabel('Barang Keluar (Menu OUT)')
        self.header = header
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(header)

        # Form input dalam card
        form_card = QWidget()
        self.form_card = form_card
        form_layout = QHBoxLayout(form_card)
        form_layout.setSpacing(12)

        form_layout.addWidget(QLabel("Part:"))
        self.part_number_input = QLineEdit()
        self.part_number_input.setPlaceholderText("Part Number")
        # Input styling will be applied in apply_theme method
        self.part_number_input.textChanged.connect(self.search_barang)
        form_layout.addWidget(self.part_number_input)

        form_layout.addWidget(QLabel("Nama:"))
        self.nama_barang_input = QLineEdit()
        self.nama_barang_input.setPlaceholderText("Nama Barang")
        # Input styling will be applied in apply_theme method
        self.nama_barang_input.textChanged.connect(self.search_barang)
        form_layout.addWidget(self.nama_barang_input)

        form_layout.addWidget(QLabel("Qty:"))
        self.qty_input = QSpinBox()
        self.qty_input.setRange(1, 100000)
        # Input styling will be applied in apply_theme method
        form_layout.addWidget(self.qty_input)

        form_layout.addWidget(QLabel("Remarks:"))
        self.remarks_input = QLineEdit()
        self.remarks_input.setPlaceholderText("Keterangan")
        # Input styling will be applied in apply_theme method
        form_layout.addWidget(self.remarks_input)

        self.add_button = QPushButton("Tambah")
        # Button styling will be applied in apply_theme method
        self.add_button.clicked.connect(self.add_item)
        form_layout.addWidget(self.add_button)

        layout.addWidget(form_card)

        self.search_table = QTableWidget()
        self.search_table.setColumnCount(2)
        self.search_table.setHorizontalHeaderLabels(["Part Number", "Nama Barang"])
        self.search_table.setMaximumHeight(150)
        # Table styling will be applied in apply_theme method
        self.search_table.verticalHeader().setVisible(False)
        self.search_table.itemClicked.connect(self.select_barang)
        
        # Set column widths to 50% each
        search_header = self.search_table.horizontalHeader()
        search_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        search_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.search_table)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Part Number", "Nama", "Qty", "Remarks"])
        # Table styling will be applied in apply_theme method
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        hapus_row = QHBoxLayout()
        self.hapus_btn = QPushButton('Hapus Baris Terpilih')
        # Button styling will be applied in apply_theme method
        self.hapus_btn.clicked.connect(self.hapus_baris)
        hapus_row.addWidget(self.hapus_btn)
        hapus_row.addStretch()
        layout.addLayout(hapus_row)

        # Form bawah dalam card
        form_bawah_card = QWidget()
        self.form_bawah_card = form_bawah_card
        form_bawah = QHBoxLayout(form_bawah_card)
        form_bawah.setSpacing(12)
        form_bawah.addWidget(QLabel("Pengeluar:"))
        self.pengeluar_input = QLineEdit()
        # Input styling will be applied in apply_theme method
        form_bawah.addWidget(self.pengeluar_input)

        form_bawah.addWidget(QLabel("Penerima:"))
        self.penerima_input = QLineEdit()
        # Input styling will be applied in apply_theme method
        form_bawah.addWidget(self.penerima_input)

        form_bawah.addWidget(QLabel("Approver:"))
        self.approver_input = QLineEdit()
        # Input styling will be applied in apply_theme method
        form_bawah.addWidget(self.approver_input)

        layout.addWidget(form_bawah_card)

        # Form kategori dan tanggal dalam card
        bawah_card = QWidget()
        self.bawah_card = bawah_card
        bawah = QHBoxLayout(bawah_card)
        bawah.setSpacing(12)
        bawah.addWidget(QLabel("Kategori:"))
        self.kategori_input = QComboBox()
        self.kategori_input.addItems(["Project", "Retail", "Warranty", "Stock"])
        # Input styling will be applied in apply_theme method
        bawah.addWidget(self.kategori_input)

        bawah.addWidget(QLabel("Tanggal:"))
        self.tanggal_input = QDateEdit()
        self.tanggal_input.setCalendarPopup(True)
        # Input styling will be applied in apply_theme method
        self.tanggal_input.setDate(QDate.currentDate())
        bawah.addWidget(self.tanggal_input)

        layout.addWidget(bawah_card)

        self.save_export_btn = QPushButton("Simpan & Export PDF")
        # Button styling will be applied in apply_theme method
        self.save_export_btn.clicked.connect(self.export_pdf_and_save)
        layout.addWidget(self.save_export_btn)

        # Apply theme
        self.apply_theme()

    def load_barang_data(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT partnumber, nama FROM barang ORDER BY nama")
                self.barang_data = cursor.fetchall()
        except Exception as e:
            print(f"Error load barang: {e}")
            self.barang_data = []

    def search_barang(self, text):
        # Refresh data setiap kali user mengetik, agar tidak perlu relogin
        self.load_barang_data()
        text = text.strip().lower()
        if not text:
            self.search_table.setRowCount(0)
            return
        filtered = [(pn, nama) for pn, nama in self.barang_data if text in nama.lower() or text in pn.lower()]
        self.search_table.setRowCount(len(filtered))
        for row, (pn, nama) in enumerate(filtered):
            self.search_table.setItem(row, 0, QTableWidgetItem(pn))
            self.search_table.setItem(row, 1, QTableWidgetItem(nama))

    def select_barang(self, item):
        row = item.row()
        # Ambil item dan validasi tidak None
        part_item = self.search_table.item(row, 0)
        nama_item = self.search_table.item(row, 1)
        if part_item is not None and nama_item is not None:
            # Simpan teks lebih dulu sebelum tabel diubah (hindari objek terhapus)
            part_text = part_item.text()
            nama_text = nama_item.text()
            # Bersihkan tabel suggestions
            self.search_table.setRowCount(0)
            # Set field input
            self.part_number_input.setText(part_text)
            self.nama_barang_input.setText(nama_text)
        else:
            print(f"Warning: Table items not found at row {row}")

    def add_item(self):
        part = self.part_number_input.text().strip()
        nama = self.nama_barang_input.text().strip()
        qty = self.qty_input.value()
        remarks = self.remarks_input.text().strip()

        if not part or not nama:
            QMessageBox.warning(self, "Peringatan", "Part number dan nama wajib diisi.")
            return

        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(part))
        self.table.setItem(row, 1, QTableWidgetItem(nama))
        self.table.setItem(row, 2, QTableWidgetItem(str(qty)))
        self.table.setItem(row, 3, QTableWidgetItem(remarks))

        self.part_number_input.clear()
        self.nama_barang_input.clear()
        self.qty_input.setValue(1)
        self.remarks_input.clear()

    def hapus_baris(self):
        selected = self.table.currentRow()
        if selected >= 0:
            self.table.removeRow(selected)

    def export_pdf_and_save(self):
        pengeluar = self.pengeluar_input.text().strip()
        penerima = self.penerima_input.text().strip()
        approver = self.approver_input.text().strip()
        kategori = self.kategori_input.currentText()
        # Simpan tanggal dengan waktu (tanggal + jam saat ini)
        tanggal_date = self.tanggal_input.date().toPyDate()
        waktu_sekarang = datetime.now().strftime("%H:%M:%S")
        tanggal = f"{tanggal_date.strftime('%Y-%m-%d')} {waktu_sekarang}"
        if not pengeluar or not penerima or not approver:
            QMessageBox.warning(self, "Peringatan", "Semua field bawah wajib diisi.")
            return
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Peringatan", "Data kosong.")
            return

        # Kumpulkan data dari tabel dan validasi tipe terlebih dahulu
        rows_to_process = []
        for row in range(self.table.rowCount()):
            part_item = self.table.item(row, 0)
            nama_item = self.table.item(row, 1)
            qty_item = self.table.item(row, 2)
            remarks_item = self.table.item(row, 3)
            part = (part_item.text() if part_item else '').strip()
            nama = (nama_item.text() if nama_item else '').strip()
            remarks = (remarks_item.text() if remarks_item else '').strip()
            try:
                qty = int((qty_item.text() if qty_item else '0').strip())
            except Exception:
                QMessageBox.warning(self, "Peringatan", f"Qty tidak valid untuk: {nama or part}")
                return
            if not part or not nama or qty <= 0:
                QMessageBox.warning(self, "Peringatan", f"Baris tidak valid pada baris {row+1}")
                return
            rows_to_process.append((part, nama, qty, remarks))

        try:
            user = get_current_user()
            user_id = user['id'] if isinstance(user, dict) and 'id' in user else user

            data_export = []

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('BEGIN')

                # Fase validasi stok untuk semua baris
                insufficient = []
                missing = []
                current_stok_map = {}
                for part, nama, qty, _ in rows_to_process:
                    cursor.execute("SELECT stok FROM barang WHERE partnumber = ?", (part,))
                    result = cursor.fetchone()
                    if not result:
                        missing.append(f"{nama} ({part}) tidak ditemukan")
                        continue
                    try:
                        stok_val = int(result[0] if result[0] is not None else 0)
                    except Exception:
                        stok_val = 0
                    current_stok_map[part] = stok_val
                    if qty > stok_val:
                        insufficient.append(f"{nama} ({part}) stok {stok_val}, perlu {qty}")

                if missing or insufficient:
                    conn.rollback()
                    msg_parts = []
                    if missing:
                        msg_parts.append("Data tidak ditemukan:\n- " + "\n- ".join(missing))
                    if insufficient:
                        msg_parts.append("Stok tidak mencukupi:\n- " + "\n- ".join(insufficient))
                    QMessageBox.warning(self, "Validasi Gagal", "\n\n".join(msg_parts))
                    return

                # Semua valid: lakukan update dan insert
                for part, nama, qty, remarks in rows_to_process:
                    new_stok = current_stok_map[part] - qty
                    cursor.execute("UPDATE barang SET stok = ? WHERE partnumber = ?", (new_stok, part))
                    cursor.execute('''
                        INSERT INTO transaksi_out (partnumber, nama, qty, kategori, pengeluar, penerima, approver, remarks, tanggal)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (part, nama, qty, kategori, pengeluar, penerima, approver, remarks, tanggal))

                    data_id = cursor.lastrowid
                    keterangan = f"{nama} ({part}), qty: {qty}"
                    log_aktivitas(user_id, "Barang Keluar", "transaksi_out", data_id, keterangan, conn, cursor)

                    data_export.append({
                        'partnumber': part,
                        'nama': nama,
                        'qty': qty,
                        'kategori': kategori,
                        'pengeluar': pengeluar,
                        'penerima': penerima,
                        'approver': approver,
                        'remarks': remarks,
                        'tanggal': tanggal
                    })

                conn.commit()

            # Simpan ke folder Desktop user saat ini (tidak hardcode USER)
            user_desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            target_dir = os.path.join(user_desktop, "Report IN OUT Barang")
            os.makedirs(target_dir, exist_ok=True)
            safe_penerima = re.sub(r'[\\/:*?"<>|]+', '_', penerima) if penerima else 'Penerima'
            remark_for_name = next((r for _, _, _, r in rows_to_process if r), '')
            pdf_file = os.path.join(target_dir, f'BarangKeluar_{safe_penerima}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
            export_out_pdf(pdf_file, data_export, tanggal)

            QMessageBox.information(self, "Sukses", f"Data disimpan & PDF dibuat:\n{pdf_file}")
            self.table.setRowCount(0)
            self.pengeluar_input.clear()
            self.penerima_input.clear()
            self.approver_input.clear()
            try:
                self.data_changed.emit()
            except Exception:
                pass

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan data: {e}")
    
    def apply_theme(self):
        """Apply current theme to menu OUT screen"""
        # Header styling
        self.header.setStyleSheet(f'font-size:32px; color:{theme.get_color("accent")}; font-weight:bold; margin-bottom:12px;')
        
        # Card styling
        self.form_card.setStyleSheet(theme.get_card_style())
        self.form_bawah_card.setStyleSheet(theme.get_card_style())
        self.bawah_card.setStyleSheet(theme.get_card_style())
        
        # Input styling
        input_style = theme.get_input_style()
        self.part_number_input.setStyleSheet(input_style)
        self.nama_barang_input.setStyleSheet(input_style)
        self.qty_input.setStyleSheet(input_style)
        self.remarks_input.setStyleSheet(input_style)
        self.pengeluar_input.setStyleSheet(input_style)
        self.penerima_input.setStyleSheet(input_style)
        self.approver_input.setStyleSheet(input_style)
        self.kategori_input.setStyleSheet(input_style)
        self.tanggal_input.setStyleSheet(input_style)
        
        # Button styling
        self.add_button.setStyleSheet(theme.get_button_style('primary'))
        self.hapus_btn.setStyleSheet(theme.get_button_style('primary'))
        self.save_export_btn.setStyleSheet(theme.get_button_style('primary'))
        
        # Table styling
        table_style = theme.get_table_style()
        self.search_table.setStyleSheet(table_style)
        self.table.setStyleSheet(table_style)
        
        # Main background
        self.setStyleSheet(f'background: {theme.get_color("background")}; font-family: Segoe UI, Arial, sans-serif;')
