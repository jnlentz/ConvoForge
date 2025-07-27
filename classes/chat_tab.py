# classes/chat_tab.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QComboBox, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal

class ChatInputBox(QTextEdit):
    """A QTextEdit that emits a signal on Enter and adds a newline on Shift+Enter."""
    sendMessage = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if QApplication.keyboardModifiers() == Qt.KeyboardModifier.ShiftModifier:
                super().keyPressEvent(event)
            else:
                self.sendMessage.emit()
        else:
            super().keyPressEvent(event)

class ChatTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        top_bar_layout = QHBoxLayout()
        self.model_combo = QComboBox()
        self.load_model_button = QPushButton("Load Model")
        self.status_label = QLabel("No model loaded.")
        self.status_label.setObjectName("ChatStatusLabel")
        
        top_bar_layout.addWidget(QLabel("Model:"))
        top_bar_layout.addWidget(self.model_combo)
        top_bar_layout.addWidget(self.load_model_button)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.status_label)
        main_layout.addLayout(top_bar_layout)
        
        conv_management_layout = QHBoxLayout()
        self.conv_combo = QComboBox()
        self.summary_input = QLineEdit()
        self.summary_input.setPlaceholderText("Enter summary for new chat here...")
        self.create_button = QPushButton("Create New Chat")
        
        conv_management_layout.addWidget(QLabel("Chat Session:"))
        conv_management_layout.addWidget(self.conv_combo, stretch=1)
        conv_management_layout.addWidget(self.summary_input, stretch=2)
        conv_management_layout.addWidget(self.create_button)
        main_layout.addLayout(conv_management_layout)

        self.history_display = QTextEdit()
        self.history_display.setReadOnly(True)
        self.history_display.setObjectName("ChatHistory")
        main_layout.addWidget(self.history_display)
        
        input_layout = QHBoxLayout()
        self.input_line = ChatInputBox()
        self.input_line.setPlaceholderText("Type your message here... (Enter to send, Shift+Enter for new line)")
        self.input_line.setFixedHeight(100)
        
        self.send_button = QPushButton("Send")
        self.send_button.setEnabled(False)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.send_button)
        main_layout.addLayout(input_layout)
