from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer
from database.db import get_connection, get_low_stock_items
from utils.theme import theme
import datetime
# Charts: gunakan Matplotlib untuk line chart
try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
except Exception:
    FigureCanvas = None
    Figure = None

class DashboardScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._low_stock_notified = False
        self.init_ui()
        self.load_stats()
        self.load_line_chart()
        # Auto refresh dashboard tiap 30 detik
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(30_000)
        self.refresh_timer.timeout.connect(self.refresh_dashboard)
        self.refresh_timer.start()

    def refresh_dashboard(self):
        self.load_stats()
        self.load_line_chart()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        # Header dengan theme support
        header_frame = QFrame()
        self.header_frame = header_frame
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(24, 18, 24, 18)
        header_layout.setSpacing(12)
        home_icon = QLabel('🏠')
        self.home_icon = home_icon
        header_layout.addWidget(home_icon)
        header_label = QLabel('Dashboard')
        header_label.setFont(QFont('Segoe UI', 22, QFont.Weight.Bold))
        self.header_label = header_label
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_frame.setLayout(header_layout)
        self.layout.addWidget(header_frame)
        # Row kartu statistik
        stat_row = QHBoxLayout()
        stat_row.setContentsMargins(24, 16, 24, 0)
        stat_row.setSpacing(16)
        self.stat_in = self._stat_widget('📥', 'Barang Masuk Hari Ini', '...')
        self.stat_total = self._stat_widget('🗃️', 'Total Data Barang', '...')
        self.stat_out = self._stat_widget('📤', 'Barang Keluar Hari Ini', '...')
        stat_row.addWidget(self.stat_in)
        stat_row.addWidget(self.stat_total)
        stat_row.addWidget(self.stat_out)
        self.layout.addLayout(stat_row)
        # Apply theme
        self.apply_theme()
        
        # Line Chart Container
        chart_frame = QFrame()
        chart_frame.setProperty('modernCard', True)
        chart_layout = QVBoxLayout()
        chart_layout.setContentsMargins(16, 16, 16, 12)
        title = QLabel('Tren 14 Hari - IN vs OUT')
        title.setStyleSheet('font-size:16px; font-weight:bold; color:#222;')
        chart_layout.addWidget(title)
        if FigureCanvas and Figure:
            self.line_canvas = FigureCanvas(Figure(figsize=(5, 2)))
            chart_layout.addWidget(self.line_canvas)
        else:
            placeholder = QLabel('Chart tidak tersedia (Matplotlib belum terpasang).')
            placeholder.setStyleSheet('color:#888;')
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chart_layout.addWidget(placeholder)
            self.line_canvas = None
        chart_frame.setLayout(chart_layout)
        self.layout.addWidget(chart_frame)

        # Warning section untuk stok rendah
        self.warning_section = self._create_warning_section()
        self.layout.addWidget(self.warning_section)
        
        self.layout.addStretch()
        self.setLayout(self.layout)
        self.setStyleSheet('background:#FFF; font-family: Segoe UI, Arial, sans-serif;')

    def _create_warning_section(self):
        """Membuat section warning untuk stok rendah"""
        warning_frame = QFrame()
        warning_frame.setStyleSheet('''
            QFrame {
                background: #FFF8E6;
                border: 1px solid #FFE0B2;
                border-radius: 14px;
                margin: 12px 24px 0 24px;
                padding: 10px 12px;
            }
        ''')
        
        warning_layout = QVBoxLayout()
        warning_layout.setContentsMargins(12, 10, 12, 10)
        warning_layout.setSpacing(8)
        
        # Header warning
        warning_header = QHBoxLayout()
        warning_icon = QLabel('⚠️')
        warning_icon.setStyleSheet('font-size: 18px;')
        warning_title = QLabel('Peringatan Stok Rendah')
        warning_title.setStyleSheet('font-size: 15px; font-weight: bold; color: #E65100;')
        warning_header.addWidget(warning_icon)
        warning_header.addWidget(warning_title)
        warning_header.addStretch()
        
        # Tombol untuk melihat detail
        self.btn_view_low_stock = QPushButton('Lihat Detail')
        self.btn_view_low_stock.setStyleSheet('''
            QPushButton {
                background: #FF9800;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background: #F57C00; }
        ''')
        self.btn_view_low_stock.clicked.connect(self.show_low_stock_details)
        warning_header.addWidget(self.btn_view_low_stock)
        
        warning_layout.addLayout(warning_header)
        
        # Content warning dengan scroll area yang lebih kecil
        from PyQt6.QtWidgets import QScrollArea, QWidget
        
        # Container untuk content
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.warning_content = QLabel('Memeriksa stok rendah...')
        self.warning_content.setStyleSheet('font-size: 13px; color: #B45309; line-height: 1.4; padding: 4px;')
        self.warning_content.setWordWrap(True)
        self.warning_content.setMinimumHeight(36)
        self.warning_content.setMaximumHeight(72)
        content_layout.addWidget(self.warning_content)
        
        content_widget.setLayout(content_layout)
        
        # Scroll area dengan scroll bar yang lebih kecil
        scroll_area = QScrollArea()
        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(80)
        scroll_area.setMinimumHeight(40)
        scroll_area.setStyleSheet('''
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #F0F0F0;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #C0C0C0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #A0A0A0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        ''')
        
        warning_layout.addWidget(scroll_area)
        
        warning_frame.setLayout(warning_layout)
        return warning_frame

    def _stat_widget(self, icon, label, value):
        from PyQt6.QtWidgets import QFrame
        card = QFrame()
        card.setProperty('modernCard', True)
        card.setMinimumWidth(240)
        card.setMaximumWidth(420)
        card.setMinimumHeight(130)
        card.setStyleSheet('QFrame {padding: 20px 16px 16px 16px;}')
        l = QVBoxLayout()
        l.setContentsMargins(0,0,0,0)
        l.setSpacing(8)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f'font-size:36px; color:{theme.get_color("accent")}; margin-bottom:4px;')
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(icon_label)
        
        # Value - lebih kecil dan dengan word wrap
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f'font-size:32px; font-weight:bold; color:{theme.get_color("text_primary")}; margin-bottom:4px; line-height:1.2;')
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setWordWrap(True)
        value_label.setMinimumHeight(40)
        l.addWidget(value_label)
        
        # Label
        label_label = QLabel(label)
        label_label.setStyleSheet(f'font-size:14px; color:{theme.get_color("text_secondary")}; margin-bottom:0px; line-height:1.3;')
        label_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_label.setWordWrap(True)
        l.addWidget(label_label)
        
        l.addStretch()
        card.setLayout(l)
        return card

    # mini card dihapus

    def load_line_chart(self):
        if not getattr(self, 'line_canvas', None):
            return
        try:
            conn = get_connection()
            c = conn.cursor()
            days = 14
            labels = []
            in_values = []
            out_values = []
            today = datetime.date.today()
            for d in range(days):
                day = today - datetime.timedelta(days=days - d - 1)
                ds = day.isoformat()
                labels.append(day.strftime('%d/%m'))
                c.execute('SELECT COALESCE(SUM(qty),0) FROM transaksi_in WHERE tanggal=?', (ds,))
                in_values.append(c.fetchone()[0] or 0)
                c.execute('SELECT COALESCE(SUM(qty),0) FROM transaksi_out WHERE tanggal=?', (ds,))
                out_values.append(c.fetchone()[0] or 0)
            conn.close()
        except Exception:
            return
        ax = self.line_canvas.figure.subplots()
        ax.clear()
        
        # Set background color based on theme
        if theme.get_current_theme() == 'dark':
            ax.set_facecolor('#2d2d2d')
            self.line_canvas.figure.patch.set_facecolor('#1a1a1a')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
        else:
            ax.set_facecolor('white')
            self.line_canvas.figure.patch.set_facecolor('white')
            ax.tick_params(colors='black')
            ax.xaxis.label.set_color('black')
            ax.yaxis.label.set_color('black')
            ax.title.set_color('black')
        
        ax.plot(labels, in_values, color=theme.get_color('accent'), linewidth=2.2, marker='o', label='IN')
        ax.plot(labels, out_values, color='#2962FF', linewidth=2.2, marker='o', label='OUT')
        ax.set_ylabel('Qty')
        ax.set_xlabel('Tanggal')
        ax.grid(True, linestyle='--', alpha=0.25)
        ax.legend()
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha('right')
        self.line_canvas.figure.tight_layout()
        self.line_canvas.draw()

    def load_stats(self):
        conn = get_connection()
        c = conn.cursor()
        # Total barang
        c.execute('SELECT COUNT(*) FROM barang')
        total_barang = c.fetchone()[0]
        # Barang masuk hari ini
        today = datetime.date.today().isoformat()
        c.execute('SELECT SUM(qty) FROM transaksi_in WHERE tanggal=?', (today,))
        in_today = c.fetchone()[0] or 0
        # Barang keluar hari ini
        c.execute('SELECT SUM(qty) FROM transaksi_out WHERE tanggal=?', (today,))
        out_today = c.fetchone()[0] or 0
        
        # Update statistik kategori
        c.execute('SELECT COUNT(DISTINCT kategori) FROM barang WHERE kategori IS NOT NULL AND kategori != ""')
        categories_count = c.fetchone()[0]
        
        conn.close()
        
        # Update UI
        self.stat_total.layout().itemAt(1).widget().setText(str(total_barang))
        self.stat_in.layout().itemAt(1).widget().setText(str(in_today))
        self.stat_out.layout().itemAt(1).widget().setText(str(out_today))
        
        # Update statistik stok rendah (mini card)
        low_stock_count = len(get_low_stock_items())
        try:
            # Jika widget lama tidak ada, abaikan
            self.stat_low_stock.layout().itemAt(1).widget().setText(str(low_stock_count))
        except Exception:
            pass
        try:
            self.stat_categories.layout().itemAt(1).widget().setText(str(categories_count))
        except Exception:
            pass
        # Mini cards dihapus
        
        # Update warning section
        self.update_warning_section()

    def update_warning_section(self):
        """Update warning section dengan data stok rendah"""
        low_stock_items = get_low_stock_items()
        
        if low_stock_items:
            # Ada barang dengan stok rendah
            self.warning_section.setVisible(True)
            warning_text = f"Ada {len(low_stock_items)} barang dengan stok rendah:\n"
            for i, (partnumber, nama, stok, rop) in enumerate(low_stock_items[:3]):  # Tampilkan max 3 item
                warning_text += f"• {partnumber} ({nama}): Stok {stok}, ROP {rop}\n"
            if len(low_stock_items) > 3:
                warning_text += f"... dan {len(low_stock_items) - 3} barang lainnya"
            
            self.warning_content.setText(warning_text)
            self.btn_view_low_stock.setText(f"Lihat Semua ({len(low_stock_items)})")
            # Tampilkan notifikasi sekali per sesi saat terdeteksi stok rendah
            if not self._low_stock_notified:
                try:
                    QMessageBox.warning(self, 'Stok Rendah', 'Ada barang yang mencapai/bawah ROP. Klik "Lihat Detail" untuk info lengkap.')
                except Exception:
                    pass
                self._low_stock_notified = True
        else:
            # Tidak ada barang dengan stok rendah
            self.warning_section.setVisible(False)
            self._low_stock_notified = False

    def show_low_stock_details(self):
        """Menampilkan dialog detail barang dengan stok rendah"""
        low_stock_items = get_low_stock_items()
        
        if not low_stock_items:
            QMessageBox.information(self, 'Stok Rendah', 'Tidak ada barang dengan stok rendah.')
            return
        
        # Buat dialog detail
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
        
        dialog = QDialog(self)
        dialog.setWindowTitle('Detail Barang dengan Stok Rendah')
        dialog.setModal(True)
        dialog.resize(600, 400)
        
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel(f'Barang dengan Stok ≤ ROP ({len(low_stock_items)} item)')
        header_label.setStyleSheet('font-size: 16px; font-weight: bold; color: #E65100; margin-bottom: 10px;')
        layout.addWidget(header_label)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['Part Number', 'Nama Barang', 'Stok', 'ROP'])
        table.setRowCount(len(low_stock_items))
        
        header = table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        for i, (partnumber, nama, stok, rop) in enumerate(low_stock_items):
            table.setItem(i, 0, QTableWidgetItem(partnumber))
            table.setItem(i, 1, QTableWidgetItem(nama))
            
            stok_item = QTableWidgetItem(str(stok))
            stok_item.setBackground(Qt.GlobalColor.red)
            stok_item.setForeground(Qt.GlobalColor.white)
            table.setItem(i, 2, stok_item)
            
            rop_item = QTableWidgetItem(str(rop))
            rop_item.setBackground(Qt.GlobalColor.red)
            rop_item.setForeground(Qt.GlobalColor.white)
            table.setItem(i, 3, rop_item)
        
        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.exec()

    def load_charts(self):
        conn = get_connection()
        c = conn.cursor()
        today = datetime.date.today().isoformat()
        
        # Pie & Bar chart IN: transaksi_in hari ini (hanya kategori peruntukan)
        c.execute('SELECT kategori, SUM(qty) FROM transaksi_in WHERE tanggal=? AND kategori IN (?, ?, ?, ?) GROUP BY kategori', 
                 (today, 'project', 'retail', 'stock', 'warranty'))
        in_data = c.fetchall()
        in_labels = [row[0] if row[0] else 'Lainnya' for row in in_data]
        in_values = [row[1] or 0 for row in in_data]
        
        # Pie & Bar chart OUT: transaksi_out hari ini (hanya kategori peruntukan)
        c.execute('SELECT kategori, SUM(qty) FROM transaksi_out WHERE tanggal=? AND kategori IN (?, ?, ?, ?) GROUP BY kategori', 
                 (today, 'project', 'retail', 'stock', 'warranty'))
        out_data = c.fetchall()
        out_labels = [row[0] if row[0] else 'Lainnya' for row in out_data]
        out_values = [row[1] or 0 for row in out_data]
        conn.close()
        
        # Warna untuk kategori peruntukan (project, retail, stock, warranty)
        category_colors = {
            'project': '#FF2800',      # Merah
            'retail': '#FF8A65',       # Orange
            'stock': '#FFD180',        # Kuning
            'warranty': '#81C784',     # Hijau
            'Lainnya': '#9E9E9E'       # Abu-abu untuk kategori yang tidak terdaftar
        }
        
        # Pie chart IN
        pie_in_ax = self.pie_in_canvas.figure.subplots()
        pie_in_ax.clear()
        if in_values and sum(in_values) > 0:
            # Gunakan warna yang sesuai dengan kategori
            in_colors = [category_colors.get(label, '#9E9E9E') for label in in_labels]
            pie_in_ax.pie(in_values, labels=in_labels, autopct='%1.0f%%', startangle=140, colors=in_colors)
            pie_in_ax.set_title('Komposisi Barang Masuk Hari Ini', fontsize=12)
        else:
            pie_in_ax.text(0.5, 0.5, 'Tidak ada transaksi IN hari ini', ha='center', va='center', fontsize=11)
            pie_in_ax.set_title('Komposisi Barang Masuk Hari Ini', fontsize=12)
        self.pie_in_canvas.draw()
        
        # Pie chart OUT
        pie_out_ax = self.pie_out_canvas.figure.subplots()
        pie_out_ax.clear()
        if out_values and sum(out_values) > 0:
            # Gunakan warna yang sesuai dengan kategori
            out_colors = [category_colors.get(label, '#9E9E9E') for label in out_labels]
            pie_out_ax.pie(out_values, labels=out_labels, autopct='%1.0f%%', startangle=140, colors=out_colors)
            pie_out_ax.set_title('Komposisi Barang Keluar Hari Ini', fontsize=12)
        else:
            pie_out_ax.text(0.5, 0.5, 'Tidak ada transaksi OUT hari ini', ha='center', va='center', fontsize=11)
            pie_out_ax.set_title('Komposisi Barang Keluar Hari Ini', fontsize=12)
        self.pie_out_canvas.draw()
        
        # Bar chart IN
        bar_in_ax = self.bar_in_canvas.figure.subplots()
        bar_in_ax.clear()
        if in_values and sum(in_values) > 0:
            # Gunakan warna yang sesuai dengan kategori
            in_bar_colors = [category_colors.get(label, '#9E9E9E') for label in in_labels]
            bars = bar_in_ax.bar(in_labels, in_values, color=in_bar_colors)
            bar_in_ax.set_ylabel('Qty')
            bar_in_ax.set_title('Qty Barang Masuk per Kategori', fontsize=12)
            bar_in_ax.tick_params(axis='x', rotation=15)
        else:
            bar_in_ax.text(0.5, 0.5, 'Tidak ada transaksi IN hari ini', ha='center', va='center', fontsize=11)
            bar_in_ax.set_title('Qty Barang Masuk per Kategori', fontsize=12)
        self.bar_in_canvas.draw()
        
        # Bar chart OUT
        bar_out_ax = self.bar_out_canvas.figure.subplots()
        bar_out_ax.clear()
        if out_values and sum(out_values) > 0:
            # Gunakan warna yang sesuai dengan kategori
            out_bar_colors = [category_colors.get(label, '#9E9E9E') for label in out_labels]
            bars = bar_out_ax.bar(out_labels, out_values, color=out_bar_colors)
            bar_out_ax.set_ylabel('Qty')
            bar_out_ax.set_title('Qty Barang Keluar per Kategori', fontsize=12)
            bar_out_ax.tick_params(axis='x', rotation=15)
        else:
            bar_out_ax.text(0.5, 0.5, 'Tidak ada transaksi OUT hari ini', ha='center', va='center', fontsize=11)
            bar_out_ax.set_title('Qty Barang Keluar per Kategori', fontsize=12)
        self.bar_out_canvas.draw()
    
    def apply_theme(self):
        """Apply current theme to dashboard"""
        # Header styling
        self.header_frame.setStyleSheet(f'''
            background: {theme.get_color('card_background')}; 
            border-bottom: 1px solid {theme.get_color('border')};
        ''')
        self.home_icon.setStyleSheet(f'font-size:26px; color:{theme.get_color('accent')}; margin-right:8px;')
        self.header_label.setStyleSheet(f'color: {theme.get_color('text_primary')}; font-weight:bold;')
        
        # Main background
        self.setStyleSheet(f'''
            background: {theme.get_color('background')};
            QFrame[modernCard="true"] {{
                background: {theme.get_color('card_background')}; 
                border: 1px solid {theme.get_color('border')}; 
                border-radius: 18px;
            }}
        ''')
        
        # Update chart colors if matplotlib is available
        if hasattr(self, 'line_canvas') and self.line_canvas:
            self.load_line_chart() 