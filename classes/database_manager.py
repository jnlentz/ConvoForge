# classes/database_manager.py
import sqlite3
import time

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def _execute(self, query, params=(), fetch=None):
        try:
            con = sqlite3.connect(self.db_path)
            con.execute("PRAGMA foreign_keys = ON")
            cur = con.cursor()
            cur.execute(query, params)
            
            result = None
            if fetch == 'one':
                result = cur.fetchone()
            if fetch == 'all':
                result = cur.fetchall()
            if fetch == 'lastrowid':
                result = cur.lastrowid
            
            con.commit()
            con.close()
            return result
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def init_db(self):
        self._execute("""
            CREATE TABLE IF NOT EXISTS turns (
                id INTEGER PRIMARY KEY,
                conversation_id INTEGER,
                user_prompt TEXT,
                assistant_response TEXT,
                timestamp_utc REAL,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
            )
        """)
        self._execute("""CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY, conversation_id_str TEXT UNIQUE, summary TEXT, source_model TEXT, creation_date REAL)""")

    def delete_conversation(self, conversation_db_id):
        """Deletes a conversation and all of its associated turns manually."""
        try:
            with sqlite3.connect(self.db_path) as con:
                cur = con.cursor()
                cur.execute("DELETE FROM turns WHERE conversation_id = ?", (conversation_db_id,))
                cur.execute("DELETE FROM conversations WHERE id = ?", (conversation_db_id,))
                con.commit()
        except sqlite3.Error as e:
            print(f"Database error during delete: {e}")

    def get_all_conversations(self):
        return self._execute("SELECT id, summary FROM conversations ORDER BY creation_date DESC", fetch='all')

    def get_all_conversations_by_model(self, model_name):
        return self._execute("SELECT id, summary FROM conversations WHERE source_model = ? ORDER BY creation_date DESC", (model_name,), fetch='all')

    def get_distinct_models(self):
        return self._execute("SELECT DISTINCT source_model FROM conversations ORDER BY source_model", fetch='all')

    def get_conversations_by_model(self, model_name):
        return self._execute("SELECT conversation_id_str, summary FROM conversations WHERE source_model = ? ORDER BY creation_date DESC", (model_name,), fetch='all')

    def get_conversation_details(self, conv_id_str):
        return self._execute("SELECT id, summary FROM conversations WHERE conversation_id_str = ?", (conv_id_str,), fetch='one')
    
    def get_conversation_turns(self, conv_db_id):
        return self._execute("SELECT user_prompt, assistant_response FROM turns WHERE conversation_id = ? ORDER BY timestamp_utc ASC", (conv_db_id,), fetch='all')

    def update_conversation_summary(self, conv_id_str, new_summary):
        self._execute("UPDATE conversations SET summary = ? WHERE conversation_id_str = ?", (new_summary, conv_id_str))

    def find_conversation(self, conv_id_str):
        return self._execute("SELECT id FROM conversations WHERE conversation_id_str = ?", (conv_id_str,), fetch='one')

    def create_conversation(self, conv_id_str, summary, model_name):
        return self._execute("INSERT INTO conversations (conversation_id_str, summary, source_model, creation_date) VALUES (?, ?, ?, ?)", (conv_id_str, summary, model_name, time.time()), fetch='lastrowid')

    def save_turn(self, conv_db_id, user_prompt, assistant_response):
        self._execute("INSERT INTO turns (conversation_id, user_prompt, assistant_response, timestamp_utc) VALUES (?, ?, ?, ?)", (conv_db_id, user_prompt, assistant_response, time.time()))

    def get_db_stats(self):
        conv_count = self._execute("SELECT COUNT(*) FROM conversations", fetch='one')[0]
        pair_count = self._execute("SELECT COUNT(*) FROM turns", fetch='one')[0]
        
        total_words = 0
        all_turns = self._execute("SELECT user_prompt, assistant_response FROM turns", fetch='all')
        if all_turns:
            for user_prompt, assistant_response in all_turns:
                total_words += len(user_prompt.split())
                total_words += len(assistant_response.split())
        return conv_count, pair_count, total_words

    def get_next_conversation_num(self, search_pattern):
        results = self._execute("SELECT conversation_id_str FROM conversations WHERE conversation_id_str LIKE ?", (search_pattern,), fetch='all')
        existing_ids = []
        if results:
            for row in results:
                if row and row[0]:
                    parts = row[0].split('-')
                    if len(parts) > 1 and parts[-1].isdigit():
                        existing_ids.append(int(parts[-1]))
        return max(existing_ids) + 1 if existing_ids else 1
