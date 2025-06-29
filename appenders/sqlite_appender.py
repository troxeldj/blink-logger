from appenders.base_appender import BaseAppender
from core.record import LogRecord
import sqlite3
from typing import override, List, Optional
from filters import BaseFilter
from config.str_to import StringToFilter 

class SQLiteAppender(BaseAppender):
  def __init__(self, db_path: str, table_name = "logs", filters: Optional[List[BaseFilter]] = []):
    self.filters: Optional[List[BaseFilter]] = filters if filters else []
    self.db_path: str = db_path
    self.table_name: str = table_name
    self._connection: sqlite3.Connection = sqlite3.connect(db_path)
    self._cursor: sqlite3.Cursor = self._connection.cursor()
    self._init_table()

  @override
  def __del__(self):
    self.teardown()

  @override
  def teardown(self):
    self._cursor.close()
    self._connection.close()

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
    if self.filters:
      if not all(f.should_log(record) for f in self.filters):
        return
    self._cursor.execute(
      f"INSERT INTO {self.table_name} (timestamp, level, message) VALUES (?, ?, ?)",
      (record.timestamp, record.level.name, record.message)
    )
    self._connection.commit()


  @classmethod
  def _parse_filters(cls, data: List[dict]) -> List[BaseFilter]:
    filters = []
    for filter_data in data:
      if not isinstance(filter_data, dict):
        raise ValueError("Each filter must be a dictionary")
      if 'type' not in filter_data:
        raise ValueError("Filter should have a 'type' property")
      filter_type = filter_data.get("type")
      if not filter_type:
        raise ValueError("Each filter dictionary must have a 'type' key")
      # Assuming you have a registry or factory for filters
      filter_cls: type = StringToFilter(filter_type)
      filter_instance = filter_cls.from_dict(filter_data)
      if not isinstance(filter_instance, BaseFilter):
        raise ValueError("Filter must be a subclass of BaseFilter")
      filters.append(filter_instance)
    return filters

  @override
  @classmethod 
  def from_dict(cls, data: dict):
    if 'db_path' not in data:
      raise ValueError("db_path must be in the config dictionary")
    if type(data['db_path']) != str:
      raise ValueError("db_path must be a string")
    if 'filters' in data:
      if type(data['filters']) != list:
        raise ValueError('filters must be a list')
      filters: List[BaseFilter] = cls._parse_filters(data['filters'])
    return cls(
      db_path=data["db_path"],
      table_name=data.get("table_name", "logs"),
      filters=filters
    )
    
  @override
  def to_dict(self):
    return {
      "db_path": self.db_path,
      "table_name": self.table_name
    }
