from appenders.base_appender import BaseAppender
from core.record import LogRecord
import sqlite3
from typing import override

class SQLiteAppender(BaseAppender):
  def __init__(self, db_path: str, table_name = "logs"):
    self.db_path: str = db_path
    self.table_name: str = table_name
    self._connection: sqlite3.Connection = sqlite3.connect(db_path)
    self._cursor: sqlite3.Cursor = self._connection.cursor()
    self._init_table()

  def _init_table(self):
    self._cursor.execute(f"""
      CREATE TABLE IF NOT EXISTS {self.table_name} (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      timestamp TEXT NOT NULL,
      level TEXT NOT NULL,
      message TEXT NOT NULL
      )
    """)
    self._connection.commit()

  @override
  def append(self, record: LogRecord):
    self._cursor.execute(
      f"INSERT INTO {self.table_name} (timestamp, level, message) VALUES (?, ?, ?)",
      (record.timestamp, record.level.name, record.message)
    )
    self._connection.commit()

  @override
  @classmethod 
  def from_dict(cls, data: dict):
    if 'db_path' not in data:
      raise ValueError("db_path must be in the config dictionary")
    if type(data['db_path']) != str:
      raise ValueError("db_path must be a string")
    return cls(
      db_path=data["db_path"],
      table_name=data.get("table_name", "logs")
    )
    
  @override
  def to_dict(self):
    return {
      "db_path": self.db_path,
      "table_name": self.table_name
    }
