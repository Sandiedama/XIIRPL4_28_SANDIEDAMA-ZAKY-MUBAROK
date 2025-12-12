from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout, QComboBox, QDateEdit, QMessageBox
from database.db import get_connection
from utils.export_pdf import export_custom_pdf
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import QFileDialog

class ReportCustomScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 0, 24, 12)
        layout.setSpacing(8)

        header = QLabel('Report Custom')
        header.setStyleSheet('font-size:32px; color:#FF2800; font-weight:bold; margin-bottom:0;')
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(header)

        # Filter row
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)

        filter_row.addWidget(QLabel('Dari:'))
        self.tgl_awal = QDateEdit()
        self.tgl_awal.setDisplayFormat('yyyy-MM-dd')
        self.tgl_awal.setDate(QDate.currentDate().addMonths(-1))
        self.tgl_awal.setCalendarPopup(True)
        filter_row.addWidget(self.tgl_awal)

        filter_row.addWidget(QLabel('Sampai:'))
        self.tgl_akhir = QDateEdit()
        self.tgl_akhir.setDisplayFormat('yyyy-MM-dd')
        self.tgl_akhir.setDate(QDate.currentDate())
        self.tgl_akhir.setCalendarPopup(True)
        filter_row.addWidget(self.tgl_akhir)

        filter_row.addWidget(QLabel('Pengeluar:'))
        self.user_combo = QComboBox()
        self.user_combo.addItem('All User')
        self.load_user_options()
        filter_row.addWidget(self.user_combo)

        filter_row.addWidget(QLabel('Kategori:'))
        self.kategori_combo = QComboBox()
        self.kategori_combo.addItem('All Kategori')
        self.load_kategori_options()
        filter_row.addWidget(self.kategori_combo)

        filter_row.addWidget(QLabel('Transaksi:'))
        self.jenis_combo = QComboBox()
        self.jenis_combo.addItems(['Keduanya', 'IN', 'OUT'])
        filter_row.addWidget(self.jenis_combo)

        self.btn_tampilkan = QPushButton('Tampilkan')
        self.btn_tampilkan.setStyleSheet('background:#FF2800; color:#FFF; font-size:16px; padding:8px 24px; border-radius:8px; font-weight:bold;')
        self.btn_tampilkan.clicked.connect(self.load_data)
        filter_row.addWidget(self.btn_tampilkan)

        layout.addLayout(filter_row)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(['No', 'Jenis', 'Part Number', 'Nama Barang', 'Kategori', 'Qty', 'Pengeluar', 'Penerima', 'Menyetujui'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Export button
        btn_row = QHBoxLayout()
        self.btn_export = QPushButton('Export PDF')
        self.btn_export.setStyleSheet('background:#FF2800; color:#FFF; font-size:16px; padding:8px 24px; border-radius:8px; font-weight:bold; margin-top:16px;')
        self.btn_export.clicked.connect(self.export_pdf)
        btn_row.addWidget(self.btn_export)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.setLayout(layout)
        self.setStyleSheet('background:#FFF; font-family: Segoe UI, Arial, sans-serif;')

    def load_user_options(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT username FROM users ORDER BY username')
        users = [row[0] for row in c.fetchall() if row[0]]
        self.user_combo.addItems(users)
        conn.close()

    def load_kategori_options(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT DISTINCT kategori FROM barang ORDER BY kategori')
        kategori = [row[0] for row in c.fetchall() if row[0]]
        self.kategori_combo.addItems(kategori)
        conn.close()

    def load_data(self):
        tgl_awal = self.tgl_awal.date().toString('yyyy-MM-dd')
        tgl_akhir = self.tgl_akhir.date().toString('yyyy-MM-dd')
        user = self.user_combo.currentText()
        kategori = self.kategori_combo.currentText()
        jenis = self.jenis_combo.currentText()

        conn = get_connection()
        c = conn.cursor()
        data = []

        if jenis in ['Keduanya', 'IN']:
            q_in = '''
                SELECT "IN", partnumber, nama, kategori, qty, penerima, penerima, "-" 
                FROM transaksi_in 
                WHERE tanggal >= ? AND tanggal <= ?
            '''
            params = [tgl_awal, tgl_akhir]
            if user != 'All User':
                q_in += ' AND penerima = ?'
                params.append(user)
            if kategori != 'All Kategori':
                q_in += ' AND kategori = ?'
                params.append(kategori)
            c.execute(q_in, params)
            data += c.fetchall()

        if jenis in ['Keduanya', 'OUT']:
            q_out = '''
                SELECT "OUT", partnumber, nama, kategori, qty, pengeluar, penerima, approver 
                FROM transaksi_out 
                WHERE tanggal >= ? AND tanggal <= ?
            '''
            params = [tgl_awal, tgl_akhir]
            if user != 'All User':
                q_out += ' AND pengeluar = ?'
                params.append(user)
            if kategori != 'All Kategori':
                q_out += ' AND kategori = ?'
                params.append(kategori)
            c.execute(q_out, params)
            data += c.fetchall()

        conn.close()

        data.sort(key=lambda x: x[0])  # sort by jenis if needed
        self.table.setRowCount(len(data))
        for i, row in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            for j in range(len(row)):
                self.table.setItem(i, j + 1, QTableWidgetItem(str(row[j])))
        self.data_export = data

    def export_pdf(self):
        if not hasattr(self, 'data_export') or not self.data_export:
            QMessageBox.warning(self, 'Export PDF', 'Tidak ada data untuk diexport!')
            return

        headers = ['No', 'Jenis', 'Part Number', 'Nama Barang', 'Kategori', 'Qty', 'Pengeluar', 'Penerima', 'Menyetujui']
        data = []
        for i, row in enumerate(self.data_export):
            data.append([
                str(i + 1),
                row[0], row[1], row[2], row[3],
                str(row[4]), row[5], row[6], row[7]
            ])

        filename, _ = QFileDialog.getSaveFileName(self, 'Simpan PDF', 'Report_Custom.pdf', 'PDF Files (*.pdf)')
        if filename:
            export_custom_pdf(filename, data, headers)
            QMessageBox.information(self, 'Export PDF', f'PDF berhasil disimpan: {filename}')
