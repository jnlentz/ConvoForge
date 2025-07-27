# classes/data_management_tab.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QTextEdit, QFormLayout, QSpacerItem, QSizePolicy

class DataManagementTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # --- Top controls for filtering and deleting ---
        controls_layout = QFormLayout()

        self.model_filter_combo = QComboBox()
        self.delete_combo = QComboBox()
        self.delete_button = QPushButton("Delete Selected Conversation")

        controls_layout.addRow("Filter by Model:", self.model_filter_combo)
        controls_layout.addRow("Select Conversation:", self.delete_combo)
        controls_layout.addRow(self.delete_button)
        
        main_layout.addLayout(controls_layout)

        # --- Preview Pane ---
        main_layout.addWidget(QLabel("Conversation Preview:"))
        self.preview_pane = QTextEdit()
        self.preview_pane.setReadOnly(True)
        self.preview_pane.setObjectName("PreviewPane")
        main_layout.addWidget(self.preview_pane)
        
        self.setLayout(main_layout)
