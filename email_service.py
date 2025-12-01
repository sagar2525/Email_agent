import sqlite3
import json
import pandas as pd

class EmailService:
    def __init__(self, db_name="pro_agent.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY,
                thread_id TEXT,
                sender TEXT,
                subject TEXT,
                body TEXT,
                timestamp TEXT,
                category TEXT DEFAULT 'Unprocessed',
                priority TEXT DEFAULT 'Low',
                action_items TEXT DEFAULT '[]'
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompts (key TEXT PRIMARY KEY, value TEXT)
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER,
                draft_body TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def load_mock_data(self, json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM emails") # Reset for demo
            for email in data:
                cursor.execute('''
                    INSERT INTO emails (id, thread_id, sender, subject, body, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (email['id'], email['thread_id'], email['sender'], email['subject'], email['body'], email['timestamp']))
            self.conn.commit()

    def get_all_emails(self):
        return pd.read_sql("SELECT * FROM emails", self.conn)

    def get_thread(self, thread_id):
        return pd.read_sql("SELECT * FROM emails WHERE thread_id = ?", self.conn, params=(thread_id,))

    def bulk_update_emails(self, results_list):
        """Efficient bulk update transaction"""
        cursor = self.conn.cursor()
        for res in results_list:
            cursor.execute('''
                UPDATE emails 
                SET category = ?, priority = ?, action_items = ? 
                WHERE id = ?
            ''', (res['category'], res['priority'], json.dumps(res['action_items']), res['id']))
        self.conn.commit()

    # ... (Keep get_prompt, save_prompt, save_draft from previous version) ...
    def save_prompt(self, key, value):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO prompts (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()

    def get_prompt(self, key, default=""):
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM prompts WHERE key = ?", (key,))
        res = cursor.fetchone()
        return res[0] if res else default
    
    def save_draft(self, email_id, draft_body):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO drafts (email_id, draft_body) VALUES (?, ?)", (email_id, draft_body))
        self.conn.commit()
    
    def get_stats(self):
        """Analytics Query"""
        df = pd.read_sql("SELECT category, priority, COUNT(*) as count FROM emails GROUP BY category, priority", self.conn)
        return df