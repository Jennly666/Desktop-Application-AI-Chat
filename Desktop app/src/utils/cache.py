import sqlite3
import json
from datetime import datetime
import threading


class ChatCache:
    """
    Класс для кэширования истории чата в SQLite.
    """
    
    def __init__(self):
        self.db_name = 'chat_cache.db'
        
        self.local = threading.local()
        
        self.create_tables()

    def get_connection(self):
        if not hasattr(self.local, 'connection'):
            self.local.connection = sqlite3.connect(self.db_name)
        return self.local.connection

    def create_tables(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT,
                user_message TEXT,
                ai_response TEXT,
                timestamp DATETIME,
                tokens_used INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                model TEXT,
                message_length INTEGER,
                response_time FLOAT,
                tokens_used INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auth (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                api_key TEXT NOT NULL,
                pin TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()

    # ---------- Сообщения чата ----------

    def save_message(self, model, user_message, ai_response, tokens_used):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (model, user_message, ai_response, timestamp, tokens_used)
            VALUES (?, ?, ?, ?, ?)
        ''', (model, user_message, ai_response, datetime.now(), tokens_used))
        conn.commit()

    def get_chat_history(self, limit=50):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM messages 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()

    def clear_history(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM messages')
        conn.commit()

    def get_formatted_history(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                id,
                model,
                user_message,
                ai_response,
                timestamp,
                tokens_used
            FROM messages 
            ORDER BY timestamp ASC
        ''')
        
        history = []
        for row in cursor.fetchall():
            history.append({
                "id": row[0],
                "model": row[1],
                "user_message": row[2],
                "ai_response": row[3],
                "timestamp": row[4],
                "tokens_used": row[5]
            })
        return history

    # ---------- Аналитика ----------

    def save_analytics(self, timestamp, model, message_length, response_time, tokens_used):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analytics_messages 
            (timestamp, model, message_length, response_time, tokens_used)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, model, message_length, response_time, tokens_used))
        conn.commit()

    def get_analytics_history(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, model, message_length, response_time, tokens_used
            FROM analytics_messages
            ORDER BY timestamp ASC
        ''')
        return cursor.fetchall()

    # ---------- Авторизация ----------

    def save_auth(self, api_key: str, pin: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT OR REPLACE INTO auth (id, api_key, pin)
            VALUES (1, ?, ?)
            ''',
            (api_key, pin),
        )
        conn.commit()

    def get_auth(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT api_key, pin FROM auth WHERE id = 1')
        row = cursor.fetchone()
        if not row:
            return None
        return {"api_key": row[0], "pin": row[1]}

    def clear_auth(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM auth WHERE id = 1')
        conn.commit()

    # ---------- Деструктор ----------

    def __del__(self):
        if hasattr(self.local, 'connection'):
            self.local.connection.close()
