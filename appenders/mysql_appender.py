import mysql.connector
from appenders.base_appender import BaseAppender
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from core.record import LogRecord
from utils.dec import throws
from typing import override, Optional, List, Union, Any
from filters.base_filter import BaseFilter
from config.str_to import StringToFilter
import json
import time


class MySQLConnectionException(Exception):
  def __init__(self, message: str):
    super().__init__(message)


class MySQLAppender(BaseAppender):
  @throws(MySQLConnectionException)
  def __init__(
    self,
    host: str,
    user: str,
    password: str,
    database: str,
    table_name: str = "logs",
    filters: Optional[List[BaseFilter]] = [],
    autocommit: bool = True,
    reconnect: bool = True,
    connect_timeout: int = 10,
  ):
    self.filters = filters if filters else []
    self.host: str = host
    self.user: str = user
    self.password: str = password
    self.database: str = database
    self.table_name: str = table_name if table_name else "logs"
    self.autocommit: bool = autocommit
    self.reconnect: bool = reconnect
    self.connect_timeout: int = connect_timeout
    self._connection: Optional[Any] = None
    self._cursor: Optional[Any] = None
    self._last_ping: float = 0
    self._ping_interval: float = 300  # Ping every 5 minutes

    self._connect()
    self._init_table()

  def _connect(self):
    """Establish database connection with proper timeout and reconnection settings."""
    try:
      self._connection = mysql.connector.connect(
        host=self.host,
        user=self.user,
        password=self.password,
        database=self.database,
        autocommit=self.autocommit,
        use_unicode=True,
        charset="utf8mb4",
        connect_timeout=self.connect_timeout,
        # Connection pool settings to prevent timeouts
        pool_name=f"logger_pool_{id(self)}",
        pool_size=1,
        pool_reset_session=True,
        # Keep connection alive
        sql_mode="",
        init_command="SET SESSION wait_timeout=31536000",  # 1 year
      )
      self._cursor = self._connection.cursor()
      self._last_ping = time.time()
    except mysql.connector.Error as err:
      raise MySQLConnectionException(f"Error connecting to MySQL: {err}")

  def _ensure_connection(self):
    """Ensure database connection is alive, reconnect if needed."""
    current_time = time.time()

    # Check if we need to ping (every 5 minutes)
    if current_time - self._last_ping > self._ping_interval:
      try:
        if self._connection and self._connection.is_connected():
          self._connection.ping(reconnect=self.reconnect, attempts=3, delay=1)
          self._last_ping = current_time
          return
      except mysql.connector.Error:
        pass  # Will reconnect below

    # Connection is dead or doesn't exist, reconnect
    if not self._connection or not self._connection.is_connected():
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

  def _init_table(self):
    """Initialize the log table if it doesn't exist."""
    self._ensure_connection()
    create_table_query = f"""
  CREATE TABLE IF NOT EXISTS `{self.table_name}` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    extra JSON NULL
  )
  """
    if self._cursor:
      self._cursor.execute(create_table_query)
    if self._connection and not self.autocommit:
      self._connection.commit()

  @override
  def teardown(self):
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

  @override
  def to_dict(self) -> dict:
    return {
      "host": self.host,
      "user": self.user,
      "password": self.password,
      "database": self.database,
      "table_name": self.table_name,
      "autocommit": self.autocommit,
      "reconnect": self.reconnect,
      "connect_timeout": self.connect_timeout,
    }

  @override
  def append(self, record: LogRecord):
    """Append a log record to the database with automatic reconnection."""
    if self.filters:
      if not all(f.should_log(record) for f in self.filters):
        return

    try:
      self._ensure_connection()

      insert_query = f"""
    INSERT INTO `{self.table_name}` (timestamp, level, message)
    VALUES (%s, %s, %s)
    """
      timestamp = record.timestamp.strftime("%Y-%m-%d %H:%M:%S")
      level = str(record.level)
      message = record.message

      if self._cursor:
        self._cursor.execute(insert_query, (timestamp, level, message))
      if self._connection and not self.autocommit:
        self._connection.commit()

    except mysql.connector.Error as err:
      # Try to reconnect once more on error
      try:
        self._connect()
        if self._cursor:
          self._cursor.execute(insert_query, (timestamp, level, message))
        if self._connection and not self.autocommit:
          self._connection.commit()
      except mysql.connector.Error:
        # Log the error but don't raise it to prevent breaking the application
        print(f"MySQLAppender: Failed to log message: {err}")
        pass

  @classmethod
  @override
  def from_dict(cls, data: dict) -> "MySQLAppender":
    if "host" not in data:
      raise ValueError("'host' must be specified")
    if not isinstance(data["host"], str):
      raise ValueError("'host' must be a string")
    host: str = data["host"]
    if "user" not in data:
      raise ValueError("'user' must be specified")
    if not isinstance(data["user"], str):
      raise ValueError("'user' must be a string")
    user: str = data["user"]
    if "password" not in data:
      raise ValueError("'password' must be specified")
    if not isinstance(data["password"], str):
      raise ValueError("'password' must be a string")
    password: str = data["password"]
    if "database" not in data:
      raise ValueError("'database' must be specified")
    if not isinstance(data["database"], str):
      raise ValueError("'database' must be a string")
    database: str = data["database"]
    table_name: Union[str, None] = None
    if "table_name" in data:
      if isinstance(data["table_name"], str):
        table_name = data["table_name"]
    filters: Optional[List[BaseFilter]] = []
    if "filters" in data:
      if not isinstance(data["filters"], list):
        raise ValueError("'filters' must be a list")
      filters = cls._parse_filters(data["filters"])
    return cls(
      host=host,
      user=user,
      password=password,
      database=database,
      filters=filters,
      table_name=table_name if table_name else "logs",
    )

  @classmethod
  def _parse_filters(cls, data: List[dict]) -> List[BaseFilter]:
    filters = []
    for filter_data in data:
      if not isinstance(filter_data, dict):
        raise ValueError("Each filter must be a dictionary")
      if "type" not in filter_data:
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
