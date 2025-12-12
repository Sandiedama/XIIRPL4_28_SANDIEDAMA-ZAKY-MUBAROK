from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QHBoxLayout, QMessageBox, QSpinBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from datetime import datetime
import re
import sqlite3
import os
from utils.helpers import get_current_user, log_aktivitas
from utils.export_pdf import export_in_pdf
from utils.theme import theme

class MenuInScreen(QWidget):
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
        header = QLabel('Barang Masuk (Menu IN)')
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

        form_layout.addWidget(QLabel("Kategori:"))
        self.kategori_input = QComboBox()
        self.kategori_input.addItems(["Project", "Retail", "Warranty", "Stock"])
        # Input styling will be applied in apply_theme method
        form_layout.addWidget(self.kategori_input)

        form_layout.addWidget(QLabel("Qty:"))
        self.qty_input = QSpinBox()
        self.qty_input.setRange(1, 100000)
        # Input styling will be applied in apply_theme method
        form_layout.addWidget(self.qty_input)

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
        self.table.setHorizontalHeaderLabels(["Part Number", "Nama", "Kategori", "Qty"])
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
        bawah_card = QWidget()
        self.bawah_card = bawah_card
        bawah = QHBoxLayout(bawah_card)
        bawah.setSpacing(12)
        bawah.addWidget(QLabel("Penerima:"))
        self.penerima_input = QLineEdit()
        # Input styling will be applied in apply_theme method
        bawah.addWidget(self.penerima_input)

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
            print(f"Error loading barang data: {e}")
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
        
        # Check if the items exist before accessing them
        part_item = self.search_table.item(row, 0)
        nama_item = self.search_table.item(row, 1)
        
        if part_item is not None and nama_item is not None:
            # Store the text values immediately to avoid deletion issues
            part_text = part_item.text()
            nama_text = nama_item.text()
            
            # Clear the table first to avoid any race conditions
            self.search_table.setRowCount(0)
            
            # Set the input fields with the stored text
            self.part_number_input.setText(part_text)
            self.nama_barang_input.setText(nama_text)
        else:
            print(f"Warning: Table items not found at row {row}")

    def add_item(self):
        part = self.part_number_input.text().strip()
        nama = self.nama_barang_input.text().strip()
        kategori = self.kategori_input.currentText()
        qty = self.qty_input.value()

        if not part or not nama:
            QMessageBox.warning(self, "Peringatan", "Part number dan nama wajib diisi.")
            return

        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(part))
        self.table.setItem(row, 1, QTableWidgetItem(nama))
        self.table.setItem(row, 2, QTableWidgetItem(kategori))
        self.table.setItem(row, 3, QTableWidgetItem(str(qty)))

        self.part_number_input.clear()
        self.nama_barang_input.clear()
        self.qty_input.setValue(1)

    def hapus_baris(self):
        selected = self.table.currentRow()
        if selected >= 0:
            self.table.removeRow(selected)

    def export_pdf_and_save(self):
        penerima = self.penerima_input.text().strip()
        # Simpan tanggal dengan waktu (tanggal + jam saat ini)
        tanggal_date = self.tanggal_input.date().toPyDate()
        waktu_sekarang = datetime.now().strftime("%H:%M:%S")
        tanggal = f"{tanggal_date.strftime('%Y-%m-%d')} {waktu_sekarang}"

        if not penerima:
            QMessageBox.warning(self, "Peringatan", "Kolom penerima wajib diisi.")
            return
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Peringatan", "Data kosong.")
            return

        try:
            user = get_current_user()
            user_id = None

            if isinstance(user, dict):
                user_id = user.get('id')
            else:
                with sqlite3.connect(self.db_path) as conn_user:
                    cur_user = conn_user.cursor()
                    cur_user.execute("SELECT id FROM users WHERE username = ?", (user,))
                    row_user = cur_user.fetchone()
                    if row_user:
                        user_id = row_user[0]

            if not isinstance(user_id, int):
                raise Exception("User aktif tidak valid. Silakan login ulang.")

            data_export = []

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                for row in range(self.table.rowCount()):
                    part = self.table.item(row, 0).text()
                    nama = self.table.item(row, 1).text()
                    kategori = self.table.item(row, 2).text()
                    qty = int(self.table.item(row, 3).text())

                    cursor.execute("SELECT stok FROM barang WHERE partnumber = ?", (part,))
                    result = cursor.fetchone()
                    if result:
                        stok_baru = result[0] + qty
                        cursor.execute("UPDATE barang SET stok = ? WHERE partnumber = ?", (stok_baru, part))
                        conn.commit()
                    else:
                        raise Exception(f"Barang dengan part number {part} tidak ditemukan.")

                    cursor.execute('''
                        INSERT INTO transaksi_in (partnumber, nama, kategori, qty, penerima, tanggal)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (part, nama, kategori, qty, penerima, tanggal))

                    data_id = cursor.lastrowid
                    keterangan = f"{nama} ({part}), qty: {qty}"
                    log_aktivitas(user_id, "Barang Masuk", "transaksi_in", data_id, keterangan, conn, cursor)

                    data_export.append({
                        'partnumber': part,
                        'nama': nama,
                        'kategori': kategori,
                        'qty': qty,
                        'penerima': penerima,
                    })

            # Simpan ke folder Desktop user saat ini (tidak hardcode USER)
            user_desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            target_dir = os.path.join(user_desktop, "Report IN OUT Barang")
            os.makedirs(target_dir, exist_ok=True)
            # Sertakan nama penerima yang sudah disanitasi di nama file
            safe_penerima = re.sub(r'[\\/:*?"<>|]+', '_', penerima) if penerima else 'Penerima'
            pdf_filename = os.path.join(target_dir, f'BarangMasuk_{safe_penerima}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
            export_in_pdf(pdf_filename, data_export, tanggal)

            QMessageBox.information(self, "Sukses", f"Data disimpan dan PDF dibuat:\n{pdf_filename}")
            self.table.setRowCount(0)
            self.penerima_input.clear()
            try:
                self.data_changed.emit()
            except Exception:
                pass

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan data: {e}")
    
    def apply_theme(self):
        """Apply current theme to menu IN screen"""
        # Header styling
        self.header.setStyleSheet(f'font-size:32px; color:{theme.get_color("accent")}; font-weight:bold; margin-bottom:12px;')
        
        # Card styling
        self.form_card.setStyleSheet(theme.get_card_style())
        self.bawah_card.setStyleSheet(theme.get_card_style())
        
        # Input styling
        input_style = theme.get_input_style()
        self.part_number_input.setStyleSheet(input_style)
        self.nama_barang_input.setStyleSheet(input_style)
        self.kategori_input.setStyleSheet(input_style)
        self.qty_input.setStyleSheet(input_style)
        self.penerima_input.setStyleSheet(input_style)
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
