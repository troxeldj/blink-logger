from core.level import LoggingLevel
from core.record import LogRecord
from typing import Union, List, Optional, TYPE_CHECKING
from utils.dec import throws

if TYPE_CHECKING:
    from appenders.base_appender import BaseAppender
    from formatters.base_formatter import BaseFormatter
    from formatters.simple_formatter import SimpleFormatter
class Logger:
		@throws(TypeError, ValueError)
		def __init__(self, name: str, level: Union[LoggingLevel, None] = None, formatter: Optional["BaseFormatter"] = None, appenders: List["BaseAppender"] = []):
			"""Initialize the Logger with a name, logging level, formatter, and appenders."""
			self.name: str = name
			self.current_level: LoggingLevel = level if level else LoggingLevel.INFO
			from formatters.simple_formatter import SimpleFormatter
			self.formatter: "BaseFormatter" = formatter if formatter else SimpleFormatter()
			from formatters.base_formatter import BaseFormatter
			if not isinstance(self.formatter, BaseFormatter):
				raise TypeError("formatter must be an instance of BaseFormatter.")
			if not appenders:
				raise ValueError("At least one appender must be provided.")
			self.appenders: List["BaseAppender"] = appenders
			from managers.global_manager import GlobalManager
			GlobalManager.get_instance().add_logger(self)

		@throws(TypeError)
		def _verify_log(self, level: LoggingLevel, message: str, metadata: Optional[dict] = {}):
			if not isinstance(level, LoggingLevel):
				raise TypeError("level must be an instance of LoggingLevel.")
			if level < self.current_level:
				return	
			if not isinstance(message, str):
				raise TypeError("message must be a string.")
			if metadata is not None and not isinstance(metadata, dict):
				raise TypeError("metadata must be a dictionary or None.")
			if not isinstance(self.formatter, self._get_base_formatter_class()):
				raise TypeError("formatter must be an instance of BaseFormatter.")
			if not isinstance(self.appenders, list):
				raise TypeError("appenders must be a list of BaseAppender instances.")
			if not all(isinstance(appender, self._get_base_appender_class()) for appender in self.appenders):
				raise TypeError("All appenders must be instances of BaseAppender.")

		def _get_base_formatter_class(self):
			"""Helper method to get BaseFormatter class at runtime."""
			from formatters.base_formatter import BaseFormatter
			return BaseFormatter

		def _get_base_appender_class(self):
			"""Helper method to get BaseAppender class at runtime."""
			from appenders.base_appender import BaseAppender
			return BaseAppender

		@throws(TypeError)
		def log(self, level: LoggingLevel, message: str, metadata: Optional[dict] = {}):
			"""Log a message at the specified logging level."""
			self._verify_log(level, message, metadata)
			record = LogRecord(
				level=level,
				message=message,
				metadata=metadata
			)
			for appender in self.appenders:
				appender.append(record)

		@throws(TypeError)	
		def set_level(self, level: LoggingLevel):
			"""Set the logging level for the logger."""
			if not isinstance(level, LoggingLevel):
				raise TypeError("level must be an instance of LoggingLevel.")
			self.current_level = level

		@throws(TypeError)	
		def add_appender(self, appender: "BaseAppender"):
			"""Add an appender to the logger."""
			if not isinstance(appender, self._get_base_appender_class()):
				raise TypeError("appender must be an instance of BaseAppender.")
			self.appenders.append(appender)

		@throws(TypeError, ValueError)
		def remove_appender(self, appender: "BaseAppender"):
			"""Remove an appender from the logger."""
			if not isinstance(appender, self._get_base_appender_class()):
				raise TypeError("appender must be an instance of BaseAppender.")
			if appender in self.appenders:
				self.appenders.remove(appender)
			else:
				raise ValueError("Appender not found in the logger's appenders list.")
		
		def clear_appenders(self):
			"""Clear all appenders from the logger."""
			self.appenders.clear()

		def get_appenders(self) -> List["BaseAppender"]:
			"""Get the list of appenders associated with the logger."""
			return self.appenders.copy()
		
		def get_level(self) -> LoggingLevel:
			"""Get the current logging level of the logger."""
			return self.current_level
		
		def get_name(self) -> str:
			"""Get the name of the logger."""
			return self.name

		@throws(TypeError)	
		def set_formatter(self, formatter: "BaseFormatter"):
			"""Set the formatter for the logger."""
			if not isinstance(formatter, self._get_base_formatter_class()):
				raise TypeError("formatter must be an instance of BaseFormatter.")
			self.formatter = formatter

		def get_formatter(self) -> "BaseFormatter":
			"""Get the current formatter of the logger."""
			return self.formatter
		
		def __repr__(self):
			return f"Logger(name={self.name}, level={self.current_level}, formatter={self.formatter.__class__.__name__}, appenders={len(self.appenders)})"
		
		def __str__(self):
			return f"Logger: {self.name}, Level: {self.current_level.name}, Formatter: {self.formatter.__class__.__name__}, Appenders: {len(self.appenders)}"
		
		def __eq__(self, other):
			if not isinstance(other, Logger):
				return False
			return (self.name == other.name and
					self.current_level == other.current_level and
					self.formatter == other.formatter and
					self.appenders == other.appenders)