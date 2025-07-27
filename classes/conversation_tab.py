# classes/conversation_tab.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QFormLayout, QComboBox

class ConversationTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        top_layout = QHBoxLayout()
        metadata_widget = QWidget()
        metadata_layout = QFormLayout(metadata_widget)

        self.model_combo = QComboBox()
        self.model_combo.setEditable(True) # <-- FIX IS HERE
        
        self.conv_combo = QComboBox()
        self.summary_input = QLineEdit()
        self.conv_id_display = QLineEdit()
        self.conv_id_display.setReadOnly(True)
        
        metadata_layout.addRow("Source Model:", self.model_combo)
        metadata_layout.addRow("Conversation:", self.conv_combo)
        metadata_layout.addRow("Conversation ID:", self.conv_id_display)
        metadata_layout.addRow("Summary:", self.summary_input)
        
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        self.autogen_button = QPushButton("Auto-generate ID")
        self.edit_button = QPushButton("Unlock / Edit Metadata")
        self.stats_button = QPushButton("DB Stats")
        self.new_conv_button = QPushButton("New Conversation")
        controls_layout.addWidget(self.autogen_button)
        controls_layout.addWidget(self.edit_button)
        controls_layout.addWidget(self.stats_button)
        controls_layout.addWidget(self.new_conv_button)
        
        top_layout.addWidget(metadata_widget, stretch=3)
        top_layout.addWidget(controls_widget, stretch=1)
        main_layout.addLayout(top_layout)

        content_layout = QHBoxLayout()
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        prompts_layout = QHBoxLayout()
        user_layout = QVBoxLayout()
        user_layout.addWidget(QLabel("User Prompt:"))
        self.user_prompt_input = QTextEdit()
        user_layout.addWidget(self.user_prompt_input)
        
        assistant_layout = QVBoxLayout()
        assistant_layout.addWidget(QLabel("Assistant Response:"))
        self.assistant_response_input = QTextEdit()
        assistant_layout.addWidget(self.assistant_response_input)
        
        prompts_layout.addLayout(user_layout)
        prompts_layout.addLayout(assistant_layout)
        
        self.save_pair_button = QPushButton("Save Pair")
        input_layout.addLayout(prompts_layout)
        input_layout.addWidget(self.save_pair_button)
        
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.addWidget(QLabel("Conversation Preview"))
        self.preview_pane = QTextEdit()
        self.preview_pane.setReadOnly(True)
        self.preview_pane.setObjectName("PreviewPane")
        preview_layout.addWidget(self.preview_pane)
        
        content_layout.addWidget(input_widget, stretch=2)
        content_layout.addWidget(preview_widget, stretch=1)
        main_layout.addLayout(content_layout)