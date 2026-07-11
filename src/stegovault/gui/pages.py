"""
Application pages module containing individual screen views for the stacked widget.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QLineEdit, QComboBox, QProgressBar, 
    QCheckBox, QSpacerItem, QSizePolicy, QFormLayout
)
from PySide6.QtCore import Qt

class BasePage(QWidget):
    """Base class for all application pages providing standard margins."""
    def __init__(self) -> None:
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(20)

class HomePage(BasePage):
    """The landing page displaying welcome information and feature highlights."""
    def __init__(self) -> None:
        super().__init__()
        
        title = QLabel("Welcome to StegoVault")
        title.setObjectName("TitleLabel")
        
        subtitle = QLabel("Secure, cross-platform steganography and encryption toolkit.")
        subtitle.setObjectName("SubtitleLabel")
        
        self.main_layout.addWidget(title)
        self.main_layout.addWidget(subtitle)
        
        # Feature Cards
        grid = QGridLayout()
        grid.setSpacing(20)
        
        features = [
            ("Hide Text", "Embed secret text messages directly into image files securely."),
            ("Hide Files", "Compress and hide entire documents or archives within images."),
            ("AES Encryption", "Secure your payloads with military-grade AES-256 encryption."),
            ("Cross Platform", "Run seamlessly across Windows, macOS, and Linux operating systems.")
        ]
        
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        
        for position, (f_title, f_desc) in zip(positions, features):
            card = QFrame()
            card.setObjectName("FeatureCard")
            card_layout = QVBoxLayout(card)
            
            card_title_lbl = QLabel(f_title)
            card_title_lbl.setObjectName("CardTitle")
            
            card_desc_lbl = QLabel(f_desc)
            card_desc_lbl.setWordWrap(True)
            
            card_layout.addWidget(card_title_lbl)
            card_layout.addWidget(card_desc_lbl)
            grid.addWidget(card, *position)
            
        self.main_layout.addLayout(grid)
        
        # Status Section
        status_header = QLabel("System Status")
        status_header.setObjectName("HeaderLabel")
        self.main_layout.addWidget(status_header)
        
        status_desc = QLabel("Crypto engine initialized. Awaiting user instructions.")
        self.main_layout.addWidget(status_desc)
        
        self.main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

class HideDataPage(BasePage):
    """Page dedicated to concealing payloads within carrier images."""
    def __init__(self) -> None:
        super().__init__()
        
        title = QLabel("Hide Data")
        title.setObjectName("TitleLabel")
        self.main_layout.addWidget(title)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        
        # Image Selection
        self.img_path = QLineEdit()
        self.img_path.setPlaceholderText("Select a carrier image...")
        self.img_path.setReadOnly(True)
        img_btn = QPushButton("Browse Image")
        
        img_layout = QHBoxLayout()
        img_layout.addWidget(self.img_path)
        img_layout.addWidget(img_btn)
        form_layout.addRow("Carrier Image:", img_layout)
        
        # Payload Type Selection
        self.payload_type = QComboBox()
        self.payload_type.addItems(["Text Message", "Single File"])
        form_layout.addRow("Payload Type:", self.payload_type)
        
        # Payload Input
        self.payload_path = QLineEdit()
        self.payload_path.setPlaceholderText("Select payload file or type message...")
        payload_btn = QPushButton("Browse Payload")
        
        payload_layout = QHBoxLayout()
        payload_layout.addWidget(self.payload_path)
        payload_layout.addWidget(payload_btn)
        form_layout.addRow("Payload Data:", payload_layout)
        
        # Security
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter encryption password...")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.encrypt_check = QCheckBox("Enable AES-256 Encryption")
        self.encrypt_check.setChecked(True)
        
        sec_layout = QVBoxLayout()
        sec_layout.addWidget(self.password)
        sec_layout.addWidget(self.encrypt_check)
        form_layout.addRow("Security:", sec_layout)
        
        self.main_layout.addLayout(form_layout)
        
        # Status & Capacity
        self.capacity_label = QLabel("Estimated Capacity: -- / --")
        self.status_label = QLabel("Ready.")
        self.main_layout.addWidget(self.capacity_label)
        self.main_layout.addWidget(self.status_label)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.main_layout.addWidget(self.progress_bar)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("Reset Form")
        self.hide_btn = QPushButton("Execute Hide Operation")
        self.hide_btn.setObjectName("PrimaryButton")
        self.hide_btn.setMinimumHeight(45)
        
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.hide_btn)
        
        self.main_layout.addLayout(btn_layout)
        self.main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

class ExtractDataPage(BasePage):
    """Page dedicated to extracting concealed payloads from carrier images."""
    def __init__(self) -> None:
        super().__init__()
        
        title = QLabel("Extract Data")
        title.setObjectName("TitleLabel")
        self.main_layout.addWidget(title)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        
        self.img_path = QLineEdit()
        self.img_path.setPlaceholderText("Select a carrier image containing hidden data...")
        self.img_path.setReadOnly(True)
        img_btn = QPushButton("Browse Image")
        
        img_layout = QHBoxLayout()
        img_layout.addWidget(self.img_path)
        img_layout.addWidget(img_btn)
        form_layout.addRow("Carrier Image:", img_layout)
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter decryption password (if applicable)...")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Password:", self.password)
        
        self.main_layout.addLayout(form_layout)
        
        self.status_label = QLabel("Awaiting image selection.")
        self.main_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.main_layout.addWidget(self.progress_bar)
        
        btn_layout = QHBoxLayout()
        self.open_folder_btn = QPushButton("Open Output Folder")
        self.extract_btn = QPushButton("Extract Data")
        self.extract_btn.setObjectName("PrimaryButton")
        self.extract_btn.setMinimumHeight(45)
        
        btn_layout.addWidget(self.open_folder_btn)
        btn_layout.addWidget(self.extract_btn)
        
        self.main_layout.addLayout(btn_layout)
        self.main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

class SettingsPage(BasePage):
    """Page for configuring application preferences."""
    def __init__(self) -> None:
        super().__init__()
        
        title = QLabel("Settings")
        title.setObjectName("TitleLabel")
        self.main_layout.addWidget(title)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(25)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark (VS Code)", "Dark (Docker)", "Light (System)"])
        form_layout.addRow("Application Theme:", self.theme_combo)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English (US)", "System Default"])
        form_layout.addRow("Language:", self.lang_combo)
        
        self.out_path = QLineEdit()
        self.out_path.setText("~/StegoVault_Output")
        out_btn = QPushButton("Browse")
        
        out_layout = QHBoxLayout()
        out_layout.addWidget(self.out_path)
        out_layout.addWidget(out_btn)
        form_layout.addRow("Default Output Directory:", out_layout)
        
        self.overwrite_check = QCheckBox("Overwrite existing files without prompting")
        self.logs_check = QCheckBox("Enable detailed diagnostic logging")
        self.logs_check.setChecked(True)
        
        form_layout.addRow("", self.overwrite_check)
        form_layout.addRow("", self.logs_check)
        
        self.main_layout.addLayout(form_layout)
        
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        self.save_btn = QPushButton("Save Configuration")
        self.save_btn.setObjectName("PrimaryButton")
        save_layout.addWidget(self.save_btn)
        
        self.main_layout.addLayout(save_layout)
        self.main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

class AboutPage(BasePage):
    """Page displaying application metadata, developer information, and licensing."""
    def __init__(self) -> None:
        super().__init__()
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        
        title = QLabel("StegoVault")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 36px;")
        
        version = QLabel("Version: v1.0.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("color: #007acc; font-weight: bold; font-size: 16px;")
        
        desc = QLabel("A professional cross-platform toolkit for data concealment and extraction.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        developer = QLabel("Developed by: Open Source Community")
        developer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        license_info = QLabel("License: MIT License")
        license_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        github = QLabel("Repository: github.com/stegovault/stegovault")
        github.setAlignment(Qt.AlignmentFlag.AlignCenter)
        github.setStyleSheet("color: #569cd6;")
        
        layout.addWidget(title)
        layout.addWidget(version)
        layout.addWidget(desc)
        layout.addWidget(developer)
        layout.addWidget(license_info)
        layout.addWidget(github)
        
        self.main_layout.addLayout(layout)