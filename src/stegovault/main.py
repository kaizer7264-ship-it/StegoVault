import sys
from pathlib import Path

# Fix the path to ensure imports work
src_dir = Path(__file__).resolve().parents[1]
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from PySide6.QtWidgets import QApplication  # noqa: E402
from PySide6.QtCore import Qt  # noqa: E402

from stegovault.gui.main_window import StegoVaultMainWindow  # noqa: E402
from stegovault.gui.styles import get_light_theme  # noqa: E402


def main() -> None:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    
    # Force the Palette to Light (This prevents the 'stuck black' issue)
    from PySide6.QtGui import QPalette, QColor
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#FDFDFC"))
    palette.setColor(QPalette.WindowText, QColor("#333333"))
    app.setPalette(palette)

    # Apply the Stylesheet
    app.setStyleSheet(get_light_theme())
    
    window = StegoVaultMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()