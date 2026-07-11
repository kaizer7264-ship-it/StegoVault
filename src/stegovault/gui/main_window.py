"""
Main window module assembling the sidebar and page stack.
"""

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from .sidebar import Sidebar
from .pages import HomePage, HideDataPage, ExtractDataPage, SettingsPage, AboutPage

class StegoVaultMainWindow(QMainWindow):
    """
    The primary application window that holds the sidebar and manages the stacked widget navigation.
    """
    def __init__(self) -> None:
        """Initializes the main window, properties, and layout structure."""
        super().__init__()
        
        self.setWindowTitle("StegoVault v1.0.0")
        self.resize(1300, 850)
        self.setMinimumSize(900, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Configures the UI components and instantiates the page stack."""
        self.sidebar = Sidebar()
        self.stacked_widget = QStackedWidget()
        
        # Instantiate pages
        self.home_page = HomePage()
        self.hide_page = HideDataPage()
        self.extract_page = ExtractDataPage()
        self.settings_page = SettingsPage()
        self.about_page = AboutPage()
        
        # Add pages to stack
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.hide_page)
        self.stacked_widget.addWidget(self.extract_page)
        self.stacked_widget.addWidget(self.settings_page)
        self.stacked_widget.addWidget(self.about_page)
        
        # Add to main layout
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.stacked_widget)
        
        # Connect signals
        self.sidebar.page_requested.connect(self.switch_page)
        
    def switch_page(self, index: int) -> None:
        """
        Switches the visible page in the stacked widget.
        
        Args:
            index (int): The target page index from the sidebar.
        """
        self.stacked_widget.setCurrentIndex(index)