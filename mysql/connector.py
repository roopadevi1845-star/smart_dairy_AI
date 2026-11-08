import os
import sqlite3

DB_PATH = os.path.join(os.getcwd(), "smart_dairy.db")

class CursorProxy:
    def __init__(self, cursor):
        self.cursor = cursor
    def execute(self, operation, params=None, multi=False):
        if params:
            operation = operation.replace("%s", "?")
            return self.cursor.execute(operation, params)
        return self.cursor.execute(operation)
    def executemany(self, operation, seq_params):
        operation = operation.replace("%s", "?")
        return self.cursor.executemany(operation, seq_params)
    def fetchone(self): return self.cursor.fetchone()
    def fetchall(self): return self.cursor.fetchall()
    def fetchmany(self, size=None): return self.cursor.fetchmany(size)
    @property
    def lastrowid(self): return self.cursor.lastrowid
    @property
    def rowcount(self): return self.cursor.rowcount
    def close(self): return self.cursor.close()
    def __iter__(self): return iter(self.cursor)

class ConnectionProxy:
    def __init__(self, conn): self.conn = conn
    def cursor(self, *args, **kwargs):
        # SQLite cursor() does not take arguments like dictionary=True; call plain cursor()
        return CursorProxy(self.conn.cursor())
    def commit(self): return self.conn.commit()
    def rollback(self): return self.conn.rollback()
    def close(self): return self.conn.close()
    def __enter__(self): return self
    def __exit__(self, et, ev, tb):
        if et: self.rollback()
        else: self.commit()
        self.close()

def connect(*args, **kwargs):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return ConnectionProxy(conn)

Error = sqlite3.Error
IntegrityError = sqlite3.IntegrityError
DatabaseError = sqlite3.DatabaseError
ProgrammingError = sqlite3.ProgrammingError
