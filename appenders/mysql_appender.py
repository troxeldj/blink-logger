import mysql.connector
from appenders import BaseAppender
import mysql

class MySQLAppender(BaseAppender):
  def __init__(self, user: str, password: str):
    self.user = user
    self.password = password

  def __del__(self):
    self.teardown()

  def teardown(self):
    pass

  def to_dict(self) -> dict:
    pass

  def from_dict(data: dict) -> "MySQLAppender":
    pass