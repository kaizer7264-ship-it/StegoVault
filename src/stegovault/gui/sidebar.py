"""
Sidebar component module for application navigation.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PySide6.QtCore import Signal, Qt

class Sidebar(QFrame):
    """
    Vertical sidebar containing navigation buttons to switch between application pages.
    """
    
    page_requested = Signal(int)
    
    def __init__(self) -> None:
        """Initializes the sidebar and configures layout and buttons."""
        super().__init__()
        self.setObjectName("SidebarFrame")
        self.setMinimumWidth(220)
        self.setMaximumWidth(220)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 20, 0, 20)
        self.layout.setSpacing(5)
        
        self._setup_branding()
        self._setup_buttons()
        self._setup_footer()
        
    def _setup_branding(self) -> None:
        """Sets up the application logo and title in the sidebar."""
        branding_layout = QVBoxLayout()
        branding_layout.setContentsMargins(20, 0, 20, 30)
        
        app_title = QLabel("StegoVault")
        app_title.setObjectName("HeaderLabel")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        branding_layout.addWidget(app_title)
        self.layout.addLayout(branding_layout)
        
    def _setup_buttons(self) -> None:
        """Creates and configures the navigation buttons."""
        self.buttons: list[QPushButton] = []
        
        nav_items = [
            ("🏠 Home", 0),
            ("🔒 Hide Data", 1),
            ("📂 Extract Data", 2),
            ("⚙ Settings", 3),
            ("ℹ About", 4)
        ]
        
        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("SidebarButton")
            btn.setCheckable(True)
            if index == 0:
                btn.setChecked(True)
                
            btn.clicked.connect(lambda checked=False, idx=index: self._on_button_clicked(idx))
            self.buttons.append(btn)
            self.layout.addWidget(btn)
            
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.layout.addItem(spacer)
        
    def _setup_footer(self) -> None:
        """Sets up the footer information in the sidebar."""
        version_label = QLabel("v1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #666666; font-size: 12px;")
        self.layout.addWidget(version_label)
        
    def _on_button_clicked(self, index: int) -> None:
        """
        Handles click events for navigation buttons, updating their active state.
        
        Args:
            index (int): The index of the requested page.
        """
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
        self.page_requested.emit(index)