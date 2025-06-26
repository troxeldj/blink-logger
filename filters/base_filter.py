from core.record import LogRecord
from abc import ABC, abstractmethod

class BaseFilter(ABC):
		@abstractmethod
		def should_log(self, record: LogRecord) -> bool:
			"""Determine if the log record should be processed by this filter."""
			pass