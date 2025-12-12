from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QFont
import sys

class FloatingWindow(QWidget):
    """
    Floating window yang bisa dibuka bersamaan dengan window utama
    """
    
    def __init__(self, title="Floating Window", content_widget=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        
        # Set ukuran default
        self.resize(800, 600)
        
        # Layout utama
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header dengan title dan tombol close
        header = self.create_header(title)
        layout.addWidget(header)
        
        # Content area
        self.content_area = QFrame()
        self.content_area.setStyleSheet('''
            QFrame {
                background: #FFF;
                border: none;
            }
        ''')
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        if content_widget:
            content_layout.addWidget(content_widget)
        
        self.content_area.setLayout(content_layout)
        layout.addWidget(self.content_area)
        
        self.setLayout(layout)
        
        # Styling
        self.setStyleSheet('''
            QWidget {
                background: #FFF;
                font-family: Segoe UI, Arial, sans-serif;
            }
        ''')
        
        # Tambah shadow effect
        self.add_shadow_effect()
    
    def create_header(self, title):
        """Membuat header dengan title dan tombol close"""
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet('''
            QFrame {
                background: #FF2800;
                border: none;
            }
        ''')
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet('''
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        ''')
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Tombol close
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet('''
            QPushButton {
                background: transparent;
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
                border-radius: 15px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
            }
        ''')
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        header.setLayout(header_layout)
        return header
    
    def add_shadow_effect(self):
        """Menambahkan shadow effect pada window"""
        try:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setOffset(0, 5)
            shadow.setColor(Qt.GlobalColor.black)
            self.setGraphicsEffect(shadow)
        except Exception:
            pass
    
    def set_content(self, widget):
        """Set content widget"""
        # Clear existing content
        layout = self.content_area.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        
        # Add new content
        layout.addWidget(widget)
    
    def show_floating(self, x=None, y=None):
        """Show window dengan posisi yang diatur"""
        if x is not None and y is not None:
            self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()

class FloatingWindowManager:
    """
    Manager untuk mengelola multiple floating windows
    """
    
    def __init__(self):
        self.floating_windows = {}
    
    def create_floating_window(self, window_id, title, content_widget=None):
        """Membuat floating window baru"""
        if window_id in self.floating_windows:
            # Jika sudah ada, focus ke window yang ada
            window = self.floating_windows[window_id]
            window.show_floating()
            return window
        
        # Buat window baru
        window = FloatingWindow(title, content_widget)
        self.floating_windows[window_id] = window
        
        # Connect close event untuk remove dari manager
        window.destroyed.connect(lambda: self.remove_window(window_id))
        
        return window
    
    def remove_window(self, window_id):
        """Remove window dari manager"""
        if window_id in self.floating_windows:
            del self.floating_windows[window_id]
    
    def close_all(self):
        """Close semua floating windows"""
        for window in self.floating_windows.values():
            if window.isVisible():
                window.close()
        self.floating_windows.clear()
    
    def get_window(self, window_id):
        """Get window berdasarkan ID"""
        return self.floating_windows.get(window_id)
    
    def is_window_open(self, window_id):
        """Check apakah window sudah terbuka"""
        return window_id in self.floating_windows and self.floating_windows[window_id].isVisible()

# Global instance
floating_manager = FloatingWindowManager() 