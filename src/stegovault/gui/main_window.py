"""
Main Application Window.
Coordinates the sidebar navigation and the stacked widget pages.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QPushButton, QFrame, QLabel
)

from .pages import HomePage, HideDataPage, ExtractDataPage, SettingsPage, AboutPage
from .styles import get_light_theme

class StegoVaultMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        
        self.setWindowTitle("StegoVault v1.0.0")
        self.resize(1000, 700)
        
        # Apply the styling
        self.setStyleSheet(get_light_theme())
        
        # Main container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(200)
        # Note: Sidebar color is defined by QFrame#Sidebar in styles.py, 
        # but we ensure layout integrity here.
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)
        
        # Logo/Title
        title = QLabel("StegoVault")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-bottom: 20px; padding-left: 10px;")
        sidebar_layout.addWidget(title)
        
        # Navigation
        self.pages = QStackedWidget()
        
        nav_buttons = [
            ("Home", HomePage),
            ("Hide Data", HideDataPage),
            ("Extract Data", ExtractDataPage),
            ("Settings", SettingsPage),
            ("About", AboutPage)
        ]
        
        for i, (name, page_class) in enumerate(nav_buttons):
            btn = QPushButton(name)
            # Custom style for navigation buttons
            btn.setStyleSheet("""
                QPushButton { 
                    text-align: left; 
                    padding: 12px; 
                    border: none; 
                    color: #555; 
                    background: transparent;
                }
                QPushButton:hover { 
                    background: #EFEFEF; 
                    border-radius: 8px;
                }
            """)
            btn.clicked.connect(lambda checked, index=i: self.pages.setCurrentIndex(index))
            sidebar_layout.addWidget(btn)
            self.pages.addWidget(page_class())
            
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages)