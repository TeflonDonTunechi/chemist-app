# src/main.py
import sys
from PyQt6.QtWidgets import QApplication
from src.database import init_db
from src.views.main_window import MainWindow
import os

def main():
    init_db()

    app = QApplication(sys.argv)

    style_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'style.qss')
    if os.path.exists(style_path):
        with open(style_path, 'r') as f:
            app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()