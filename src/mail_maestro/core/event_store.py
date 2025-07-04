import sqlite3
from datetime import datetime

class EventStore:
    def __init__(self, path='events.db'):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS processed (fingerprint TEXT PRIMARY KEY, timestamp DATETIME)"
        )
    def seen(self, fp: str):
        cur = self.conn.execute("SELECT 1 FROM processed WHERE fingerprint=?",(fp,))
        return cur.fetchone() is not None
    def mark(self, fp: str):
        self.conn.execute("INSERT OR IGNORE INTO processed(fingerprint, timestamp) VALUES(?,?)", (fp, datetime.utcnow()))
        self.conn.commit()
