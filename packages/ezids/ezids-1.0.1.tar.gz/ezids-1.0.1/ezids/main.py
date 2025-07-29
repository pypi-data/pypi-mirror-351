from ezids.gui import IDSApp
from PyQt6.QtWidgets import QApplication
import sys

def main():
    app = QApplication(sys.argv)
    window = IDSApp()
    window.show()
    sys.exit(app.exec())
