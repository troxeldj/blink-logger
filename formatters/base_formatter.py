from abc import ABC, abstractmethod
from core.record import LogRecord
from utils.dec import throws
class BaseFormatter(ABC):
	@throws(NotImplementedError)
	@abstractmethod
	def format(self, record:  LogRecord)-> str:
		"""Format a log record into the desired output format"""
		raise NotImplementedError("Subclasses must implement this method")