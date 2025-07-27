# main.py
# Main entry point for the ConvoForge application.
import sys
from PyQt6.QtWidgets import QApplication

# Local imports
from config import DARK_STYLESHEET
from classes.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
