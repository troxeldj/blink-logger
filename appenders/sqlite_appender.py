from appenders.base_appender import BaseAppender
from core.record import LogRecord
import sqlite3
import time
import threading
from typing import override, List, Optional
from filters.base_filter import BaseFilter
from config.str_to import StringToFilter 

class SQLiteAppender(BaseAppender):
  def __init__(self, db_path: str, table_name = "logs", filters: Optional[List[BaseFilter]] = [], 
               timeout: float = 30.0, check_same_thread: bool = False):
    self.filters: Optional[List[BaseFilter]] = filters if filters else []
    self.db_path: str = db_path
    self.table_name: str = table_name
    self.timeout: float = timeout
    self.check_same_thread: bool = check_same_thread
    self._connection: Optional[sqlite3.Connection] = None
    self._cursor: Optional[sqlite3.Cursor] = None
    self._lock = threading.RLock()  # Thread-safe access
    
    self._connect()
    self._init_table()

  def _connect(self):
    """Establish SQLite connection with proper settings."""
    try:
      self._connection = sqlite3.connect(
        self.db_path, 
        timeout=self.timeout,
        check_same_thread=self.check_same_thread,
        isolation_level='DEFERRED'  # Better concurrency
      )
      # Enable WAL mode for better concurrent access
      self._connection.execute('PRAGMA journal_mode=WAL')
      # Set reasonable timeout for busy database
      self._connection.execute('PRAGMA busy_timeout=30000')  # 30 seconds
      self._cursor = self._connection.cursor()
    except sqlite3.Error as err:
      raise ValueError(f"Error connecting to SQLite database: {err}")

  def _ensure_connection(self):
    """Ensure database connection is alive, reconnect if needed."""
    with self._lock:
      try:
        if self._connection:
          # Test connection with a simple query
          self._connection.execute('SELECT 1')
          return
      except sqlite3.Error:
        pass  # Will reconnect below
      
      # Connection is dead or doesn't exist, reconnect
      try:
        if self._cursor:
          self._cursor.close()
        if self._connection:
          self._connection.close()
      except:
        pass  # Ignore errors when cleaning up dead connection
      
      self._connect()

  @override
  def __del__(self):
    self.teardown()

  @override
  def teardown(self):
    with self._lock:
      try:
        if self._cursor:
          self._cursor.close()
        if self._connection:
          self._connection.close()
      except:
        pass  # Ignore errors during cleanup
      finally:
        self._cursor = None
        self._connection = None

  def _init_table(self):
    """Initialize the log table if it doesn't exist."""
    self._ensure_connection()
    if self._cursor:
      self._cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        level TEXT NOT NULL,
        message TEXT NOT NULL
        )
      """)
    if self._connection:
      self._connection.commit()

  @override
  def append(self, record: LogRecord):
    """Append a log record to the database with thread safety and error handling."""
    if self.filters:
      if not all(f.should_log(record) for f in self.filters):
        return
    
    with self._lock:
      try:
        self._ensure_connection()
        
        if self._cursor:
          self._cursor.execute(
            f"INSERT INTO {self.table_name} (timestamp, level, message) VALUES (?, ?, ?)",
            (str(record.timestamp), str(record.level), record.message)
          )
        if self._connection:
          self._connection.commit()
          
      except sqlite3.Error as err:
        # Try to reconnect once more on error
        try:
          self._connect()
          if self._cursor:
            self._cursor.execute(
              f"INSERT INTO {self.table_name} (timestamp, level, message) VALUES (?, ?, ?)",
              (str(record.timestamp), str(record.level), record.message)
            )
          if self._connection:
            self._connection.commit()
        except sqlite3.Error:
          # Log the error but don't raise it to prevent breaking the application
          print(f"SQLiteAppender: Failed to log message: {err}")
          pass


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
    
    filters = []  # Default to empty list
    if 'filters' in data:
      if type(data['filters']) != list:
        raise ValueError('filters must be a list')
      filters: List[BaseFilter] = cls._parse_filters(data['filters'])
    
    return cls(
      db_path=data["db_path"],
      table_name=data.get("table_name", "logs"),
      timeout=data.get("timeout", 30.0),
      check_same_thread=data.get("check_same_thread", False),
      filters=filters
    )
    
  @override
  def to_dict(self):
    return {
      "db_path": self.db_path,
      "table_name": self.table_name,
      "timeout": self.timeout,
      "check_same_thread": self.check_same_thread
    }
