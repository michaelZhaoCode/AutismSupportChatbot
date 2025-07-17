import sqlite3

from feedback_data_provider import FeedbackDataProvider

class SQLiteFeedbackDataProvider(FeedbackDataProvider):
    def __init__(self, db_path=None):
        """
        Initialize the SQLiteFeedbackStorage.

        Parameters:
            db_path: Optional path to the SQLite database file. If None, defaults to 'feedback.db'.
        """
        self.db_path = db_path or "feedback.db"
        self.conn = sqlite3.connect(self.db_path)
        self._initialize_db()

    def _initialize_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                feedback TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def add_feedback(self, username: str, feedback: str):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO feedback (username, feedback) VALUES (:username, :feedback)',
            {'username': username, 'feedback': feedback}
        )
        self.conn.commit()

    def retrieve_all_feedback(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT username, feedback FROM feedback')
        rows = cursor.fetchall()
        return [{'username': row[0], 'feedback': row[1]} for row in rows]

    def clear_database(self):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM feedback')
        self.conn.commit()

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()