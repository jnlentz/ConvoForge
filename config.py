# config.py
# Central configuration for the ConvoForge application.

# --- Paths ---
DATABASE_PATH = "./databases/convoforge_data.db"

# --- Model Configuration ---
BASE_MODEL_ID = "google/gemma-2b-it"

# A list of all your fine-tuned adapters.
# Add new models here as you train them.
# The 'path' should point to the directory containing your adapter_config.json
ADAPTER_MODELS = [
    {
        "display_name": "My Fine-Tuned Model v1.0",
        "path": "./models/My_FineTuned_Model_v1.0-adapter",
        "clean_name": "My_FineTuned_Model_v1.0"
    }
]

# --- UI Configuration ---
DARK_STYLESHEET = """
    QTabWidget::pane { border: 1px solid #555; }
    QTabBar::tab { background-color: #2B2B2B; color: #A9A9A9; padding: 10px 20px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
    QTabBar::tab:selected { background-color: #3C3F41; color: #D3D3D3; }
    QWidget { background-color: #2B2B2B; color: #D3D3D3; font-size: 14px; }
    QMainWindow { background-color: #1E1E1E; }
    QLineEdit, QTextEdit, QComboBox { background-color: #3C3F41; border: 1px solid #555; border-radius: 4px; padding: 5px; color: #BBBBBB; }
    QTextEdit#PreviewPane, QTextEdit#ChatHistory { background-color: #212121; }
    QLineEdit:read-only { background-color: #333333; }
    QPushButton { background-color: #007ACC; color: white; border: none; border-radius: 4px; padding: 8px 12px; }
    QPushButton:hover { background-color: #005A9E; }
    QPushButton:disabled { background-color: #555; }
    QLabel { color: #A9A9A9; }
    QLabel#StatsLabel, QLabel#ChatStatusLabel { color: #00AACC; font-weight: bold; font-size: 13px; }
"""
