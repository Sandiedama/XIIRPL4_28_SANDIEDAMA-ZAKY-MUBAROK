from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QComboBox, QDateEdit, QLineEdit, QPushButton
from database.db import get_connection
from PyQt6.QtCore import Qt, QDate

class LogAktivitasScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        self.load_filter_options()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QLabel('Log Aktivitas')
        header.setStyleSheet('font-size:32px; color:#FF2800; font-weight:bold; margin-bottom:12px;')
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(header)
        # Filter row
        filter_row = QHBoxLayout()
        self.user_combo = QComboBox()
        self.user_combo.setMinimumWidth(120)
        self.user_combo.currentIndexChanged.connect(self.load_data)
        filter_row.addWidget(QLabel('User:'))
        filter_row.addWidget(self.user_combo)
        self.aksi_combo = QComboBox()
        self.aksi_combo.setMinimumWidth(120)
        self.aksi_combo.currentIndexChanged.connect(self.load_data)
        filter_row.addWidget(QLabel('Aksi:'))
        filter_row.addWidget(self.aksi_combo)
        self.tgl_awal = QDateEdit()
        self.tgl_awal.setDisplayFormat('yyyy-MM-dd')
        self.tgl_awal.setDate(QDate.currentDate().addMonths(-1))
        self.tgl_awal.setCalendarPopup(True)
        self.tgl_awal.dateChanged.connect(self.load_data)
        filter_row.addWidget(QLabel('Dari:'))
        filter_row.addWidget(self.tgl_awal)
        self.tgl_akhir = QDateEdit()
        self.tgl_akhir.setDisplayFormat('yyyy-MM-dd')
        self.tgl_akhir.setDate(QDate.currentDate())
        self.tgl_akhir.setCalendarPopup(True)
        self.tgl_akhir.dateChanged.connect(self.load_data)
        filter_row.addWidget(QLabel('Sampai:'))
        filter_row.addWidget(self.tgl_akhir)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Cari keterangan...')
        self.search_input.setMinimumWidth(160)
        self.search_input.textChanged.connect(self.load_data)
        filter_row.addWidget(self.search_input)
        filter_row.addStretch()
        layout.addLayout(filter_row)
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['User', 'Aksi', 'Tabel', 'Data ID', 'Waktu', 'Keterangan'])
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header_view.setFixedHeight(44)
        self.table.setStyleSheet('QTableWidget {font-size:16px; padding:8px; background:#FFF; border-radius:14px; border:1.5px solid #eee;} QHeaderView::section {background:#FFF; color:#FF2800; font-size:18px; font-weight:bold; height:44px; border:1.5px solid #eee; border-radius:10px;}')
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # Tombol Export Excel
        btn_row = QHBoxLayout()
        self.btn_export_excel = QPushButton('Export Excel')
        self.btn_export_excel.setStyleSheet('background:#228B22; color:#FFF; font-size:15px; padding:8px 24px; border-radius:8px; font-weight:bold;')
        self.btn_export_excel.clicked.connect(self.export_excel)
        btn_row.addWidget(self.btn_export_excel)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.setStyleSheet('background:#FFF; font-family: Segoe UI, Arial, sans-serif;')

    def load_filter_options(self):
        conn = get_connection()
        c = conn.cursor()
        # User options
        c.execute('SELECT DISTINCT u.username FROM log_aktivitas l LEFT JOIN users u ON l.user_id = u.id ORDER BY u.username')
        users = [row[0] for row in c.fetchall() if row[0]]
        self.user_combo.clear()
        self.user_combo.addItem('Semua')
        self.user_combo.addItems(users)
        # Aksi options
        c.execute('SELECT DISTINCT aksi FROM log_aktivitas ORDER BY aksi')
        aksi_list = [row[0] for row in c.fetchall() if row[0]]
        self.aksi_combo.clear()
        self.aksi_combo.addItem('Semua')
        self.aksi_combo.addItems(aksi_list)
        conn.close()

    def load_data(self):
        user = self.user_combo.currentText()
        aksi = self.aksi_combo.currentText()
        tgl_awal = self.tgl_awal.date().toString('yyyy-MM-dd')
        tgl_akhir = self.tgl_akhir.date().toString('yyyy-MM-dd')
        keyword = self.search_input.text().strip()
        query = '''
            SELECT u.username, l.aksi, l.tabel, l.data_id, l.waktu, l.keterangan
            FROM log_aktivitas l
            LEFT JOIN users u ON l.user_id = u.id
            WHERE 1=1
        '''
        params = []
        if user and user != 'Semua':
            query += ' AND u.username = ?'
            params.append(user)
        if aksi and aksi != 'Semua':
            query += ' AND l.aksi = ?'
            params.append(aksi)
        if tgl_awal:
            query += ' AND date(l.waktu) >= ?'
            params.append(tgl_awal)
        if tgl_akhir:
            query += ' AND date(l.waktu) <= ?'
            params.append(tgl_akhir)
        if keyword:
            query += ' AND l.keterangan LIKE ?'
            params.append(f'%{keyword}%')
        query += ' ORDER BY l.waktu DESC LIMIT 200'
        conn = get_connection()
        c = conn.cursor()
        c.execute(query, params)
        rows = c.fetchall()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val) if val is not None else ''))
        conn.close()

    def export_excel(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import openpyxl
        filename, _ = QFileDialog.getSaveFileName(self, 'Simpan Excel', 'Log_Aktivitas.xlsx', 'Excel Files (*.xlsx)')
        if not filename:
            return
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Log Aktivitas'
        # Header
        headers = ['User', 'Aksi', 'Tabel', 'Data ID', 'Waktu', 'Keterangan']
        ws.append(headers)
        # Data
        for row in range(self.table.rowCount()):
            ws.append([self.table.item(row, col).text() if self.table.item(row, col) else '' for col in range(self.table.columnCount())])
        try:
            wb.save(filename)
            QMessageBox.information(self, 'Export Excel', f'File berhasil disimpan: {filename}')
        except Exception as e:
            QMessageBox.warning(self, 'Export Excel', f'Gagal menyimpan file: {e}') 