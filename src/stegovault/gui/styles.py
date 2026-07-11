"""
Stylesheet module for StegoVault.
Provides the modern dark theme inspired by professional desktop applications.
"""

def get_dark_theme() -> str:
    """
    Returns the complete QSS string for the application's dark theme.
    
    Returns:
        str: The Qt Style Sheet definitions.
    """
    return """
    /* Main Window and General Base */
    QMainWindow, QWidget {
        background-color: #1e1e1e;
        color: #cccccc;
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 14px;
    }

    /* Sidebar Navigation */
    #SidebarFrame {
        background-color: #252526;
        border-right: 1px solid #333333;
    }
    
    #SidebarButton {
        background-color: transparent;
        color: #cccccc;
        text-align: left;
        padding: 12px 20px;
        border: none;
        border-radius: 6px;
        margin: 4px 8px;
        font-size: 15px;
        font-weight: 500;
    }
    
    #SidebarButton:hover {
        background-color: #2a2d2e;
        color: #ffffff;
    }
    
    #SidebarButton:checked {
        background-color: #007acc;
        color: #ffffff;
        font-weight: bold;
    }

    /* Typography */
    QLabel {
        background-color: transparent;
    }
    
    #TitleLabel {
        font-size: 28px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 10px;
    }
    
    #SubtitleLabel {
        font-size: 16px;
        color: #9cdcfe;
        margin-bottom: 20px;
    }

    #HeaderLabel {
        font-size: 20px;
        font-weight: 600;
        color: #ffffff;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    /* Feature Cards */
    #FeatureCard {
        background-color: #2d2d30;
        border: 1px solid #3e3e42;
        border-radius: 8px;
        padding: 20px;
    }
    
    #FeatureCard:hover {
        border: 1px solid #007acc;
        background-color: #333337;
    }

    #CardTitle {
        font-size: 16px;
        font-weight: bold;
        color: #569cd6;
    }

    /* Input Controls */
    QLineEdit, QComboBox {
        background-color: #3c3c3c;
        border: 1px solid #3c3c3c;
        border-radius: 4px;
        padding: 8px 12px;
        color: #cccccc;
        selection-background-color: #007acc;
    }
    
    QLineEdit:focus, QComboBox:focus {
        border: 1px solid #007acc;
        background-color: #3c3c3c;
    }

    QComboBox::drop-down {
        border: none;
        padding-right: 10px;
    }

    /* Primary and Secondary Buttons */
    QPushButton {
        background-color: #3c3c3c;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 10px 16px;
        font-weight: 600;
    }
    
    QPushButton:hover {
        background-color: #4a4a4a;
    }
    
    QPushButton:pressed {
        background-color: #2b2b2b;
    }

    #PrimaryButton {
        background-color: #007acc;
        color: #ffffff;
    }
    
    #PrimaryButton:hover {
        background-color: #0098ff;
    }
    
    #PrimaryButton:pressed {
        background-color: #005a9e;
    }

    /* Progress Bar */
    QProgressBar {
        background-color: #3c3c3c;
        border: none;
        border-radius: 4px;
        text-align: center;
        color: #ffffff;
        font-weight: bold;
    }
    
    QProgressBar::chunk {
        background-color: #007acc;
        border-radius: 4px;
    }

    /* Checkboxes */
    QCheckBox {
        spacing: 8px;
        background-color: transparent;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        background-color: #3c3c3c;
        border: 1px solid #3c3c3c;
        border-radius: 4px;
    }
    
    QCheckBox::indicator:checked {
        background-color: #007acc;
        border: 1px solid #007acc;
    }
    """