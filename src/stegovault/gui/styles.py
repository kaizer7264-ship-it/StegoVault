"""
Application stylesheet definitions.
Provides the crisp, clean 'Claude Light' aesthetic.
"""

def get_light_theme() -> str:
    return """
    /* Main application background (Clean, soft white) */
    QWidget, QMainWindow {
        background-color: #FDFDFC;
        color: #333333;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Sidebar (Soft light gray) */
    QFrame#Sidebar {
        background-color: #F7F7F5;
        border-right: 1px solid #E5E5E5;
    }

    /* Headings */
    QLabel#TitleLabel {
        font-size: 28px;
        font-weight: 600;
        color: #111111;
    }

    /* Feature Cards */
    QFrame#FeatureCard {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 12px;
        padding: 20px;
    }
    
    QFrame#FeatureCard:hover {
        border: 1px solid #D1D1D1;
    }

    /* Inputs */
    QLineEdit, QComboBox {
        background-color: #FFFFFF;
        border: 1px solid #D1D1D1;
        border-radius: 8px;
        padding: 8px 12px;
    }

    /* Primary Button (Claude Terracotta) */
    QPushButton#PrimaryButton {
        background-color: #D97757;
        color: #FFFFFF;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px;
    }
    
    QPushButton#PrimaryButton:hover {
        background-color: #C66A4D;
    }
    """