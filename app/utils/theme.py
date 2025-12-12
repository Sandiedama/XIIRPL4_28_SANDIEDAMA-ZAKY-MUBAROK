"""
Theme system for the inventory app
Supports light and dark mode with consistent styling
"""

class Theme:
    def __init__(self):
        self.is_dark = False
        self.themes = {
            'light': {
                'background': '#FFF',
                'background_secondary': '#F3F6FB',
                'card_background': '#FFF',
                'text_primary': '#222',
                'text_secondary': '#666',
                'text_muted': '#888',
                'accent': '#FF2800',
                'accent_hover': '#e02400',
                'border': '#EEF1F4',
                'border_focus': '#FF2800',
                'shadow': 'rgba(0, 0, 0, 0.1)',
                'table_header': '#FFF',
                'table_row_even': '#FAFAFA',
                'table_row_odd': '#FFF',
                'table_selection': '#FFE3D6',
                'input_background': '#FFF',
                'button_primary': '#FF2800',
                'button_primary_hover': '#e02400',
                'button_secondary': '#6F42C1',
                'button_secondary_hover': '#5a2d9a',
                'warning_background': '#FFF3E0',
                'warning_border': '#FF9800',
                'success_background': '#E8F5E8',
                'success_border': '#4CAF50',
                'error_background': '#FFEBEE',
                'error_border': '#F44336'
            },
            'dark': {
                'background': '#1a1a1a',
                'background_secondary': '#2d2d2d',
                'card_background': '#2d2d2d',
                'text_primary': '#ffffff',
                'text_secondary': '#b3b3b3',
                'text_muted': '#888888',
                'accent': '#FF2800',
                'accent_hover': '#ff4d33',
                'border': '#404040',
                'border_focus': '#FF2800',
                'shadow': 'rgba(0, 0, 0, 0.3)',
                'table_header': '#2d2d2d',
                'table_row_even': '#333333',
                'table_row_odd': '#2d2d2d',
                'table_selection': '#4a2d2d',
                'input_background': '#333333',
                'button_primary': '#FF2800',
                'button_primary_hover': '#ff4d33',
                'button_secondary': '#6F42C1',
                'button_secondary_hover': '#8a5acf',
                'warning_background': '#4a3a1a',
                'warning_border': '#FF9800',
                'success_background': '#1a3a1a',
                'success_border': '#4CAF50',
                'error_background': '#3a1a1a',
                'error_border': '#F44336'
            }
        }
    
    def get_current_theme(self):
        return 'dark' if self.is_dark else 'light'
    
    def get_color(self, color_name):
        theme = self.get_current_theme()
        return self.themes[theme].get(color_name, '#000000')
    
    def toggle_theme(self):
        self.is_dark = not self.is_dark
        return self.get_current_theme()
    
    def set_theme(self, is_dark):
        self.is_dark = is_dark
    
    def get_sidebar_style(self):
        theme = self.get_current_theme()
        if theme == 'dark':
            return '''
                QWidget#sidebar {
                    background: #2d2d2d;
                    border-right: 1px solid #404040;
                }
                QFrame#sidebarCard {
                    background: #333333;
                    border-radius: 18px;
                    border: 1px solid #404040;
                }
                QLabel {
                    color: #ffffff;
                }
                QLineEdit {
                    background: #333333;
                    color: #ffffff;
                    border: 1px solid #404040;
                    border-radius: 10px;
                    padding: 8px 12px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 1px solid #FF2800;
                }
                QPushButton {
                    background: transparent;
                    color: #b3b3b3;
                    font-size: 16px;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 14px;
                    text-align: left;
                }
                QPushButton:hover {
                    background: #404040;
                }
                QPushButton[active="true"] {
                    background: #FF2800;
                    color: #ffffff;
                }
                QPushButton#btn_logout {
                    background: #FF2800;
                    color: #ffffff;
                    text-align: center;
                    font-weight: 600;
                }
                QPushButton#btn_logout:hover {
                    background: #ff4d33;
                }
                QPushButton#toggle_btn {
                    background: #404040;
                    color: #ffffff;
                    border-radius: 8px;
                    padding: 8px;
                }
                QPushButton#toggle_btn:hover {
                    background: #555555;
                }
            '''
        else:
            return '''
                QWidget#sidebar {
                    background: #F3F6FB;
                    border-right: 1px solid #E0E0E0;
                }
                QFrame#sidebarCard {
                    background: #FFF;
                    border-radius: 18px;
                    border: 1px solid #E0E0E0;
                }
                QLabel {
                    color: #222;
                }
                QLineEdit {
                    background: #FFF;
                    color: #222;
                    border: 1px solid #E0E0E0;
                    border-radius: 10px;
                    padding: 8px 12px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 1px solid #FF2800;
                }
                QPushButton {
                    background: transparent;
                    color: #4A4A4A;
                    font-size: 16px;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 14px;
                    text-align: left;
                }
                QPushButton:hover {
                    background: #FFF3F0;
                }
                QPushButton[active="true"] {
                    background: #FF2800;
                    color: #FFF;
                }
                QPushButton#btn_logout {
                    background: #FF2800;
                    color: #FFF;
                    text-align: center;
                    font-weight: 600;
                }
                QPushButton#btn_logout:hover {
                    background: #e02400;
                }
                QPushButton#toggle_btn {
                    background: #E0E0E0;
                    color: #222;
                    border-radius: 8px;
                    padding: 8px;
                }
                QPushButton#toggle_btn:hover {
                    background: #D0D0D0;
                }
            '''
    
    def get_main_window_style(self):
        theme = self.get_current_theme()
        if theme == 'dark':
            return '''
                QMainWindow {
                    background: #1a1a1a;
                    color: #ffffff;
                }
                QWidget {
                    background: #1a1a1a;
                    color: #ffffff;
                    font-family: Segoe UI, Arial, sans-serif;
                }
            '''
        else:
            return '''
                QMainWindow {
                    background: #FFF;
                    color: #222;
                }
                QWidget {
                    background: #FFF;
                    color: #222;
                    font-family: Segoe UI, Arial, sans-serif;
                }
            '''
    
    def get_card_style(self):
        theme = self.get_current_theme()
        if theme == 'dark':
            return 'background: #2d2d2d; border-radius: 16px; border: 1px solid #404040; padding: 16px;'
        else:
            return 'background: #FFF; border-radius: 16px; border: 1px solid #EEF1F4; padding: 16px;'
    
    def get_table_style(self):
        theme = self.get_current_theme()
        if theme == 'dark':
            return '''
                QTableWidget { 
                    font-size: 15px; 
                    background: #2d2d2d; 
                    border-radius: 14px; 
                    border: 1px solid #404040; 
                    gridline-color: #404040; 
                    color: #ffffff;
                }
                QTableWidget::item { 
                    padding: 8px; 
                    border-bottom: 1px solid #404040;
                }
                QTableWidget::item:selected { 
                    background: #4a2d2d; 
                    color: #ffffff; 
                }
                QTableWidget::item:alternate { 
                    background: #333333; 
                }
                QHeaderView::section { 
                    background: #2d2d2d; 
                    color: #FF2800; 
                    font-size: 15px; 
                    font-weight: 600; 
                    height: 40px; 
                    border: 1px solid #404040; 
                    border-radius: 8px; 
                }
            '''
        else:
            return '''
                QTableWidget { 
                    font-size: 15px; 
                    background: #FFF; 
                    border-radius: 14px; 
                    border: 1px solid #EEF1F4; 
                    gridline-color: #F0F3F6; 
                    color: #222;
                }
                QTableWidget::item { 
                    padding: 8px; 
                }
                QTableWidget::item:selected { 
                    background: #FFE3D6; 
                    color: #222; 
                }
                QTableWidget::item:alternate { 
                    background: #FAFAFA; 
                }
                QHeaderView::section { 
                    background: #FFF; 
                    color: #FF2800; 
                    font-size: 15px; 
                    font-weight: 600; 
                    height: 40px; 
                    border: 1px solid #EEF1F4; 
                    border-radius: 8px; 
                }
            '''
    
    def get_input_style(self):
        theme = self.get_current_theme()
        if theme == 'dark':
            return '''
                QLineEdit, QComboBox, QSpinBox, QDateEdit { 
                    font-size: 15px; 
                    padding: 10px 12px; 
                    border-radius: 10px; 
                    border: 1px solid #404040; 
                    background: #333333;
                    color: #ffffff;
                }
                QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus { 
                    border: 1px solid #FF2800; 
                }
            '''
        else:
            return '''
                QLineEdit, QComboBox, QSpinBox, QDateEdit { 
                    font-size: 15px; 
                    padding: 10px 12px; 
                    border-radius: 10px; 
                    border: 1px solid #EEF1F4; 
                    background: #FFF;
                    color: #222;
                }
                QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus { 
                    border: 1px solid #FF2800; 
                }
            '''
    
    def get_button_style(self, button_type='primary'):
        theme = self.get_current_theme()
        if button_type == 'primary':
            if theme == 'dark':
                return '''
                    QPushButton { 
                        background: #FF2800; 
                        color: #ffffff; 
                        font-size: 16px; 
                        padding: 12px 24px; 
                        border-radius: 10px; 
                        font-weight: 600; 
                    }
                    QPushButton:hover { 
                        background: #ff4d33; 
                    }
                '''
            else:
                return '''
                    QPushButton { 
                        background: #FF2800; 
                        color: #FFF; 
                        font-size: 16px; 
                        padding: 12px 24px; 
                        border-radius: 10px; 
                        font-weight: 600; 
                    }
                    QPushButton:hover { 
                        background: #e02400; 
                    }
                '''
        elif button_type == 'secondary':
            if theme == 'dark':
                return '''
                    QPushButton { 
                        background: #6F42C1; 
                        color: #ffffff; 
                        font-size: 16px; 
                        padding: 12px 24px; 
                        border-radius: 10px; 
                        font-weight: 600; 
                    }
                    QPushButton:hover { 
                        background: #8a5acf; 
                    }
                '''
            else:
                return '''
                    QPushButton { 
                        background: #6F42C1; 
                        color: #FFF; 
                        font-size: 16px; 
                        padding: 12px 24px; 
                        border-radius: 10px; 
                        font-weight: 600; 
                    }
                    QPushButton:hover { 
                        background: #5a2d9a; 
                    }
                '''

# Global theme instance
theme = Theme()
