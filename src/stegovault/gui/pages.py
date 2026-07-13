"""
Application pages module containing individual screen views for the stacked widget.
Wired to the StegoVault backend services for full end-to-end functionality.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QLineEdit, QComboBox, QProgressBar, 
    QCheckBox, QSpacerItem, QSizePolicy, QFormLayout, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt

# Backend Imports
from stegovault.services.stego_service import StegoService
from stegovault.core.capacity import ImageCapacity
from stegovault.utils.exceptions import SteganographyError, CryptoError


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
        
        status_desc = QLabel("Crypto and LSB engines initialized. Ready for operation.")
        self.main_layout.addWidget(status_desc)
        
        self.main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


class HideDataPage(BasePage):
    """Page dedicated to concealing payloads within carrier images."""
    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        title = QLabel("Hide Data")
        title.setObjectName("TitleLabel")
        self.main_layout.addWidget(title)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        
        # Image Selection
        self.img_path = QLineEdit()
        self.img_path.setPlaceholderText("Select a carrier image (*.png)...")
        self.img_path.setReadOnly(True)
        self.img_btn = QPushButton("Browse Image")
        
        img_layout = QHBoxLayout()
        img_layout.addWidget(self.img_path)
        img_layout.addWidget(self.img_btn)
        form_layout.addRow("Carrier Image:", img_layout)
        
        # Payload Type Selection
        self.payload_type = QComboBox()
        self.payload_type.addItems(["Text Message", "Single File"])
        form_layout.addRow("Payload Type:", self.payload_type)
        
        # Payload Input
        self.payload_path = QLineEdit()
        self.payload_path.setPlaceholderText("Type your secret message here...")
        self.payload_btn = QPushButton("Browse Payload")
        self.payload_btn.setVisible(False) # Hidden by default for Text mode
        
        payload_layout = QHBoxLayout()
        payload_layout.addWidget(self.payload_path)
        payload_layout.addWidget(self.payload_btn)
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
        self.capacity_label = QLabel("Estimated Capacity: Awaiting Image")
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

    def _connect_signals(self) -> None:
        """Binds UI buttons to their respective controller methods."""
        self.img_btn.clicked.connect(self._browse_image)
        self.payload_btn.clicked.connect(self._browse_payload)
        self.payload_type.currentIndexChanged.connect(self._toggle_payload_mode)
        self.hide_btn.clicked.connect(self._execute_hide)
        self.reset_btn.clicked.connect(self._reset_form)
        self.encrypt_check.stateChanged.connect(self._toggle_encryption)

    def _toggle_payload_mode(self, index: int) -> None:
        """Adjusts the UI based on whether Text or File is selected."""
        self.payload_path.clear()
        if index == 0:  # Text Mode
            self.payload_path.setReadOnly(False)
            self.payload_path.setPlaceholderText("Type your secret message here...")
            self.payload_btn.setVisible(False)
        else:           # File Mode
            self.payload_path.setReadOnly(True)
            self.payload_path.setPlaceholderText("Select a file to hide...")
            self.payload_btn.setVisible(True)

    def _toggle_encryption(self, state: int) -> None:
        """Enables or disables the password field based on the checkbox."""
        self.password.setEnabled(self.encrypt_check.isChecked())

    def _browse_image(self) -> None:
        """Opens a file dialog to select the carrier PNG image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Carrier Image", "", "PNG Images (*.png)"
        )
        if file_path:
            self.img_path.setText(file_path)
            self._update_capacity()

    def _browse_payload(self) -> None:
        """Opens a file dialog to select the payload file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Payload File", "", "All Files (*.*)"
        )
        if file_path:
            self.payload_path.setText(file_path)

    def _update_capacity(self) -> None:
        """Updates the capacity label dynamically when an image is loaded."""
        if not self.img_path.text():
            return
            
        try:
            info = ImageCapacity.calculate(self.img_path.text())
            self.capacity_label.setText(f"Estimated Capacity: {info.formatted}")
        except Exception:
            self.capacity_label.setText("Estimated Capacity: Error reading image.")

    def _execute_hide(self) -> None:
        """Validates inputs and calls the backend StegoService to hide data."""
        carrier = self.img_path.text()
        payload_data = self.payload_path.text()
        is_text = self.payload_type.currentIndex() == 0
        encrypt = self.encrypt_check.isChecked()
        pwd = self.password.text()

        if not carrier:
            QMessageBox.warning(self, "Validation Error", "Please select a carrier image.")
            return
        if not payload_data:
            QMessageBox.warning(self, "Validation Error", "Please provide payload data.")
            return
        if encrypt and not pwd:
            QMessageBox.warning(self, "Validation Error", "Please enter an encryption password.")
            return

        # Prompt user for where to save the final Stego Image
        output_image, _ = QFileDialog.getSaveFileName(
            self, "Save Stego Image As", "", "PNG Images (*.png)"
        )
        if not output_image:
            return

        self.status_label.setText("Processing... Please wait.")
        self.progress_bar.setValue(50)
        self.repaint()  # Force UI update before heavy lifting

        try:
            if is_text:
                msg = StegoService.hide_text(carrier, payload_data, output_image, encrypt, pwd)
            else:
                msg = StegoService.hide_file(carrier, payload_data, output_image, encrypt, pwd)
                
            self.progress_bar.setValue(100)
            self.status_label.setText("Operation Complete.")
            QMessageBox.information(self, "Success", msg)
            self._reset_form()
            
        except (SteganographyError, CryptoError, ValueError) as e:
            self.progress_bar.setValue(0)
            self.status_label.setText("Operation Failed.")
            QMessageBox.critical(self, "Error", str(e))
        except Exception as e:
            self.progress_bar.setValue(0)
            self.status_label.setText("Critical Error.")
            QMessageBox.critical(self, "Critical Error", f"An unexpected error occurred:\n{e}")

    def _reset_form(self) -> None:
        """Clears all form inputs."""
        self.img_path.clear()
        self.payload_path.clear()
        self.password.clear()
        self.progress_bar.setValue(0)
        self.capacity_label.setText("Estimated Capacity: Awaiting Image")
        self.status_label.setText("Ready.")
        if self.payload_type.currentIndex() == 0:
            self.payload_path.setPlaceholderText("Type your secret message here...")
        else:
            self.payload_path.setPlaceholderText("Select a file to hide...")


class ExtractDataPage(BasePage):
    """Page dedicated to extracting concealed payloads from carrier images."""
    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        title = QLabel("Extract Data")
        title.setObjectName("TitleLabel")
        self.main_layout.addWidget(title)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        
        self.img_path = QLineEdit()
        self.img_path.setPlaceholderText("Select a carrier image containing hidden data...")
        self.img_path.setReadOnly(True)
        self.img_btn = QPushButton("Browse Image")
        
        img_layout = QHBoxLayout()
        img_layout.addWidget(self.img_path)
        img_layout.addWidget(self.img_btn)
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
        self.extract_btn = QPushButton("Extract Data")
        self.extract_btn.setObjectName("PrimaryButton")
        self.extract_btn.setMinimumHeight(45)
        
        btn_layout.addWidget(self.extract_btn)
        
        self.main_layout.addLayout(btn_layout)
        self.main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def _connect_signals(self) -> None:
        self.img_btn.clicked.connect(self._browse_image)
        self.extract_btn.clicked.connect(self._execute_extract)

    def _browse_image(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Stego Image", "", "PNG Images (*.png)"
        )
        if file_path:
            self.img_path.setText(file_path)
            self.status_label.setText("Image loaded. Ready for extraction.")

    def _execute_extract(self) -> None:
        carrier = self.img_path.text()
        pwd = self.password.text()

        if not carrier:
            QMessageBox.warning(self, "Validation Error", "Please select an image to extract from.")
            return

        # Ask user where to save potential files
        out_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory for Extracted Files")
        if not out_dir:
            return  # User cancelled

        self.status_label.setText("Extracting... Please wait.")
        self.progress_bar.setValue(50)
        self.repaint()

        try:
            result = StegoService.extract(carrier, out_dir, pwd)
            self.progress_bar.setValue(100)
            self.status_label.setText("Extraction Complete.")
            
            # If the result is just text (no file was saved), show it in the prompt
            if not result.startswith("File extracted successfully"):
                QMessageBox.information(self, "Extracted Secret Text", f"Hidden Message:\n\n{result}")
            else:
                QMessageBox.information(self, "Success", result)
                
            self.password.clear()
            
        except (SteganographyError, CryptoError) as e:
            self.progress_bar.setValue(0)
            self.status_label.setText("Extraction Failed.")
            QMessageBox.critical(self, "Extraction Error", str(e))
        except Exception as e:
            self.progress_bar.setValue(0)
            self.status_label.setText("Critical Error.")
            QMessageBox.critical(self, "Critical Error", f"An unexpected error occurred:\n{e}")


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