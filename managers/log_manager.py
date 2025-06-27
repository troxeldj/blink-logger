from typing import List, Dict, TYPE_CHECKING
from utils.dec import throws

if TYPE_CHECKING:
    from core.logger import Logger
class LogManager:
		def __init__(self, name: str, initial_loggers: Dict[str, "Logger"] = {}):
				self.name: str = name
				"""Initialize the LogManager with an optional dictionary of loggers."""
				self.loggers: Dict[str, "Logger"] = initial_loggers if initial_loggers else {}

		@throws(TypeError, ValueError)
		def _add_logger_checks(self, logger: "Logger") -> None:
				"""Perform checks before adding a logger."""
				from core.logger import Logger
				if not isinstance(logger, Logger):
					raise TypeError("logger must be an instance of Logger.")
				if not logger.name:
					raise ValueError("Logger must have a name.")
				if not isinstance(logger.name, str):
					raise TypeError("Logger name must be a string.")
				if logger.name in self.loggers:
					raise ValueError(f"A logger with the name '{logger.name}' already exists.")

		def add_logger(self, logger: "Logger"):
				"""Add a logger to the LogManager."""
				self._add_logger_checks(logger)
				self.loggers[logger.name] = logger

		@throws(TypeError, KeyError)
		def get_logger(self, name: str) -> "Logger":
				"""Retrieve a logger by its name."""
				if not isinstance(name, str):
					raise TypeError("Logger name must be a string.")
				if name not in self.loggers:
					raise KeyError(f"No logger found with the name '{name}'.")
				return self.loggers[name]

		@throws(TypeError, KeyError)	
		def remove_logger(self, name: str):
				"""Remove a logger by its name."""
				if not isinstance(name, str):
					raise TypeError("Logger name must be a string.")
				if name not in self.loggers:
					raise KeyError(f"No logger found with the name '{name}'.")
				del self.loggers[name]

		def get_all_loggers(self) -> List["Logger"]:
				"""Get a list of all loggers managed by the LogManager."""
				return list(self.loggers.values())
		
		def clear_loggers(self):
				"""Clear all loggers managed by the LogManager."""
				self.loggers.clear()

		def __repr__(self):
				return f"LogManager(loggers={list(self.loggers.keys())})"

		@throws(TypeError)	
		def __contains__(self, name: str) -> bool:
				"""Check if a logger with the given name exists in the LogManager."""
				if not isinstance(name, str):
					raise TypeError("Logger name must be a string.")
				return name in self.loggers
		
		def __getitem__(self, name: str) -> "Logger":
				"""Get a logger by its name using dictionary-like access."""
				return self.get_logger(name)

		@throws(TypeError)	
		def __setitem__(self, name: str, logger: "Logger"):
				"""Set a logger by its name using dictionary-like access."""
				if not isinstance(name, str):
					raise TypeError("Logger name must be a string.")
				self.add_logger(logger)

		@throws(TypeError, KeyError)
		def __delitem__(self, name: str):
				"""Delete a logger by its name using dictionary-like access."""
				self.remove_logger(name)

		def __iter__(self):
				"""Iterate over the names of the loggers."""
				return iter(self.loggers)
		
		def __len__(self) -> int:
				"""Get the number of loggers managed by the LogManager."""
				return len(self.loggers)
		
		def __str__(self):
				"""Get a string representation of the LogManager."""
				return f"LogManager with {len(self.loggers)} loggers: {', '.join(self.loggers.keys())}"