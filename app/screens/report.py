from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout, QMessageBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from database.db import get_connection
from utils.export_pdf import export_in_pdf, export_out_pdf
from utils.theme import theme
import os
import datetime

def truncate(text, maxlen):
    text = str(text)
    return text if len(text) <= maxlen else text[:maxlen-3] + '...'

class ReportScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header modern
        header = QLabel('Report Harian')
        self.header = header
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(header)
        
        # Date picker dalam card
        date_card = QWidget()
        self.date_card = date_card
        date_row = QHBoxLayout(date_card)
        date_row.setSpacing(12)
        date_label = QLabel('Pilih Tanggal:')
        self.date_label = date_label
        date_row.addWidget(date_label)
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        # Input styling will be applied in apply_theme method
        self.date_edit.dateChanged.connect(self.on_date_changed)
        date_row.addWidget(self.date_edit)
        date_row.addStretch()
        layout.addWidget(date_card)
        # Label IN
        label_in = QLabel('📥 Transaksi IN')
        self.label_in = label_in
        layout.addWidget(label_in)
        self.table_in = QTableWidget()
        self.table_in.setColumnCount(7)
        self.table_in.setHorizontalHeaderLabels(['No', 'Part Number', 'Nama Barang', 'Kategori', 'Qty', 'Penerima', 'Waktu'])
        header_in = self.table_in.horizontalHeader()
        if header_in is not None:
            header_in.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            header_in.setFixedHeight(40)
        # Table styling will be applied in apply_theme method
        self.table_in.verticalHeader().setVisible(False)
        self.table_in.setAlternatingRowColors(True)
        self.table_in.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_in.setMinimumHeight(120)
        layout.addWidget(self.table_in)
        self.label_no_in = QLabel('')
        layout.addWidget(self.label_no_in)
        # Label OUT
        label_out = QLabel('📤 Transaksi OUT')
        self.label_out = label_out
        layout.addWidget(label_out)
        self.table_out = QTableWidget()
        self.table_out.setColumnCount(9)
        self.table_out.setHorizontalHeaderLabels(['No', 'Part Number', 'Nama Barang', 'Kategori', 'Qty', 'Pengeluar', 'Penerima', 'Menyetujui', 'Waktu'])
        header_out = self.table_out.horizontalHeader()
        if header_out is not None:
            header_out.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            header_out.setFixedHeight(40)
        # Table styling will be applied in apply_theme method
        self.table_out.verticalHeader().setVisible(False)
        self.table_out.setAlternatingRowColors(True)
        self.table_out.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_out.setMinimumHeight(120)
        layout.addWidget(self.table_out)
        self.label_no_out = QLabel('')
        layout.addWidget(self.label_no_out)
        # Tombol Export PDF dalam card
        btn_card = QWidget()
        self.btn_card = btn_card
        btn_row = QHBoxLayout(btn_card)
        btn_row.setSpacing(12)
        self.btn_export_in = QPushButton('Export PDF IN')
        # Button styling will be applied in apply_theme method
        self.btn_export_in.clicked.connect(self.export_pdf_in)
        btn_row.addWidget(self.btn_export_in)
        self.btn_export_out = QPushButton('Export PDF OUT')
        # Button styling will be applied in apply_theme method
        self.btn_export_out.clicked.connect(self.export_pdf_out)
        btn_row.addWidget(self.btn_export_out)
        self.btn_export_harian = QPushButton('Export PDF Harian')
        # Button styling will be applied in apply_theme method
        self.btn_export_harian.clicked.connect(self.export_pdf_harian)
        btn_row.addWidget(self.btn_export_harian)
        btn_row.addStretch()
        layout.addWidget(btn_card)

        self.setLayout(layout)
        # Apply theme
        self.apply_theme()

    def on_date_changed(self, qdate):
        self.load_data()

    def load_data(self):
        tanggal = self.date_edit.date().toString('yyyy-MM-dd')
        # IN
        conn = get_connection()
        c = conn.cursor()
        # Filter berdasarkan tanggal (tanggal LIKE 'tanggal%') untuk menangani format dengan waktu
        c.execute('SELECT partnumber, nama, kategori, qty, penerima, tanggal FROM transaksi_in WHERE tanggal LIKE ?', (f'{tanggal}%',))
        rows_in = c.fetchall()
        self.table_in.setRowCount(len(rows_in))
        if rows_in:
            self.label_no_in.setText('')
        else:
            self.label_no_in.setText('Tidak ada data')
        for i, row in enumerate(rows_in):
            self.table_in.setItem(i, 0, QTableWidgetItem(str(i+1)))
            for j, val in enumerate(row):
                # Format waktu untuk kolom tanggal (index 5)
                if j == 5 and val:
                    # Format waktu: jika sudah ada waktu, tampilkan; jika belum, hanya tanggal
                    val_str = str(val)
                    if len(val_str) > 10:  # Ada waktu (format: YYYY-MM-DD HH:MM:SS)
                        try:
                            # Parse dan format ulang untuk tampilan lebih rapi
                            dt = datetime.datetime.strptime(val_str, "%Y-%m-%d %H:%M:%S")
                            formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
                            self.table_in.setItem(i, j+1, QTableWidgetItem(formatted))
                        except:
                            self.table_in.setItem(i, j+1, QTableWidgetItem(val_str))
                    else:
                        self.table_in.setItem(i, j+1, QTableWidgetItem(val_str))
                else:
                    self.table_in.setItem(i, j+1, QTableWidgetItem(str(val)))
        # OUT
        c.execute('SELECT partnumber, nama, kategori, qty, pengeluar, penerima, approver, tanggal, remarks FROM transaksi_out WHERE tanggal LIKE ?', (f'{tanggal}%',))
        rows_out = c.fetchall()
        self.table_out.setRowCount(len(rows_out))
        if rows_out:
            self.label_no_out.setText('')
        else:
            self.label_no_out.setText('Tidak ada data')
        for i, row in enumerate(rows_out):
            self.table_out.setItem(i, 0, QTableWidgetItem(str(i+1)))
            for j, val in enumerate(row):
                # Format waktu untuk kolom tanggal (index 7)
                if j == 7 and val:
                    # Format waktu: jika sudah ada waktu, tampilkan; jika belum, hanya tanggal
                    val_str = str(val)
                    if len(val_str) > 10:  # Ada waktu (format: YYYY-MM-DD HH:MM:SS)
                        try:
                            # Parse dan format ulang untuk tampilan lebih rapi
                            dt = datetime.datetime.strptime(val_str, "%Y-%m-%d %H:%M:%S")
                            formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
                            self.table_out.setItem(i, j+1, QTableWidgetItem(formatted))
                        except:
                            self.table_out.setItem(i, j+1, QTableWidgetItem(val_str))
                    else:
                        self.table_out.setItem(i, j+1, QTableWidgetItem(val_str))
                else:
                    self.table_out.setItem(i, j+1, QTableWidgetItem(str(val)))
        conn.close()
        self.rows_in = rows_in
        self.rows_out = rows_out

    def export_pdf_in(self):
        if not self.rows_in:
            QMessageBox.information(self, 'Export PDF', 'Tidak ada transaksi IN pada tanggal ini.')
            return
        data = []
        for row in self.rows_in:
            data.append({
                'partnumber': row[0],
                'nama': row[1],
                'kategori': row[2],
                'qty': row[3],
                'penerima': row[4],
                'tanggal': row[5]
            })
        kop_path = os.path.join(os.path.dirname(__file__), '../assets/logo.png')
        from PyQt6.QtWidgets import QFileDialog
        default_name = f'Report_IN_{self.date_edit.date().toString("yyyy-MM-dd")}.pdf'
        filename, _ = QFileDialog.getSaveFileName(self, 'Simpan PDF', default_name, 'PDF Files (*.pdf)')
        if not filename:
            return
        export_in_pdf(filename, data, kop_path=kop_path)
        QMessageBox.information(self, 'Export PDF', f'PDF IN berhasil diexport: {filename}')

    def export_pdf_out(self):
        if not self.rows_out:
            QMessageBox.information(self, 'Export PDF', 'Tidak ada transaksi OUT pada tanggal ini.')
            return
        data = []
        for row in self.rows_out:
            d = {
                'partnumber': row[0],
                'nama': row[1],
                'kategori': row[2],
                'qty': row[3],
                'pengeluar': row[4],
                'penerima': row[5],
                'approver': row[6],
                'tanggal': row[7]
            }
            if len(row) > 8:
                d['remarks'] = row[8]
            data.append(d)
        kop_path = os.path.join(os.path.dirname(__file__), '../assets/logo.png')
        from PyQt6.QtWidgets import QFileDialog
        default_name = f'Report_OUT_{self.date_edit.date().toString("yyyy-MM-dd")}.pdf'
        filename, _ = QFileDialog.getSaveFileName(self, 'Simpan PDF', default_name, 'PDF Files (*.pdf)')
        if not filename:
            return
        export_out_pdf(filename, data, kop_path=kop_path)
        QMessageBox.information(self, 'Export PDF', f'PDF OUT berhasil diexport: {filename}')

    def export_pdf_harian(self):
        if not self.rows_in and not self.rows_out:
            QMessageBox.information(self, 'Export PDF', 'Tidak ada transaksi IN/OUT pada tanggal ini.')
            return
        from PyQt6.QtWidgets import QFileDialog
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.colors import black, HexColor
        from reportlab.lib.utils import ImageReader
        filename, _ = QFileDialog.getSaveFileName(self, 'Simpan PDF', f'Report_Harian_{self.date_edit.date().toString("yyyy-MM-dd")}.pdf', 'PDF Files (*.pdf)')
        if not filename:
            return
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        y = height - 60
        # Logo besar di kiri atas
        logo_path = os.path.join(os.path.dirname(__file__), '../assets/logo.png')
        logo_width = 90
        logo_height = 50
        logo_y = y - logo_height + 10
        if os.path.exists(logo_path):
            c.drawImage(ImageReader(logo_path), 40, logo_y, width=logo_width, height=logo_height, mask='auto')
        text_x = 40 + logo_width + 18
        # Kop surat
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(black)
        c.drawString(text_x, y, "PT. MULTIDAYA MITRA SINERGI")
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(HexColor("#FF2800"))
        c.drawString(text_x, y-20, "PROJECT & ENGINEERING SOLUTIONS")
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(text_x, y-38, "Jl. Cipendawa Lama No.21 Kota Bekasi")
        c.setFont("Helvetica", 12)
        c.drawString(text_x, y-52, "Telepon 0811-9698-237, Fax (021) 82635464")
        c.setFont("Helvetica", 10)
        c.drawString(text_x, y-65, "Instagram : @multidayamitrasinergi")
        c.setLineWidth(2)
        c.line(40, y-80, width-40, y-80)
        c.setLineWidth(1)
        c.line(40, y-85, width-40, y-85)
        y -= 100
        # Tanggal di bawah kop surat
        from datetime import datetime
        tanggal = datetime.now().strftime('%d/%m/%Y')
        # Beri jarak turun sedikit dari kop
        y -= 10
        # Jenis laporan harian
        c.setFont("Helvetica-Bold", 15)
        c.setFillColor(black)
        title = "Laporan Barang Masuk & Keluar (Harian)"
        title_w = c.stringWidth(title, "Helvetica-Bold", 15)
        c.drawString((width - title_w) / 2, y, title)
        y -= 24
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, f"Tanggal: {tanggal}")
        y -= 30
        # Tabel IN
        if self.rows_in:
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(HexColor("#FF2800"))
            c.drawString(40, y, "Transaksi IN")
            y -= 20
            # Table IN
            headers = ['No', 'Part Number', 'Nama Barang', 'Kategori', 'Qty', 'Penerima']
            table_data = [headers]
            from reportlab.platypus import Paragraph, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            styles = getSampleStyleSheet()
            para_style = styles['Normal']
            para_style.fontName = 'Helvetica'
            para_style.fontSize = 10
            para_style.leading = 14
            for idx, row in enumerate(self.rows_in):
                row = list(row) + [''] * (6 - len(row))
                table_data.append([
                    str(idx+1),
                    Paragraph(str(row[0]), para_style),
                    Paragraph(str(row[1]), para_style),
                    str(row[2]),
                    str(row[3]),
                    str(row[4])
                ])
            col_widths = [30, 100, 120, 60, 35, 60]
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FF2800')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('ALIGN', (0,0), (-1,0), 'CENTER'),
                ('ALIGN', (0,1), (0,-1), 'CENTER'),
                ('ALIGN', (1,1), (1,-1), 'CENTER'),
                ('ALIGN', (3,1), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#000000')),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('ROWHEIGHT', (0,1), (-1,-1), 32),
            ]))
            table.wrapOn(c, width, height)
            table.drawOn(c, 30, y - table._height)
            y = y - table._height - 18
        # Tabel OUT
        if self.rows_out:
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(HexColor("#FF2800"))
            c.drawString(40, y, "Transaksi OUT")
            y -= 20
            # Table OUT
            headers = ['No', 'Part Number', 'Nama Barang', 'Kategori', 'Qty', 'Pengeluar', 'Penerima', 'Menyetujui']
            table_data = [headers]
            for idx, row in enumerate(self.rows_out):
                row = list(row) + [''] * (8 - len(row))
                table_data.append([
                    str(idx+1),
                    Paragraph(str(row[0]), para_style),
                    Paragraph(str(row[1]), para_style),
                    str(row[2]),
                    str(row[3]),
                    str(row[4]),
                    str(row[5]),
                    str(row[6])
                ])
            col_widths = [30, 100, 120, 60, 35, 60, 60, 60]
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FF2800')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('ALIGN', (0,0), (-1,0), 'CENTER'),
                ('ALIGN', (0,1), (0,-1), 'CENTER'),
                ('ALIGN', (1,1), (1,-1), 'CENTER'),
                ('ALIGN', (3,1), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#000000')),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('ROWHEIGHT', (0,1), (-1,-1), 32),
            ]))
            table.wrapOn(c, width, height)
            table.drawOn(c, 30, y - table._height)
            y = y - table._height - 18
        c.save()
        QMessageBox.information(self, 'Export PDF', f'PDF Harian berhasil diexport: {filename}')

    def showEvent(self, event):
        super().showEvent(event)
        self.load_data()

    def go_back(self):
        if hasattr(self, 'parent') and self.parent and hasattr(self.parent, 'go_to_page'):
            self.parent.go_to_page(0)
    
    def apply_theme(self):
        """Apply current theme to report screen"""
        # Header styling
        self.header.setStyleSheet(f'font-size:32px; color:{theme.get_color("accent")}; font-weight:bold; margin-bottom:12px;')
        
        # Card styling
        self.date_card.setStyleSheet(theme.get_card_style())
        self.btn_card.setStyleSheet(theme.get_card_style())
        
        # Label styling
        self.date_label.setStyleSheet(f'font-size:16px; color:{theme.get_color("text_primary")}; font-weight:600;')
        self.label_in.setStyleSheet(f'font-size:20px; color:{theme.get_color("accent")}; font-weight:bold; margin-top:8px;')
        self.label_out.setStyleSheet(f'font-size:20px; color:{theme.get_color("accent")}; font-weight:bold; margin-top:8px;')
        self.label_no_in.setStyleSheet(f'font-size:14px; color:{theme.get_color("text_muted")}; margin-bottom:8px;')
        self.label_no_out.setStyleSheet(f'font-size:14px; color:{theme.get_color("text_muted")}; margin-bottom:8px;')
        
        # Input styling
        self.date_edit.setStyleSheet(theme.get_input_style())
        
        # Button styling
        self.btn_export_in.setStyleSheet(theme.get_button_style('primary'))
        self.btn_export_out.setStyleSheet(theme.get_button_style('primary'))
        self.btn_export_harian.setStyleSheet(theme.get_button_style('secondary'))
        
        # Table styling
        table_style = theme.get_table_style()
        self.table_in.setStyleSheet(table_style)
        self.table_out.setStyleSheet(table_style)
        
        # Main background
        self.setStyleSheet(f'background: {theme.get_color("background")}; font-family: Segoe UI, Arial, sans-serif;') 