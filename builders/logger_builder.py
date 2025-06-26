from core.logger import Logger
from typing import Optional
from formatters.base_formatter import BaseFormatter
from appenders.base_appender import BaseAppender
from core.level import LoggingLevel
from utils.dec import throws
from managers.global_manager import GlobalManager

class LoggerBuilder:
		def __init__(self):
			self.name: Optional[str] = None
			self.level: Optional[LoggingLevel] = None
			self.formatter = None
			self.appenders: list[BaseAppender] = []

		@throws(TypeError)
		def set_name(self, name: str):
			"""Set the name of the logger."""
			if not isinstance(name, str):
				raise TypeError("name must be a string.")
			self.name = name
			return self

		@throws(TypeError)	
		def set_level(self, level: LoggingLevel):
			"""Set the logging level for the logger."""
			if not isinstance(level, LoggingLevel):
				raise TypeError("level must be an instance of LoggingLevel.")
			self.level = level
			return self

		@throws(TypeError)
		def set_formatter(self, formatter: BaseFormatter):
			"""Set the formatter for the logger."""
			if not isinstance(formatter, BaseFormatter):
				raise TypeError("formatter must be an instance of BaseFormatter.")
			self.formatter = formatter
			return self

		@throws(TypeError)	
		def add_appender(self, appender: BaseAppender):
			"""Add an appender to the logger."""
			if not isinstance(appender, BaseAppender):
				raise TypeError("appender must be an instance of BaseAppender.")
			self.appenders.append(appender)
			return self

		@throws(ValueError)	
		def build(self) -> Logger:
			"""Build and return the Logger instance."""
			if not self.name:
				raise ValueError("Logger name must be set.")
			if not self.formatter:
				raise ValueError("Logger formatter must be set.")
			if not self.appenders:
				raise ValueError("At least one appender must be added to the logger.")
			loggerRet = Logger(
				name=self.name,
				level=self.level,
				formatter=self.formatter,
				appenders=self.appenders
			)
			# Note: Logger constructor already registers with GlobalManager
			return loggerRet
