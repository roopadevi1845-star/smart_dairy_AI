import os
import sqlite3

# Automatically use local SQLite database file
DB_PATH = os.path.join(os.getcwd(), "smart_dairy.db")

class CursorProxy:
    """Wraps sqlite3 cursor to mimic mysql.connector and convert %s to ? placeholders."""
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, operation, params=None, multi=False):
        if params:
            # Convert MySQL %s placeholders to SQLite ? placeholders
            operation = operation.replace("%s", "?")
            return self.cursor.execute(operation, params)
        else:
            return self.cursor.execute(operation)

    def executemany(self, operation, seq_params):
        operation = operation.replace("%s", "?")
        return self.cursor.executemany(operation, seq_params)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchmany(self, size=None):
        return self.cursor.fetchmany(size)

    @property
    def lastrowid(self):
        return self.cursor.lastrowid

    @property
    def rowcount(self):
        return self.cursor.rowcount

    def close(self):
        return self.cursor.close()

    def __iter__(self):
        return iter(self.cursor)

class ConnectionProxy:
    """Wraps sqlite3 connection to mimic mysql.connector connection."""
    def __init__(self, conn):
        self.conn = conn

    def cursor(self, *args, **kwargs):
        return CursorProxy(self.conn.cursor(*args, **kwargs))

    def commit(self):
        return self.conn.commit()

    def rollback(self):
        return self.conn.rollback()

    def close(self):
        return self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()

def connect(*args, **kwargs):
    """Intercepts mysql.connector.connect() and routes to SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allows dictionary-like row access
    return ConnectionProxy(conn)

# Expose standard MySQL exceptions as SQLite equivalents
Error = sqlite3.Error
IntegrityError = sqlite3.IntegrityError
DatabaseError = sqlite3.DatabaseError
ProgrammingError = sqlite3.ProgrammingError