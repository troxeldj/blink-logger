from typing import Union, override, TYPE_CHECKING

if TYPE_CHECKING:
    from managers.log_manager import LogManager

class GlobalManager():
		"""
		GlobalManager is a singleton class that manages global state and configurations
		for the application. It can be used to store and retrieve global settings,
		configurations, or any other shared state across the application.
		"""
		_instance: Union["LogManager", None] = None

		def __new__(cls) -> "LogManager":
				if cls._instance is None:
						from managers.log_manager import LogManager
						cls._instance = LogManager(name="GlobalLogManager")
				return cls._instance

		@classmethod
		def get_instance(cls) -> "LogManager":
				"""Get the singleton instance of GlobalManager."""
				if cls._instance is None:
					from managers.log_manager import LogManager
					cls._instance = LogManager(name="GlobalLogManager")
				return cls._instance
		
		@override
		def __repr__(self) -> str:
				return f"GlobalManager(instance={self._instance})"
		
		@override
		def __str__(self) -> str:
				return f"GlobalManager with LogManager: {self._instance}"