from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout, QMessageBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from database.db import get_connection
import datetime

class ReportStockScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        # Header
        header = QLabel('Laporan Stok Akhir Periode')
        header.setStyleSheet('font-size:32px; color:#FF2800; font-weight:bold; margin-bottom:12px;')
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(header)
        # Pilih tanggal awal & akhir
        date_row = QHBoxLayout()
        date_label1 = QLabel('Tanggal Awal:')
        date_label1.setStyleSheet('font-size:18px; color:#222; font-weight:bold; margin-right:12px;')
        date_row.addWidget(date_label1)
        self.date_awal = QDateEdit()
        self.date_awal.setDisplayFormat('yyyy-MM-dd')
        self.date_awal.setDate(QDate.currentDate().addMonths(-1))
        self.date_awal.setCalendarPopup(True)
        self.date_awal.setStyleSheet('font-size:18px; padding:8px 18px; border-radius:8px; border:1.5px solid #FF2800; min-width:140px;')
        date_row.addWidget(self.date_awal)
        date_label2 = QLabel('Tanggal Akhir:')
        date_label2.setStyleSheet('font-size:18px; color:#222; font-weight:bold; margin-left:18px; margin-right:12px;')
        date_row.addWidget(date_label2)
        self.date_akhir = QDateEdit()
        self.date_akhir.setDisplayFormat('yyyy-MM-dd')
        self.date_akhir.setDate(QDate.currentDate())
        self.date_akhir.setCalendarPopup(True)
        self.date_akhir.setStyleSheet('font-size:18px; padding:8px 18px; border-radius:8px; border:1.5px solid #FF2800; min-width:140px;')
        date_row.addWidget(self.date_akhir)
        btn_refresh = QPushButton('Tampilkan')
        btn_refresh.setStyleSheet('background:#FF2800; color:#FFF; font-size:18px; padding:10px 32px; border-radius:10px; font-weight:bold;')
        btn_refresh.clicked.connect(self.load_data)
        date_row.addWidget(btn_refresh)
        date_row.addStretch()
        layout.addLayout(date_row)
        # Tabel stok akhir
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Part Number', 'Nama Barang', 'Stok Awal', 'Masuk', 'Keluar', 'Stok Akhir'])
        header = self.table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            header.setFixedHeight(44)
        self.table.setStyleSheet('QTableWidget {font-size:18px; padding:10px; background:#FFF; border-radius:14px; border:1.5px solid #eee;} QHeaderView::section {background:#FFF; color:#FF2800; font-size:20px; font-weight:bold; height:44px; border:1.5px solid #eee; border-radius:10px;}')
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setMinimumHeight(180)
        layout.addWidget(self.table)
        # Tombol Export
        btn_row = QHBoxLayout()
        self.btn_export_excel = QPushButton('Export Excel')
        self.btn_export_excel.setStyleSheet('background:#FF2800; color:#FFF; font-size:20px; padding:12px 36px; border-radius:12px; font-weight:bold;')
        self.btn_export_excel.clicked.connect(self.export_excel)
        btn_row.addWidget(self.btn_export_excel)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.setLayout(layout)
        self.setStyleSheet('background:#FFF; font-family: Segoe UI, Arial, sans-serif;')
        self.load_data()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_data()

    def load_data(self):
        tgl_awal = self.date_awal.date().toString('yyyy-MM-dd')
        tgl_akhir = self.date_akhir.date().toString('yyyy-MM-dd')
        conn = get_connection()
        c = conn.cursor()
        # Ambil semua barang
        c.execute('SELECT partnumber, nama FROM barang ORDER BY partnumber')
        barang = c.fetchall()
        data = []
        for partnumber, nama in barang:
            # Stok awal = stok sebelum tgl_awal
            c.execute('SELECT SUM(qty) FROM transaksi_in WHERE partnumber=? AND tanggal<?', (partnumber, tgl_awal))
            masuk_awal = c.fetchone()[0] or 0
            c.execute('SELECT SUM(qty) FROM transaksi_out WHERE partnumber=? AND tanggal<?', (partnumber, tgl_awal))
            keluar_awal = c.fetchone()[0] or 0
            # Stok awal = stok database - (masuk setelah tgl_awal) + (keluar setelah tgl_awal)
            c.execute('SELECT stok FROM barang WHERE partnumber=?', (partnumber,))
            stok_db = c.fetchone()[0] or 0
            c.execute('SELECT SUM(qty) FROM transaksi_in WHERE partnumber=? AND tanggal>=?', (partnumber, tgl_awal))
            masuk_periode = c.fetchone()[0] or 0
            c.execute('SELECT SUM(qty) FROM transaksi_out WHERE partnumber=? AND tanggal>=?', (partnumber, tgl_awal))
            keluar_periode = c.fetchone()[0] or 0
            stok_awal = stok_db - masuk_periode + keluar_periode
            # Masuk/Keluar selama periode
            c.execute('SELECT SUM(qty) FROM transaksi_in WHERE partnumber=? AND tanggal>=? AND tanggal<=?', (partnumber, tgl_awal, tgl_akhir))
            masuk = c.fetchone()[0] or 0
            c.execute('SELECT SUM(qty) FROM transaksi_out WHERE partnumber=? AND tanggal>=? AND tanggal<=?', (partnumber, tgl_awal, tgl_akhir))
            keluar = c.fetchone()[0] or 0
            # Stok akhir = stok_awal + masuk - keluar
            stok_akhir = stok_awal + masuk - keluar
            data.append((partnumber, nama, stok_awal, masuk, keluar, stok_akhir))
        self.table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j in range(min(len(row), self.table.columnCount())):
                self.table.setItem(i, j, QTableWidgetItem(str(row[j])))
        conn.close()

    def export_excel(self):
        from PyQt6.QtWidgets import QFileDialog
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Stok Akhir'
        ws.append(['No', 'Part Number', 'Nama Barang', 'Stok Awal', 'Masuk', 'Keluar', 'Stok Akhir'])
        for i in range(self.table.rowCount()):
            ws.append([
                self.table.item(i,0).text() if self.table.item(i,0) else '',
                self.table.item(i,1).text() if self.table.item(i,1) else '',
                self.table.item(i,2).text() if self.table.item(i,2) else '',
                self.table.item(i,3).text() if self.table.item(i,3) else '',
                self.table.item(i,4).text() if self.table.item(i,4) else '',
                self.table.item(i,5).text() if self.table.item(i,5) else '',
                self.table.item(i,6).text() if self.table.item(i,6) else ''
            ])
        filename, _ = QFileDialog.getSaveFileName(self, 'Simpan Excel', 'Laporan_Stok_Akhir.xlsx', 'Excel Files (*.xlsx)')
        if filename:
            try:
                wb.save(filename)
                QMessageBox.information(self, 'Export Excel', f'Excel berhasil diexport: {filename}')
            except Exception as e:
                QMessageBox.warning(self, 'Export Excel', f'Gagal export Excel: {e}')

    def go_back(self):
        if hasattr(self, 'parent') and self.parent and hasattr(self.parent, 'go_to_page'):
            self.parent.go_to_page(0) 