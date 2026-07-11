"""
Application entry point. Bootstraps the QApplication, applies styles, and launches the main window.
"""

import sys
from pathlib import Path

# 1. Resolve absolute path to the directory containing main.py
# 2. Add it to sys.path so local packages (like 'gui') are instantly recognized
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from gui.main_window import StegoVaultMainWindow
from gui.styles import get_dark_theme

def main() -> None:
    """
    Initializes the Qt application, configures high DPI scaling, sets the modern dark theme,
    and starts the event loop.
    """
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    
    app.setStyleSheet(get_dark_theme())
    
    window = StegoVaultMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()