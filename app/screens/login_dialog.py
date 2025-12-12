from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
from database.db import get_connection
from utils.helpers import set_current_user
import os

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Login User')
        self.setModal(True)
        self.setMinimumWidth(480)
        self.setStyleSheet('''
            /* Background gradient */
            QDialog { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff, stop:1 #fff3f0);
            }
            QFrame#Card {
                /* Glassy card */
                background: rgba(255,255,255,0.78);
                border-radius: 18px;
                border: 1px solid rgba(255,255,255,0.7);
                padding: 32px 36px 24px 36px;
            }
            QLabel#Title {
                font-size: 28px;
                font-weight: bold;
                color: #1F2937; /* neutral dark, not red */
                margin-bottom: 8px;
            }
            QLabel#Subtitle {
                font-size: 15px;
                color: #888;
                margin-bottom: 18px;
            }
            QLineEdit {
                font-size: 16px;
                padding: 12px 14px;
                border-radius: 10px;
                border: 1.5px solid #eee;
                margin-bottom: 12px;
            }
            QLineEdit:focus {
                border: 1.5px solid #FF2800;
                box-shadow: 0 0 0 3px rgba(255,40,0,0.12);
            }
            QPushButton#LoginBtn {
                /* Glossy button */
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6a46, stop:0.45 #ff3b1a, stop:0.55 #ff2e08, stop:1 #ff2800);
                color: #FFF;
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
                padding: 12px 0;
                margin-top: 8px;
                border: none;
                border-top: 1px solid rgba(255,255,255,0.35);
                border-bottom: 2px solid #bf1e00;
            }
            QPushButton#LoginBtn:hover { background: #e53a16; }
            QPushButton#LoginBtn:pressed {
                background: #c81f00;
            }
            QLabel#Version {
                font-size: 12px;
                color: #aaa;
                margin-top: 18px;
            }
            QLabel.InputIcon {
                min-width: 28px;
                color: #FF2800;
                font-size: 18px;
            }
        ''')
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 32, 0, 18)
        main_layout.setSpacing(0)
        # Center content vertically (add top and bottom stretches)
        try:
            main_layout.insertStretch(0, 1)
        except Exception:
            pass
        # Logo dan judul
        self.logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), '../assets/logo.png')
        if os.path.exists(logo_path):
            self._logo_pixmap = QPixmap(logo_path)
            # Pertahankan rasio aspek, skala ke lebar 260 px secara halus
            self.logo_label.setPixmap(self._logo_pixmap.scaledToWidth(260, Qt.TransformationMode.SmoothTransformation))
            self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self.logo_label.setText('📦')
            self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.logo_label.setStyleSheet('font-size: 54px; color: #FF2800;')
        main_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        # Card
        card = QFrame()
        card.setObjectName('Card')
        card_layout = QVBoxLayout()
        card_layout.setSpacing(8)
        title = QLabel('Welcome to MMS Inventory App')
        title.setObjectName('Title')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)
        subtitle = QLabel('Silakan login untuk melanjutkan')
        subtitle.setObjectName('Subtitle')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(subtitle)
        # Form
        user_row = QHBoxLayout()
        user_icon = QLabel('👤')
        user_icon.setObjectName('')
        user_icon.setProperty('class', 'InputIcon')
        user_icon.setStyleSheet('QLabel { font-size:18px; color:#FF2800; }')
        user_row.addWidget(user_icon)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        user_row.addWidget(self.username_input)
        card_layout.addLayout(user_row)

        pw_row = QHBoxLayout()
        pw_icon = QLabel('🔒')
        pw_icon.setProperty('class', 'InputIcon')
        pw_icon.setStyleSheet('QLabel { font-size:18px; color:#FF2800; }')
        pw_row.addWidget(pw_icon)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText('Password')
        pw_row.addWidget(self.password_input)
        self.show_pw_btn = QPushButton()
        self.show_pw_btn.setCheckable(True)
        self.show_pw_btn.setFixedWidth(56)
        self.show_pw_btn.setStyleSheet('border:none; background:transparent; font-size:14px; color:#FF2800;')
        self.show_pw_btn.setText('👁 Show')
        self.show_pw_btn.clicked.connect(self.toggle_password)
        pw_row.addWidget(self.show_pw_btn)
        card_layout.addLayout(pw_row)
        self.login_btn = QPushButton('Login')
        self.login_btn.setObjectName('LoginBtn')
        self.login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_btn)
        card.setLayout(card_layout)
        main_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        # Info versi
        version = QLabel('v2.0 | PT. Multidaya Mitra Sinergi')
        version.setObjectName('Version')
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(version, alignment=Qt.AlignmentFlag.AlignCenter)
        # Bottom stretch to balance vertical space
        try:
            main_layout.addStretch(1)
        except Exception:
            pass
        self.setLayout(main_layout)
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def resizeEvent(self, event):
        # Rescale logo secara proporsional saat window di-resize
        try:
            if hasattr(self, '_logo_pixmap') and not self._logo_pixmap.isNull():
                max_width = max(200, min(360, self.width() - 180))
                self.logo_label.setPixmap(self._logo_pixmap.scaledToWidth(int(max_width), Qt.TransformationMode.SmoothTransformation))
        except Exception:
            pass
        super().resizeEvent(event)

    def toggle_password(self):
        if self.show_pw_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_pw_btn.setText('🙈 Hide')
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_pw_btn.setText('👁 Show')

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            QMessageBox.warning(self, 'Validasi', 'Username dan password wajib diisi!')
            return
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT id, username, nama, role FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            set_current_user({'id': user[0], 'username': user[1], 'nama': user[2], 'role': user[3]})
            QMessageBox.information(self, 'Selamat Datang', f'Selamat datang, {user[2]}!')
            self.accept()
        else:
            QMessageBox.warning(self, 'Login Gagal', 'Username atau password salah!') 