import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSizePolicy, QFrame, QToolButton, QDialog, QLineEdit
from screens.dashboard import DashboardScreen
from screens.list_barang import ListBarangScreen
from screens.menu_in import MenuInScreen
from screens.menu_out import MenuOutScreen
from screens.report import ReportScreen
from screens.report_stock import ReportStockScreen
from database.db import init_db
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect, Qt
from PyQt6.QtGui import QPixmap, QIcon
from utils.floating_window import floating_manager
from screens.login_dialog import LoginDialog
from utils.helpers import get_current_user
from screens.log_aktivitas import LogAktivitasScreen
from screens.manajemen_user import ManajemenUserScreen
from screens.report_custom import ReportCustomScreen
from utils.theme import theme

class Sidebar(QWidget):
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
        self.setFixedWidth(270)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setObjectName('sidebar')
        self.apply_theme()
        outer = QVBoxLayout()
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(0)

        # Kartu utama seperti contoh (sidebar putih dengan sudut membulat)
        card = QFrame()
        card.setObjectName('sidebarCard')
        self.card = card
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(18, 18, 18, 18)
        card_layout.setSpacing(12)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Header profil
        header = QHBoxLayout()
        self.header_layout = header
        avatar = QLabel()
        try:
            # Jangan tampilkan logo MMS di header
            pass
        except Exception:
            pass
        avatar.setFixedSize(1, 1)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_col = QVBoxLayout()
        user = get_current_user()
        name_label = QLabel(user.get('nama') if user else 'User')
        name_label.setStyleSheet('font-weight:600; font-size:15px; color:#2B2B2B;')
        role_label = QLabel('Web developer' if not user or user.get('role') is None else str(user.get('role')).capitalize())
        role_label.setStyleSheet('color:#8A8A8A; font-size:12px;')
        info_col.addWidget(name_label)
        info_col.addWidget(role_label)
        info_col.setSpacing(2)
        header.addWidget(avatar)
        header.addSpacing(8)
        header.addLayout(info_col)
        header.addStretch()
        # Dark mode toggle button
        self.dark_mode_btn = QToolButton()
        self.dark_mode_btn.setText('🌙')
        self.dark_mode_btn.setToolTip('Toggle Dark Mode')
        self.dark_mode_btn.setFixedSize(28, 28)
        self.dark_mode_btn.setObjectName('dark_mode_btn')
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        header.addWidget(self.dark_mode_btn)
        
        # Toggle collapse button (keperluan internal; disembunyikan saat collapsed agar hanya logo terlihat)
        self.toggle_btn = QToolButton()
        self.toggle_btn.setText('⟨')
        self.toggle_btn.setToolTip('Collapse sidebar')
        self.toggle_btn.setFixedSize(28, 28)
        self.toggle_btn.setObjectName('toggle_btn')
        self.toggle_btn.clicked.connect(self.toggle_collapse)
        header.addWidget(self.toggle_btn)
        card_layout.addLayout(header)

        # Kolom pencarian
        search = QLineEdit()
        search.setPlaceholderText('Search...')
        search.setStyleSheet('background:#F7F8FA; border:1px solid #EFEFEF; border-radius:10px; padding:8px 12px;')
        card_layout.addWidget(search)

        # Menu
        self.menu_btns = []              # daftar tombol menu utama (label_btn untuk List Barang termasuk di sini)
        self.menu_widgets = []           # container/widget baris menu (dipakai untuk layout)
        self.menu_icons = []             # simpan ikon string per tombol
        self.menu_labels = []            # simpan label per tombol
        menu_items = [
            ('Dashboard', '🏠', 0),
            ('List Barang', '📦', 1),
            ('Menu IN', '➕', 2),
            ('Menu OUT', '➖', 3),
            ('Report Harian', '📄', 4),
            ('Laporan Akhir', '📊', 5),
        ]
        for label, icon, idx in menu_items:
            if label == 'List Barang':
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(0, 0, 0, 0)
                btn_layout.setSpacing(8)
                label_btn = QPushButton(f'{icon}  {label}')
                label_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                label_btn.clicked.connect(lambda checked, i=idx: self.mainwindow.go_to_page(i))
                self.menu_btns.append(label_btn)
                self.menu_icons.append(icon)
                self.menu_labels.append(label)
                btn_layout.addWidget(label_btn)
                float_btn = QToolButton()
                float_btn.setText('🗔')
                float_btn.setToolTip('Buka Floating Window List Barang')
                float_btn.setFixedSize(32, 32)
                float_btn.setStyleSheet('''
                    QToolButton { background:#F7F8FA; color:#FF2800; border:1px solid #EFEFEF; border-radius:16px; font-size:16px; }
                    QToolButton:hover { background:#FF2800; color:#FFF; }
                ''')
                float_btn.clicked.connect(self.mainwindow.open_list_barang_floating)
                btn_layout.addWidget(float_btn)
                btn_widget.setLayout(btn_layout)
                card_layout.addWidget(btn_widget)
                self.menu_widgets.append(btn_widget)
                # simpan referensi untuk kontrol saat collapsed
                self.list_barang_label_btn = label_btn
                self.list_barang_float_btn = float_btn
            else:
                btn = QPushButton(f'{icon}  {label}')
                btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                btn.clicked.connect(lambda checked, i=idx: self.mainwindow.go_to_page(i))
                self.menu_btns.append(btn)
                self.menu_icons.append(icon)
                self.menu_labels.append(label)
                card_layout.addWidget(btn)
                self.menu_widgets.append(btn)
        # Tambahkan menu Log Aktivitas & Manajemen User jika admin
        if user and user.get('role') == 'admin':
            btn_log = QPushButton('📝  Log Aktivitas')
            btn_log.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn_log.clicked.connect(lambda checked: self.mainwindow.go_to_page(6))
            self.menu_btns.append(btn_log)
            self.menu_icons.append('📝')
            self.menu_labels.append('Log Aktivitas')
            card_layout.addWidget(btn_log)
            self.menu_widgets.append(btn_log)

            btn_user = QPushButton('👤  Manajemen User')
            btn_user.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn_user.clicked.connect(lambda checked: self.mainwindow.go_to_page(7))
            self.menu_btns.append(btn_user)
            self.menu_icons.append('👤')
            self.menu_labels.append('Manajemen User')
            card_layout.addWidget(btn_user)
            self.menu_widgets.append(btn_user)
        # Hapus button Report Custom lama jika ada
        # Tambah ulang menu Report Custom (bisa diakses semua user)
        btn_report_custom = QPushButton('📑  Report Custom')
        btn_report_custom.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_report_custom.clicked.connect(self.mainwindow.open_report_custom)
        self.menu_btns.append(btn_report_custom)
        self.menu_icons.append('📑')
        self.menu_labels.append('Report Custom')
        card_layout.addWidget(btn_report_custom)
        self.menu_widgets.append(btn_report_custom)

        card_layout.addStretch()

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet('color:#F0F0F0;')
        sep.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card_layout.addWidget(sep)
        self.sep = sep

        # Tombol Logout di bawah seperti contoh (tetap fungsi sama)
        btn_logout = QPushButton('Logout')
        btn_logout.setStyleSheet('background:#FFF; color:#FF2800; font-size:15px; border:2px solid #FF2800; border-radius:10px; padding:10px 0; font-weight:bold; text-align:center;')
        btn_logout.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_logout.clicked.connect(self.mainwindow.logout)
        card_layout.addWidget(btn_logout)
        self.btn_logout = btn_logout

        card.setLayout(card_layout)
        outer.addWidget(card)
        self.setLayout(outer)
        self.card = card

        # Set default active pada Dashboard
        self.set_active(0)

        # Collapse state
        self.collapsed = False
        self.avatar_label = avatar
        self.name_label = name_label
        self.role_label = role_label
        # Klik pada logo untuk toggle saat collapsed
        # Logo MMS disembunyikan, tidak perlu click handler
        self.avatar_label.hide()
        self.search_edit = search
        self.apply_collapse_state()

    def set_active(self, page_index: int):
        for i, btn in enumerate(self.menu_btns):
            is_active = (i == page_index)
            btn.setProperty('active', is_active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()

    def toggle_collapse(self):
        self.collapsed = not self.collapsed
        self.apply_collapse_state()

    def apply_collapse_state(self):
        if self.collapsed:
            self.setFixedWidth(96)
            self.toggle_btn.show()
            self.toggle_btn.setText('⟩')
            self.toggle_btn.setToolTip('Maximize sidebar')
            self.header_layout.setSpacing(0)
            self.header_layout.setContentsMargins(0, 0, 0, 0)
            self.name_label.hide()
            self.role_label.hide()
            self.search_edit.hide()
            # tampilkan tombol menu sebagai ikon saja dan center
            for i, btn in enumerate(self.menu_btns):
                btn.setText(self.menu_icons[i])
                btn.setToolTip(self.menu_labels[i])
                btn.setProperty('collapsed', True)
                btn.setStyleSheet('text-align:center; padding:10px 0; font-size:18px;')
                btn.show()
            # sembunyikan tombol float khusus List Barang
            try:
                self.list_barang_float_btn.hide()
            except Exception:
                pass
            self.sep.hide()
            self.btn_logout.hide()
            # Logo MMS disembunyikan
            self.avatar_label.hide()
        else:
            self.setFixedWidth(270)
            self.toggle_btn.show()
            self.toggle_btn.setText('⟨')
            self.toggle_btn.setToolTip('Collapse sidebar')
            self.header_layout.setSpacing(8)
            self.name_label.show()
            self.role_label.show()
            self.search_edit.show()
            # kembalikan tombol menu menjadi ikon + label kiri
            for i, btn in enumerate(self.menu_btns):
                btn.setText(f'{self.menu_icons[i]}  {self.menu_labels[i]}')
                btn.setProperty('collapsed', False)
                btn.setStyleSheet('')
                btn.show()
            try:
                self.list_barang_float_btn.show()
            except Exception:
                pass
            self.sep.show()
            self.btn_logout.show()
            self.avatar_label.hide()

    def apply_theme(self):
        """Apply current theme to sidebar"""
        self.setStyleSheet(theme.get_sidebar_style())
        
    def toggle_dark_mode(self):
        """Toggle between light and dark mode"""
        current_theme = theme.toggle_theme()
        self.apply_theme()
        
        # Update dark mode button icon
        if current_theme == 'dark':
            self.dark_mode_btn.setText('☀️')
            self.dark_mode_btn.setToolTip('Switch to Light Mode')
        else:
            self.dark_mode_btn.setText('🌙')
            self.dark_mode_btn.setToolTip('Switch to Dark Mode')
        
        # Notify main window to update all screens
        if hasattr(self.mainwindow, 'update_all_themes'):
            self.mainwindow.update_all_themes()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Aplikasi Manajemen Stok')
        self.setGeometry(100, 100, 1200, 700)
        # Layout utama
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        # Sidebar
        self.sidebar = Sidebar(self)
        main_layout.addWidget(self.sidebar)
        # Konten (QStackedWidget)
        self.stack = QStackedWidget()
        self.apply_main_theme()
        # Halaman
        self.dashboard = DashboardScreen(self)
        self.list_barang = ListBarangScreen(self)
        self.menu_in = MenuInScreen(self)
        self.menu_out = MenuOutScreen(self)
        self.report = ReportScreen(self)
        self.report_stock = ReportStockScreen(self)
        # Tambah LogAktivitasScreen jika admin
        user = get_current_user()
        if user and user.get('role') == 'admin':
            self.log_aktivitas = LogAktivitasScreen(self)
        else:
            self.log_aktivitas = None
        # Tambah ManajemenUserScreen jika admin
        if user and user.get('role') == 'admin':
            self.manajemen_user = ManajemenUserScreen(self)
        else:
            self.manajemen_user = None
        # Tambah ReportCustomScreen
        self.report_custom = ReportCustomScreen(self)
        self.stack.addWidget(self.dashboard)      # index 0
        self.stack.addWidget(self.list_barang)    # index 1
        self.stack.addWidget(self.menu_in)        # index 2
        self.stack.addWidget(self.menu_out)       # index 3
        self.stack.addWidget(self.report)         # index 4
        self.stack.addWidget(self.report_stock)   # index 5
        self.stack.addWidget(self.log_aktivitas if self.log_aktivitas else QWidget()) # index 6
        self.stack.addWidget(self.manajemen_user if self.manajemen_user else QWidget()) # index 7
        self.stack.addWidget(self.report_custom)  # index 8
        print('Stack widget count:', self.stack.count())
        for i in range(self.stack.count()):
            print('Widget', i, ':', self.stack.widget(i))
        self.stack.setCurrentWidget(self.dashboard)
        main_layout.addWidget(self.stack)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        # Hubungkan sinyal perubahan data dari Menu IN/OUT ke dashboard refresh
        try:
            self.menu_in.data_changed.connect(self.dashboard.refresh_dashboard)
            self.menu_out.data_changed.connect(self.dashboard.refresh_dashboard)
        except Exception:
            pass
        # Hubungkan juga dari List Barang agar perubahan ROP/live update tercermin
        try:
            self.list_barang.data_changed.connect(self.dashboard.refresh_dashboard)
        except Exception:
            pass

    def go_to_page(self, page_index):
        print('go_to_page called:', page_index)
        # Cegah user non-admin buka log aktivitas & manajemen user
        user = get_current_user()
        if (page_index == 6 or page_index == 7) and (not user or user.get('role') != 'admin'):
            return
        if page_index == 8:
            print('Setting stack index to 8')
            self.stack.setCurrentIndex(8)
            print('Current widget after set:', self.stack.currentWidget())
            print('Stack index set to 8')
            try:
                self.sidebar.set_active(len(self.sidebar.menu_btns) - 1)
            except Exception:
                pass
            return
        current_index = self.stack.currentIndex()
        next_widget = self.stack.widget(page_index)
        direction = 1 if page_index > current_index else -1
        # Animasi slide
        curr_widget = self.stack.currentWidget()
        w = self.stack.width()
        h = self.stack.height()
        next_widget.setGeometry(QRect(direction * w, 0, w, h))
        next_widget.show()
        anim_old = QPropertyAnimation(curr_widget, b"geometry")
        anim_old.setDuration(350)
        anim_old.setEasingCurve(QEasingCurve.Type.InOutCubic)
        anim_old.setStartValue(QRect(0, 0, w, h))
        anim_old.setEndValue(QRect(-direction * w, 0, w, h))
        anim_new = QPropertyAnimation(next_widget, b"geometry")
        anim_new.setDuration(350)
        anim_new.setEasingCurve(QEasingCurve.Type.InOutCubic)
        anim_new.setStartValue(QRect(direction * w, 0, w, h))
        anim_new.setEndValue(QRect(0, 0, w, h))
        anim_old.start()
        anim_new.start()
        self.stack.setCurrentIndex(page_index)
        # Update state tombol aktif di sidebar (mapping 0..7 sama; 8 = terakhir)
        try:
            self.sidebar.set_active(page_index)
        except Exception:
            pass

    def create_screen_instance(self, page_index, for_floating=False):
        if page_index == 0:
            from screens.dashboard import DashboardScreen
            return DashboardScreen(self)
        elif page_index == 1:
            from screens.list_barang import ListBarangScreen
            if for_floating:
                return ListBarangScreen(None)
            else:
                return ListBarangScreen(self)
        elif page_index == 2:
            from screens.menu_in import MenuInScreen
            return MenuInScreen(self)
        elif page_index == 3:
            from screens.menu_out import MenuOutScreen
            return MenuOutScreen(self)
        elif page_index == 4:
            from screens.report import ReportScreen
            return ReportScreen(self)
        elif page_index == 5:
            from screens.report_stock import ReportStockScreen
            return ReportStockScreen(self)
        elif page_index == 6:
            from screens.log_aktivitas import LogAktivitasScreen
            return LogAktivitasScreen(self)
        elif page_index == 7:
            from screens.manajemen_user import ManajemenUserScreen
            return ManajemenUserScreen(self)
        elif page_index == 8:
            from screens.report_custom import ReportCustomScreen
            return ReportCustomScreen(self)
        return None

    def open_floating_window(self, page_index, title):
        # Hanya izinkan List Barang (index 1)
        if page_index != 1:
            return
        widget = self.create_screen_instance(page_index, for_floating=True)
        if widget is not None:
            floating_window = floating_manager.create_floating_window(
                f"floating_{page_index}_{id(widget)}",  # unique id
                title,
                widget
            )
            main_pos = self.geometry()
            floating_window.show_floating(
                main_pos.x() + main_pos.width() + 20,
                main_pos.y()
            )

    def open_list_barang_floating(self):
        from screens.list_barang import ListBarangScreen
        from utils.floating_window import floating_manager
        floating_widget = ListBarangScreen(None, floating_mode=True)
        floating_window = floating_manager.create_floating_window(
            f"list_barang_{id(floating_widget)}",
            "List Barang",
            floating_widget
        )
        floating_window.show_floating()

    def open_report_custom(self):
        print('open_report_custom called')
        self.go_to_page(8)

    def logout(self):
        from screens.login_dialog import LoginDialog
        self.close()  # Tutup MainWindow
        login_dialog = LoginDialog()
        if login_dialog.exec() == QDialog.DialogCode.Accepted:
            new_window = MainWindow()
            new_window.show()
    
    def apply_main_theme(self):
        """Apply current theme to main window"""
        self.setStyleSheet(theme.get_main_window_style())
        self.stack.setStyleSheet(f'background: {theme.get_color("background")};')
    
    def update_all_themes(self):
        """Update theme for all screens"""
        self.apply_main_theme()
        
        # Update all screen themes
        screens = [
            self.dashboard,
            self.list_barang,
            self.menu_in,
            self.menu_out,
            self.report,
            self.report_stock,
            self.report_custom
        ]
        
        if self.log_aktivitas:
            screens.append(self.log_aktivitas)
        if self.manajemen_user:
            screens.append(self.manajemen_user)
        
        for screen in screens:
            if hasattr(screen, 'apply_theme'):
                screen.apply_theme()

def main():
    init_db()
    app = QApplication(sys.argv)
    # Login dialog
    login_dialog = LoginDialog()
    if login_dialog.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)
    # Global modern stylesheet
    app.setStyleSheet('''
        QWidget {
            font-family: Segoe UI, Arial, sans-serif;
            font-size: 15px;
        }
        QPushButton {
            background-color: #FF2800;
            color: white;
            padding: 10px 22px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 16px;
            border: none;
        }
        QPushButton:hover {
            background-color: #e02400;
        }
        /* Style khusus untuk tombol di QMessageBox agar selalu tampil */
        QMessageBox QPushButton {
            min-width: 90px;
            padding: 8px 18px;
            font-size: 15px;
            color: #FF2800;
            background: #FFF;
            border: 2px solid #FF2800;
            border-radius: 8px;
        }
        QMessageBox QPushButton:hover {
            background: #FFE3D6;
        }
        QLineEdit, QComboBox, QSpinBox {
            background: #FFF;
            border: 1.5px solid #eee;
            border-radius: 10px;
            padding: 8px 14px;
            font-size: 15px;
        }
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
            border: 1.5px solid #FF2800;
        }
        QGroupBox, QFrame[modernCard="true"] {
            background: #FFF;
            border-radius: 18px;
            padding: 18px 22px;
            border: 1.5px solid #f2f2f2;
        }
        QTableWidget {
            background: #FFF;
            border-radius: 14px;
            border: 1.5px solid #eee;
            font-size: 15px;
            gridline-color: #f2f2f2;
            alternate-background-color: #FAFAFA;
        }
        QHeaderView::section {
            background: #FFF;
            color: #FF2800;
            font-size: 16px;
            font-weight: bold;
            height: 44px;
            border: 1.5px solid #eee;
            border-radius: 10px;
        }
        QTableWidget::item {
            padding: 8px;
        }
        QTableWidget::item:selected {
            background: #FFE3D6;
            color: #FF2800;
        }
        QTableWidget {
            selection-background-color: #FFE3D6;
            selection-color: #FF2800;
        }
    ''')
    window = MainWindow()
    # Tambahkan efek shadow pada card statistik dashboard dan tombol utama sidebar
    try:
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        # Card statistik dashboard
        for card in [window.dashboard.stat_total, window.dashboard.stat_in, window.dashboard.stat_out]:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(18)
            shadow.setOffset(0, 4)
            shadow.setColor(Qt.GlobalColor.gray)
            card.setGraphicsEffect(shadow)
        # Tombol utama sidebar
        for btn in window.sidebar.menu_btns:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(12)
            shadow.setOffset(0, 2)
            shadow.setColor(Qt.GlobalColor.lightGray)
            btn.setGraphicsEffect(shadow)
    except Exception:
        pass
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 