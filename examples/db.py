
from contextlib import contextmanager
import hashlib
import sqlite3

@contextmanager
def cursor_for(conn, do_commit=False):
    cursor = conn.cursor()
    try:
        if do_commit:
            cursor.execute("BEGIN IMMEDIATE TRANSACTION")

        yield cursor

    except sqlite3.OperationalError as e:
        if do_commit:
            cursor.execute("ROLLBACK")
            print(f"sqlite3 write failed: {e}")

    finally:
        if do_commit:
            conn.commit()

        cursor.close()


class DB:
    def __init__(self, file:str):
        self.conn = None
        self.file = file

    def note_success(self, label: str, src: str, temperature: float, sequence: int, total:int):
        print(f"note success for {label} {temperature} {sequence} {total}")
        h = hashlib.sha256(src.encode()).hexdigest()
        with cursor_for(self.conn, do_commit=True) as cursor:
            cursor.execute("INSERT INTO my_data (label, hash, temperature, sequence, total, success) VALUES (?, ?, ?, ?, ?, ?)", (label, h, temperature, sequence, total, 1))

    def note_failure(self, label:str, temperature: float, total:int):
        print(f"note failure for {label} {temperature} {total}")
        with cursor_for(self.conn, do_commit=True) as cursor:
            cursor.execute("INSERT INTO my_data (label, temperature, sequence, total, success) VALUES (?, ?, NULL, ?, ?)", (label, temperature, total, 0))

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def commit(self):
        self.conn.commit()

    def new(self):
        """ create tables if they don't exist"""
        with cursor_for(self.conn, do_commit=True) as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS my_data (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    label TEXT,
                    hash TEXT,
                    temperature REAL,
                    sequence INTEGER,
                    total INTEGER,
                    success INTEGER
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS label ON my_data (label)
            """)

    def setup(self):
        self.conn = sqlite3.connect(self.file, timeout=10.0)
        self.conn.isolation_level = None
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.conn.execute("PRAGMA journal_size_limit=16777216;")
        self.new()

    def close(self):
        self.conn.close()


