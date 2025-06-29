import mysql.connector
from appenders import BaseAppender
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from core.record import LogRecord
from utils.dec import throws
from typing import override, Optional, List, Union
from filters import BaseFilter
from config.str_to import StringToFilter
import json


class MySQLConnectionException(Exception):
  def __init__(self, message: str):
    super().__init__(message)

class MySQLAppender(BaseAppender):
  @throws(MySQLConnectionException)
  def __init__(self, host: str, user: str, password: str, database: str, table_name: str = "logs", filters: Optional[List[BaseFilter]] = []):
    self.filters = filters if filters else []
    self.host: str = host
    self.user: str = user
    self.password: str = password
    self.database: str = database
    self.table_name: str = table_name if table_name else "logs"
    try:
      self._connection: MySQLConnection  = MySQLConnection(
        host=self.host,
        user=self.user,
        password=self.password,
        database=self.database
      )
      self._cursor: MySQLCursor = self._connection.cursor()
      self._init_table()
    except mysql.connector.Error as err:
      raise MySQLConnectionException(f"Error connecting to MySQL: {err}")

  @override
  def __del__(self):
    self.teardown()

  def _init_table(self):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{self.table_name}` (
      id INT AUTO_INCREMENT PRIMARY KEY,
      timestamp DATETIME NOT NULL,
      level VARCHAR(20) NOT NULL,
      message TEXT NOT NULL,
      extra JSON NULL
    )
    """
    self._cursor.execute(create_table_query)
    self._connection.commit()

  @override
  def teardown(self):
    if self._cursor:
      self._cursor.close()
    if self._connection:
      self._connection.close()

  @override
  def to_dict(self) -> dict:
    return {
      "host": self.host,
      "user": self.user,
      "password": self.password,
      "database": self.database
    }
  
  @override
  def append(self, record: LogRecord):
    if self.filters:
      if not all(f.should_log(record) for f in self.filters):
        return
    insert_query = f"""
      INSERT INTO `{self.table_name}` (timestamp, level, message)
      VALUES (%s, %s, %s)
    """
    timestamp = record.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    level = str(record.level)  # Ensure level is a string
    message = record.message
    self._cursor.execute(insert_query, (timestamp, level, message))
    self._connection.commit()


  @classmethod
  @override
  def from_dict(cls, data: dict) -> "MySQLAppender":
    if 'host' not in data:
      raise ValueError("'host' must be specified")
    if not isinstance(data['host'], str):
      raise ValueError("'host' must be a string")
    host: str = data["host"]
    if 'user' not in data:
      raise ValueError("'user' must be specified")
    if not isinstance(data['user'], str):
      raise ValueError("'user' must be a string")
    user: str = data["user"]
    if 'password' not in data:
      raise ValueError("'password' must be specified")
    if not isinstance(data['password'], str):
      raise ValueError("'password' must be a string")
    password: str = data['password']
    if 'database' not in data:
      raise ValueError("'database' must be specified")
    if not isinstance(data['database'], str):
      raise ValueError("'database' must be a string")
    database: str = data['database']
    table_name: Union[str, None] = None
    if 'table_name' in data:
      if isinstance(data['table_name'], str):
        table_name = data['table_name'] 
    filters: Optional[List[BaseFilter]] = []
    if 'filters' in data:
      if not isinstance(data['filters'], list):
        raise ValueError("'filters' must be a list")
      filters = cls._parse_filters(data['filters'])
    return cls(
      host=host,
      user=user,
      password=password,
      database=database,
      filters=filters,
      table_name=table_name if table_name else "logs"
    )
    

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


