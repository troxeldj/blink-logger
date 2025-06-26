from formatters.base_formatter import BaseFormatter
from formatters.simple_formatter import SimpleFormatter
from core.record import LogRecord
from typing import Union, Optional, List, TYPE_CHECKING, override
from utils.dec import throws
from utils.interfaces import JsonSerializable

if TYPE_CHECKING:
    from filters.base_filter import BaseFilter

class BaseAppender(JsonSerializable):
		"""Base class for all appenders"""
		def __init__(self, formatter: Union[BaseFormatter, None] = None, filters: Optional[List["BaseFilter"]] = None):
			"""
			Initialize the appender.
			This function is called when the appender is created.
			It can be used to set up resources, connections, or any other necessary initialization.
			For example, if the appender writes to a file, this function can open the file.
			"""
			self.formatter = formatter or SimpleFormatter()
			self.filters = filters or []

		def __del__(self):
			"""
			Clean up the appender.
			This function is called when the appender is no longer needed.
			It can be used to clean up resources, close connections, or any other necessary teardown.
			For example, if the appender writes to a file, this function can close the file.
			"""
			self.teardown()

		"""
		Function to run when the appender is initialized.
		This function is called when the appender is created.
		It can be used to set up resources, connections, or any other necessary initialization.
		For example, if the appender writes to a file, this function can open the
		"""
		def initialize(self):
			pass

		def teardown(self):
			"""
			Function to run when the appender is destroyed.
			This function is called when the appender is no longer needed.
			It can be used to clean up resources, close connections, or any other necessary teardown.
			For example, if the appender writes to a file, this function can close the file.
			"""
			pass

		def flush(self):
			"""
			Flush the appender.
			This function is called to ensure that all buffered data is written out.
			It can be used to ensure that all log records are written to the destination.
			"""
			pass

		@throws(NotImplementedError)
		def append(self, record: LogRecord):
			"""
			Append a log record to the appender.
			This function is called to add a log record to the appender.
			It can be used to write the log record to the destination.
			"""
			raise NotImplementedError("Subclasses must implement this method.")
		

		@override
		@classmethod
		def from_dict(cls, data: dict) -> 'BaseFormatter':
			"""
			Create an instance of BaseFormatter from a dictionary representation.
			
			Args:
				data (dict): The dictionary representation of the formatter.
			
			Returns:
				BaseFormatter: An instance of BaseFormatter.
			"""
			raise NotImplementedError("Subclasses must implement this method")
		
		@override
		def to_dict(self) -> dict:
			"""
			Convert the instance to a dictionary representation.
			
			Returns:
				dict: The dictionary representation of the formatter.
			"""
			raise NotImplementedError("Subclasses must implement this method")