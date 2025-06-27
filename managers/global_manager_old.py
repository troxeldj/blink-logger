from typing import Union, override, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from managers.log_manager import LogManager
    from core.logger import Logger


class GlobalManager():
		"""
		GlobalManager is a singleton class that manages global state and configurations
		for the application. It can be used to store and retrieve global settings,
		configurations, or any other shared state across the application.
		"""
		_instance: Optional["LogManager"]  = None

	def __new__(cls) -> "LogManager":
		"""Ensure that only one instance of GlobalManager exists."""
		if cls._instance is None:
			from managers.log_manager import LogManager
			cls._instance = LogManager(name="GlobalLogManager")
			cls._setup_global_logger()
		return cls._instance

	@classmethod
		def get_instance(cls) -> "LogManager":
				"""Get the singleton instance of GlobalManager."""
				if cls._instance is None:
					from managers.log_manager import LogManager
					cls._instance = LogManager(name="GlobalLogManager")
					cls._setup_global_logger()
				return cls._instance
		
		@classmethod
		def _setup_global_logger(cls):
				"""Set up the global logger with basic console appender."""
				if not cls.get_instance().__contains__("global"):
					from appenders.console_appender import ConsoleAppender
					from formatters.simple_formatter import SimpleFormatter
					from core.logger import Logger
					from core.level import LoggingLevel
					console_appender = ConsoleAppender(SimpleFormatter())
					cls.get_instance().add_logger(Logger("global", LoggingLevel.INFO, [console_appender], auto_register=False))

		@classmethod
		def get_global_logger(cls) -> "Logger":
				"""Get the global logger instance."""
				return cls.get_instance().get_logger("global")

		@override
		def __repr__(self) -> str:
				return f"GlobalManager(instance={self._instance})"
		
		@override
		def __str__(self) -> str:
				return f"GlobalManager with LogManager: {self._instance}"