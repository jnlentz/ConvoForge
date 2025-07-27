# classes/main_window.py
import markdown
import torch
import gc
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QApplication, QMessageBox

# Local imports
from config import DATABASE_PATH, BASE_MODEL_ID, ADAPTER_MODELS
from .database_manager import DatabaseManager
from .inference_workers import ModelLoaderThread, InferenceThread
from .conversation_tab import ConversationTab
from .chat_tab import ChatTab
from .data_management_tab import DataManagementTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ConvoForge")
        self.setGeometry(100, 100, 1400, 850)

        # Initialize backend and state
        self.db = DatabaseManager(DATABASE_PATH)
        self.chat_model = None
        self.chat_tokenizer = None
        self.chat_history = []
        self.current_chat_conv_db_id = None
        self.is_metadata_locked = False

        self.tabs = QTabWidget()
        self.chat_tab = ChatTab()
        self.conv_tab = ConversationTab()
        self.mgmt_tab = DataManagementTab()
        
        self.tabs.addTab(self.chat_tab, "Chat")
        self.tabs.addTab(self.conv_tab, "Data Collection")
        self.tabs.addTab(self.mgmt_tab, "Data Management")
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.stats_label = QLabel("Click 'DB Stats' to see totals.")
        self.stats_label.setObjectName("StatsLabel")
        self.status_label = QLabel("Status: Ready.")
        main_layout.addWidget(self.stats_label)
        main_layout.addWidget(self.status_label)
        
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        self.connect_signals()
        self.initialize_ui_state()
        
        self.tabs.setCurrentWidget(self.chat_tab)

    def connect_signals(self):
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Data Collection Tab
        self.conv_tab.model_combo.currentIndexChanged.connect(self.update_conversation_dropdown)
        self.conv_tab.conv_combo.currentIndexChanged.connect(self.load_conversation_data)
        self.conv_tab.autogen_button.clicked.connect(self.autogenerate_id)
        self.conv_tab.edit_button.clicked.connect(self.toggle_edit_mode)
        self.conv_tab.stats_button.clicked.connect(self.calculate_db_stats)
        self.conv_tab.new_conv_button.clicked.connect(self.start_new_conversation)
        self.conv_tab.save_pair_button.clicked.connect(self.save_pair)

        # Chat Tab
        self.chat_tab.load_model_button.clicked.connect(self.load_selected_model)
        self.chat_tab.create_button.clicked.connect(self.create_new_chat_conversation)
        self.chat_tab.conv_combo.currentIndexChanged.connect(self.load_chat_history)
        self.chat_tab.send_button.clicked.connect(self.send_chat_message)
        self.chat_tab.input_line.sendMessage.connect(self.send_chat_message)

        # Data Management Tab
        self.mgmt_tab.model_filter_combo.currentIndexChanged.connect(self.populate_delete_dropdown)
        self.mgmt_tab.delete_combo.currentIndexChanged.connect(self.update_mgmt_preview)
        self.mgmt_tab.delete_button.clicked.connect(self.delete_selected_conversation)

    def on_tab_changed(self, index):
        if self.tabs.widget(index) == self.mgmt_tab:
            self.populate_mgmt_model_filter()

    # --- Data Management Methods ---
    def populate_mgmt_model_filter(self):
        self.mgmt_tab.model_filter_combo.blockSignals(True)
        self.mgmt_tab.model_filter_combo.clear()
        self.mgmt_tab.model_filter_combo.addItem("All Models")
        models = self.db.get_distinct_models()
        if models:
            for row in models:
                self.mgmt_tab.model_filter_combo.addItem(row[0])
        self.mgmt_tab.model_filter_combo.blockSignals(False)
        self.populate_delete_dropdown()

    def populate_delete_dropdown(self):
        self.mgmt_tab.delete_combo.blockSignals(True)
        self.mgmt_tab.delete_combo.clear()
        self.mgmt_tab.delete_combo.addItem("-- Select a conversation to delete --", userData=None)
        selected_model = self.mgmt_tab.model_filter_combo.currentText()
        conversations = []
        if selected_model == "All Models":
            conversations = self.db.get_all_conversations()
        else:
            conversations = self.db.get_all_conversations_by_model(selected_model)
        if conversations:
            for db_id, summary in conversations:
                self.mgmt_tab.delete_combo.addItem(summary, userData=db_id)
        self.mgmt_tab.delete_combo.blockSignals(False)
        self.update_mgmt_preview()

    def delete_selected_conversation(self):
        conv_db_id = self.mgmt_tab.delete_combo.currentData()
        if not conv_db_id:
            self.status_label.setText("Status: No conversation selected to delete.")
            return
        conv_summary = self.mgmt_tab.delete_combo.currentText()
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Are you sure you want to permanently delete this entire conversation?\n\n'{conv_summary}'",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_conversation(conv_db_id)
            self.status_label.setText(f"Status: Deleted conversation '{conv_summary}'.")
            self.populate_delete_dropdown()
            self.populate_models_dropdown()
            if self.chat_model:
                self.populate_chat_conversations()

    def update_mgmt_preview(self):
        conv_db_id = self.mgmt_tab.delete_combo.currentData()
        if not conv_db_id:
            self.mgmt_tab.preview_pane.clear()
            return
        turns = self.db.get_conversation_turns(conv_db_id)
        preview_html = ""
        if turns:
            for user_prompt, assistant_response in turns:
                user_html = markdown.markdown(user_prompt)
                assistant_html = markdown.markdown(assistant_response)
                preview_html += f"<p><b style='color:#D3D3D3;'>User:</b><br>{user_html}</p>"
                preview_html += f"<p><b style='color:#00AACC;'>AI:</b><br>{assistant_html}</p><hr>"
        self.mgmt_tab.preview_pane.setHtml(preview_html)
        self.mgmt_tab.preview_pane.verticalScrollBar().setValue(0)

    # --- Shared & Data Collection Methods ---
    def initialize_ui_state(self):
        self.chat_tab.model_combo.clear()
        self.chat_tab.model_combo.addItem("Base Model", userData={"id": BASE_MODEL_ID, "name": "Base_Model", "adapter": None})
        for model_config in ADAPTER_MODELS:
            self.chat_tab.model_combo.addItem(
                model_config["display_name"], 
                userData={ "id": BASE_MODEL_ID, "name": model_config["clean_name"], "adapter": model_config["path"] }
            )
        self.populate_models_dropdown()
        self.start_new_conversation()

    def populate_models_dropdown(self):
        self.conv_tab.model_combo.blockSignals(True)
        current_model = self.conv_tab.model_combo.currentText()
        self.conv_tab.model_combo.clear()
        self.conv_tab.model_combo.addItem("-- Select Model --")
        models = self.db.get_distinct_models()
        if models:
            for row in models:
                self.conv_tab.model_combo.addItem(row[0])
        if current_model and current_model != self.conv_tab.model_combo.itemText(0):
            self.conv_tab.model_combo.setCurrentText(current_model)
        self.conv_tab.model_combo.blockSignals(False)

    def update_conversation_dropdown(self, index):
        self.conv_tab.conv_combo.blockSignals(True)
        current_conv_id = self.conv_tab.conv_id_display.text()
        self.conv_tab.conv_combo.clear()
        self.conv_tab.conv_combo.addItem("-- Create New or Select Existing --")
        if index > 0:
            model_name = self.conv_tab.model_combo.itemText(index)
            conversations = self.db.get_conversations_by_model(model_name)
            if conversations:
                for conv_id, summary in conversations:
                    self.conv_tab.conv_combo.addItem(summary, userData=conv_id)
        if current_conv_id:
            for i in range(self.conv_tab.conv_combo.count()):
                if self.conv_tab.conv_combo.itemData(i) == current_conv_id:
                    self.conv_tab.conv_combo.setCurrentIndex(i)
                    break
        self.conv_tab.conv_combo.blockSignals(False)
        if not self.conv_tab.conv_combo.currentData():
             self.start_new_conversation(for_new_model=True)
    
    def load_conversation_data(self, index):
        self.conv_tab.edit_button.setText("Unlock / Edit Metadata")
        if index <= 0:
            self.conv_tab.edit_button.setEnabled(False)
            self.conv_tab.preview_pane.clear()
            self.conv_tab.conv_id_display.clear()
            if self.conv_tab.model_combo.currentIndex() > 0:
                 self.lock_metadata(False)
            return
        conv_id_str = self.conv_tab.conv_combo.currentData()
        self.conv_tab.conv_id_display.setText(conv_id_str)
        result = self.db.get_conversation_details(conv_id_str)
        if result:
            conv_db_id, summary = result
            self.conv_tab.summary_input.setText(summary)
            self.lock_metadata(True)
            self.conv_tab.edit_button.setEnabled(True)
            self.update_preview_pane(conv_db_id)
            self.status_label.setText(f"Status: Loaded '{conv_id_str}'.")

    def update_preview_pane(self, conversation_db_id):
        if not conversation_db_id:
            self.conv_tab.preview_pane.clear()
            return
        turns = self.db.get_conversation_turns(conversation_db_id)
        preview_html = ""
        if turns:
            for user_prompt, assistant_response in turns:
                user_html = markdown.markdown(user_prompt)
                assistant_html = markdown.markdown(assistant_response)
                preview_html += f"<p><b style='color:#D3D3D3;'>User:</b><br>{user_html}</p>"
                preview_html += f"<p><b style='color:#00AACC;'>AI:</b><br>{assistant_html}</p><hr>"
        self.conv_tab.preview_pane.setHtml(preview_html)
        self.conv_tab.preview_pane.verticalScrollBar().setValue(self.conv_tab.preview_pane.verticalScrollBar().maximum())

    def lock_metadata(self, lock=True):
        self.conv_tab.summary_input.setReadOnly(lock)
        self.conv_tab.autogen_button.setEnabled(not lock)
        self.is_metadata_locked = lock

    def start_new_conversation(self, for_new_model=False):
        self.lock_metadata(False)
        self.conv_tab.edit_button.setEnabled(False)
        self.conv_tab.edit_button.setText("Unlock / Edit Metadata")
        if not for_new_model:
            self.conv_tab.model_combo.setCurrentIndex(0)
        self.conv_tab.conv_combo.setCurrentIndex(0)
        self.conv_tab.summary_input.clear()
        self.conv_tab.conv_id_display.clear()
        self.conv_tab.user_prompt_input.clear()
        self.conv_tab.assistant_response_input.clear()
        self.conv_tab.preview_pane.clear()
        self.status_label.setText("Status: Ready for new conversation.")
    
    def toggle_edit_mode(self):
        if self.conv_tab.edit_button.text() == "Unlock / Edit Metadata":
            self.conv_tab.summary_input.setReadOnly(False)
            self.conv_tab.edit_button.setText("Save Changes")
            self.status_label.setText("Status: Metadata unlocked. Click 'Save Changes' when done.")
        else:
            self.update_metadata_in_db()

    def update_metadata_in_db(self):
        conv_id_str = self.conv_tab.conv_id_display.text()
        new_summary = self.conv_tab.summary_input.text().strip()
        model_name = self.conv_tab.model_combo.currentText()
        self.db.update_conversation_summary(conv_id_str, new_summary)
        self.conv_tab.summary_input.setReadOnly(True)
        self.conv_tab.edit_button.setText("Unlock / Edit Metadata")
        self.populate_models_dropdown()
        self.conv_tab.model_combo.setCurrentText(model_name)
        self.status_label.setText(f"Status: Successfully updated metadata for '{conv_id_str}'.")

    def autogenerate_id(self):
        # --- FIX: Check currentText instead of currentIndex ---
        model_name = self.conv_tab.model_combo.currentText()
        if not model_name or model_name == "-- Select Model --":
            self.status_label.setText("Status: Enter or select a Source Model before auto-generating.")
            return
        
        search_pattern = f"{model_name.replace(' ', '_')}%"
        next_num = self.db.get_next_conversation_num(search_pattern)
        new_id = f"{model_name.replace(' ', '_')}-{next_num:02}"
        self.conv_tab.conv_id_display.setText(new_id)
        self.status_label.setText(f"Status: Generated ID '{new_id}'. Fill in summary and save first pair.")
    
    def save_pair(self):
        model_name = self.conv_tab.model_combo.currentText()
        conv_id_str = self.conv_tab.conv_id_display.text().strip()
        summary = self.conv_tab.summary_input.text().strip()
        user_prompt = self.conv_tab.user_prompt_input.toPlainText().strip()
        assistant_response = self.conv_tab.assistant_response_input.toPlainText().strip()
        if not all([conv_id_str, summary, user_prompt, assistant_response]) or not model_name or model_name == "-- Select Model --":
            self.status_label.setText("Status: Error - Model, ID, Summary, and both prompts are required.")
            return
        result = self.db.find_conversation(conv_id_str)
        if result:
            conversation_db_id = result[0]
        else:
            conversation_db_id = self.db.create_conversation(conv_id_str, summary, model_name)
            self.conv_tab.conv_id_display.setText(conv_id_str)
            self.populate_models_dropdown()
            self.conv_tab.model_combo.setCurrentText(model_name)
        self.db.save_turn(conversation_db_id, user_prompt, assistant_response)
        self.conv_tab.user_prompt_input.clear()
        self.conv_tab.assistant_response_input.clear()
        if not self.is_metadata_locked:
            self.lock_metadata(True)
            self.conv_tab.edit_button.setEnabled(True)
        self.update_preview_pane(conversation_db_id)
        self.status_label.setText(f"Status: Saved pair to conversation '{conv_id_str}'.")
    
    def calculate_db_stats(self):
        self.status_label.setText("Status: Calculating stats...")
        QApplication.processEvents()
        try:
            conv_count, pair_count, total_words = self.db.get_db_stats()
            self.stats_label.setText(f"Conversations: {conv_count} | Pairs: {pair_count} | Total Words: {total_words:,}")
            self.status_label.setText("Status: Stats calculation complete.")
        except Exception as e:
            self.status_label.setText(f"Status: Database Error - {e}")

    # --- Chat Tab Methods ---
    def unload_model(self):
        if self.chat_model is not None:
            self.chat_tab.status_label.setText("Unloading previous model...")
            QApplication.processEvents()
            del self.chat_model
            del self.chat_tokenizer
            self.chat_model = None
            self.chat_tokenizer = None
            gc.collect()
            torch.cuda.empty_cache()
            self.chat_tab.status_label.setText("Previous model unloaded.")
            QApplication.processEvents()

    def load_selected_model(self):
        self.unload_model()
        model_data = self.chat_tab.model_combo.currentData()
        self.chat_tab.status_label.setText(f"Loading {self.chat_tab.model_combo.currentText()}...")
        self.chat_tab.load_model_button.setEnabled(False)
        self.chat_tab.send_button.setEnabled(False)
        self.model_loader_thread = ModelLoaderThread(model_data["id"], model_data["adapter"])
        self.model_loader_thread.finished.connect(self.on_model_load_finished)
        self.model_loader_thread.error.connect(self.on_model_load_error)
        self.model_loader_thread.start()

    def on_model_load_finished(self, model, tokenizer):
        self.chat_model = model
        self.chat_tokenizer = tokenizer
        self.chat_tab.status_label.setText(f"Loaded: {self.chat_tab.model_combo.currentText()}")
        self.chat_tab.load_model_button.setEnabled(True)
        self.populate_chat_conversations()

    def on_model_load_error(self, error_message):
        self.chat_tab.status_label.setText(f"Error: {error_message}")
        self.chat_tab.load_model_button.setEnabled(True)
    
    def populate_chat_conversations(self):
        self.chat_tab.conv_combo.blockSignals(True)
        self.chat_tab.conv_combo.clear()
        self.chat_tab.conv_combo.addItem("-- Select Existing Chat --", userData=None)
        model_data = self.chat_tab.model_combo.currentData()
        if not model_data: return
        model_name = model_data["name"]
        conversations = self.db.get_conversations_by_model(model_name)
        if conversations:
            for conv_id_str, summary in conversations:
                db_id_result = self.db.get_conversation_details(conv_id_str)
                if db_id_result:
                    self.chat_tab.conv_combo.addItem(summary, userData=db_id_result[0])
        self.chat_tab.conv_combo.blockSignals(False)
        self.start_new_chat()

    def create_new_chat_conversation(self):
        model_data = self.chat_tab.model_combo.currentData()
        if not model_data:
            self.status_label.setText("Status: Load a model first.")
            return
        summary = self.chat_tab.summary_input.text().strip()
        if not summary:
            self.status_label.setText("Status: Please enter a summary to create a new chat.")
            return
        model_name = model_data["name"]
        search_pattern = f"{model_name}-inference-%"
        next_num = self.db.get_next_conversation_num(search_pattern)
        conv_id_str = f"{model_name}-inference-{next_num:02}"
        self.current_chat_conv_db_id = self.db.create_conversation(conv_id_str, summary, model_name)
        self.populate_chat_conversations()
        for i in range(self.chat_tab.conv_combo.count()):
            if self.chat_tab.conv_combo.itemData(i) == self.current_chat_conv_db_id:
                self.chat_tab.conv_combo.setCurrentIndex(i)
                break
        self.populate_models_dropdown()
        self.chat_tab.send_button.setEnabled(True)
        self.status_label.setText(f"Status: Created new chat '{conv_id_str}'. Ready for inference.")
        self.chat_tab.history_display.setHtml(f"<p><i>New chat session '{summary}' started.</i></p>")

    def send_chat_message(self):
        user_text = self.chat_tab.input_line.toPlainText().strip()
        if not user_text or not self.chat_model or self.current_chat_conv_db_id is None:
            return
        user_html = markdown.markdown(user_text)
        self.chat_history.append({"role": "user", "content": user_text})
        self.chat_tab.history_display.append(f"<p><b style='color:#D3D3D3;'>You:</b><br>{user_html}</p>")
        self.chat_tab.input_line.clear()
        self.chat_tab.status_label.setText("AI is thinking...")
        self.chat_tab.send_button.setEnabled(False)
        self.inference_thread = InferenceThread(self.chat_model, self.chat_tokenizer, self.chat_history)
        self.inference_thread.finished.connect(self.on_inference_finished)
        self.inference_thread.error.connect(self.on_inference_error)
        self.inference_thread.start()

    def on_inference_finished(self, response_text):
        self.chat_history.append({"role": "assistant", "content": response_text})
        assistant_html = markdown.markdown(response_text)
        self.chat_tab.history_display.append(f"<p><b style='color:#00AACC;'>AI:</b><br>{assistant_html}</p><hr>")
        user_prompt = self.chat_history[-2]['content']
        self.db.save_turn(self.current_chat_conv_db_id, user_prompt, response_text)
        self.chat_tab.status_label.setText(f"Loaded: {self.chat_tab.model_combo.currentText()}")
        self.chat_tab.send_button.setEnabled(True)

    def on_inference_error(self, error_message):
        self.chat_tab.history_display.append(f"<p><i>Error during generation: {error_message}</i></p>")
        self.chat_tab.status_label.setText(f"Loaded: {self.chat_tab.model_combo.currentText()}")
        self.chat_tab.send_button.setEnabled(True)
        
    def load_chat_history(self, index):
        if index <= 0:
            self.start_new_chat()
            return
        self.current_chat_conv_db_id = self.chat_tab.conv_combo.itemData(index)
        self.chat_history.clear()
        turns = self.db.get_conversation_turns(self.current_chat_conv_db_id)
        history_html = ""
        if turns:
            for user_prompt, assistant_response in turns:
                user_html = markdown.markdown(user_prompt)
                assistant_html = markdown.markdown(assistant_response)
                self.chat_history.append({"role": "user", "content": user_prompt})
                self.chat_history.append({"role": "assistant", "content": assistant_response})
                history_html += f"<p><b style='color:#D3D3D3;'>You:</b><br>{user_html}</p>"
                history_html += f"<p><b style='color:#00AACC;'>AI:</b><br>{assistant_html}</p><hr>"
        self.chat_tab.history_display.setHtml(history_html)
        self.chat_tab.summary_input.setText(self.chat_tab.conv_combo.currentText())
        self.chat_tab.send_button.setEnabled(True)

    def start_new_chat(self):
        self.current_chat_conv_db_id = None
        self.chat_history.clear()
        self.chat_tab.history_display.setHtml("<p><i>Load an existing session or create a new one to begin.</i></p>")
        self.chat_tab.summary_input.clear()
        if self.chat_tab.conv_combo.count() > 0:
            self.chat_tab.conv_combo.setCurrentIndex(0)
        self.chat_tab.send_button.setEnabled(False)