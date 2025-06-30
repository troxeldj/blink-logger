from appenders.base_appender import BaseAppender
from formatters.base_formatter import BaseFormatter
from core.record import LogRecord
from typing import List, Union, override, Optional, TYPE_CHECKING
from utils.dec import throws

if TYPE_CHECKING:
  from filters.base_filter import BaseFilter


class CompositeAppender(BaseAppender):
  """Appender that combines multiple appenders."""

  @throws(ValueError)
  def __init__(
    self,
    formatter: Union[BaseFormatter, None] = None,
    appenders: Optional[List[BaseAppender]] = None,
    filters: Optional[List["BaseFilter"]] = None,
  ):
    if appenders is None:
      appenders = []
    if len(appenders) == 0:
      raise ValueError("At least one appender must be provided.")
    super().__init__(formatter, filters)
    self.appenders = appenders

  @override
  def append(self, record: LogRecord):
    """Append a log record to all configured appenders."""
    for appender in self.appenders:
      # check the filters should_log method
      # if true then append the record
      # else skip the record
      if self.filters:
        if not all(f.should_log(record) for f in self.filters):
          continue
      appender.append(record)

  @override
  def flush(self):
    """Flush all appenders."""
    if hasattr(self, "appenders"):
      for appender in self.appenders:
        appender.flush()

  @override
  def initialize(self):
    """Initialize all appenders."""
    if hasattr(self, "appenders"):
      for appender in self.appenders:
        appender.initialize()

  @override
  def teardown(self):
    """Teardown all appenders."""
    if hasattr(self, "appenders"):
      for appender in self.appenders:
        appender.teardown()

  @throws(TypeError)
  def add_appender(self, appender: BaseAppender):
    """Add an appender to the composite appender."""
    if not isinstance(appender, BaseAppender):
      raise TypeError("appender must be an instance of BaseAppender.")
    self.appenders.append(appender)
