"""
Star Citizen Profile Viewer
Main entry point for the application
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Initialize and run the application"""
    app = QApplication(sys.argv)
    app.setApplicationName("Star Citizen Profile Viewer")
    app.setOrganizationName("SC Tools")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
