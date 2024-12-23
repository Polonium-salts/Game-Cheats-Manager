white = """
    QMainWindow {{
        background-color: #ffffff;
        color: #000000;
    }}

    QStatusBar::item {{
        border: none;
    }}

    QMenuBar {{
        background-color: #f5f5f5;
        color: #000000;
        border: none;
        padding: 4px;
    }}

    QMenuBar::item {{
        background-color: transparent;
        padding: 4px 8px;
        border-radius: 4px;
    }}

    QMenuBar::item:selected {{
        background-color: #e5e5e5;
    }}

    QMenu {{
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 4px;
    }}

    QMenu::item {{
        padding: 6px 24px 6px 12px;
        border-radius: 4px;
    }}

    QMenu::item:selected {{
        background-color: #e5e5e5;
    }}

    QStatusBar {{
        background-color: #f5f5f5;
        color: #000000;
        border-top: 1px solid #e0e0e0;
    }}

    QScrollArea {{
        border: none;
        background-color: transparent;
    }}

    QScrollBar:vertical {{
        background-color: #f5f5f5;
        width: 12px;
        margin: 0;
        border-radius: 6px;
    }}

    QScrollBar::handle:vertical {{
        background-color: #c0c0c0;
        min-height: 20px;
        border-radius: 6px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: #a0a0a0;
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
        background: none;
    }}

    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}

    QScrollBar:horizontal {{
        background-color: #f5f5f5;
        height: 12px;
        margin: 0;
        border-radius: 6px;
    }}

    QScrollBar::handle:horizontal {{
        background-color: #4d4d4d;
        min-width: 20px;
        border-radius: 6px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background-color: #5d5d5d;
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
        background: none;
    }}

    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none;
    }}

    QLineEdit {{
        padding: 8px 12px;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        background-color: #ffffff;
        color: #000000;
        selection-background-color: #0078d4;
    }}

    QLineEdit:focus {{
        border: 1px solid #0078d4;
    }}

    QPushButton {{
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        background-color: #0078d4;
        color: white;
    }}

    QPushButton:hover {{
        background-color: #1a86d9;
    }}

    QPushButton:pressed {{
        background-color: #006cbd;
    }}

    QPushButton:disabled {{
        background-color: #f0f0f0;
        color: #a0a0a0;
    }}

    QLabel {{
        color: #000000;
    }}

    QDialog {{
        background-color: #ffffff;
        color: #000000;
    }}

    QMessageBox {{
        background-color: #ffffff;
        color: #000000;
    }}

    QMessageBox QLabel {{
        color: #000000;
    }}

    QMessageBox QPushButton {{
        min-width: 80px;
    }}
"""

black = """
    QMainWindow {{
        background-color: #1f1f1f;
        color: white;
    }}

    QStatusBar::item {{
        border: none;
    }}

    QMenuBar {{
        background-color: #2d2d2d;
        color: white;
        border: none;
        padding: 4px;
    }}

    QMenuBar::item {{
        background-color: transparent;
        padding: 4px 8px;
        border-radius: 4px;
    }}

    QMenuBar::item:selected {{
        background-color: #3d3d3d;
    }}

    QMenu {{
        background-color: #2d2d2d;
        color: white;
        border: 1px solid #3d3d3d;
        border-radius: 4px;
        padding: 4px;
    }}

    QMenu::item {{
        padding: 6px 24px 6px 12px;
        border-radius: 4px;
    }}

    QMenu::item:selected {{
        background-color: #3d3d3d;
    }}

    QStatusBar {{
        background-color: #2d2d2d;
        color: white;
        border-top: 1px solid #3d3d3d;
    }}

    QScrollArea {{
        border: none;
        background-color: transparent;
    }}

    QScrollBar:vertical {{
        background-color: #2d2d2d;
        width: 12px;
        margin: 0;
        border-radius: 6px;
    }}

    QScrollBar::handle:vertical {{
        background-color: #4d4d4d;
        min-height: 20px;
        border-radius: 6px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: #5d5d5d;
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
        background: none;
    }}

    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}

    QScrollBar:horizontal {{
        background-color: #2d2d2d;
        height: 12px;
        margin: 0;
        border-radius: 6px;
    }}

    QScrollBar::handle:horizontal {{
        background-color: #4d4d4d;
        min-width: 20px;
        border-radius: 6px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background-color: #5d5d5d;
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
        background: none;
    }}

    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none;
    }}

    QLineEdit {{
        padding: 8px 12px;
        border: 1px solid #3d3d3d;
        border-radius: 4px;
        background-color: #2d2d2d;
        color: white;
        selection-background-color: #0078d4;
    }}

    QLineEdit:focus {{
        border: 1px solid #0078d4;
    }}

    QPushButton {{
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        background-color: #0078d4;
        color: white;
    }}

    QPushButton:hover {{
        background-color: #1a86d9;
    }}

    QPushButton:pressed {{
        background-color: #006cbd;
    }}

    QPushButton:disabled {{
        background-color: #333333;
        color: #666666;
    }}

    QLabel {{
        color: white;
    }}

    QDialog {{
        background-color: #1f1f1f;
        color: white;
    }}

    QMessageBox {{
        background-color: #1f1f1f;
        color: white;
    }}

    QMessageBox QLabel {{
        color: white;
    }}

    QMessageBox QPushButton {{
        min-width: 80px;
    }}
"""
