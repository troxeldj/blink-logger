# import override
from appenders.base_appender import BaseAppender
from core.record import LogRecord
from formatters.base_formatter import BaseFormatter
from core.color import ConsoleColor
from typing import Union, Optional, List, TYPE_CHECKING
from typing import override
from utils.interfaces import JsonSerializable
from formatters import all_formatter_strings
import sys

if TYPE_CHECKING:
    from filters.base_filter import BaseFilter
    from config.str_to import StringToFilter

class ConsoleAppender(BaseAppender):
	"""Appender that writes log records to the console."""
	def __init__(self, formatter: Union[BaseFormatter, None] = None, filters: Optional[List["BaseFilter"]] = None):
		super().__init__(formatter, filters)

	@override
	def flush(self):
		sys.stdout.flush()

	@override
	def append(self, record: LogRecord):
		"""Append a log record to the console."""
		formatted_record = self.formatter.format(record)
		if self.filters:
			if not all(f.should_log(record) for f in self.filters):
				return
		sys.stdout.write(formatted_record + '\n')
		self.flush()

	@override
	@classmethod
	def from_dict(cls, data: dict) -> 'ConsoleAppender':
		"""Create a ConsoleAppender instance from a dictionary."""
		formatter_data = data.get('formatter', {})
		formatter_type = formatter_data.get('type', 'SimpleFormatter')
		if formatter_type not in all_formatter_strings:
			raise ValueError(f"Formatter type '{formatter_type}' is not recognized.")
		formatter_class = all_formatter_strings[formatter_type]
		formatter_instance = formatter_class.from_dict(formatter_data)
		if not isinstance(formatter_instance, BaseFormatter):
			raise TypeError(f"Formatter instance must be of type BaseFormatter, got {type(formatter_instance)}")
		filters_data: List[dict] = data.get('filters', [])
		filters = []
		for f in filters_data:
			if 'type' not in f:
				raise ValueError("filter must have a type")
			filter_class = StringToFilter(f['type'])
			filters.append(filter_class.from_dict(f))
		return cls(formatter=formatter_instance, filters=filters)



class ColoredConsoleAppender(ConsoleAppender):
	"""Appender that writes colored log records to the console."""
	def __init__(self, formatter: Union[BaseFormatter, None] = None, color: ConsoleColor = ConsoleColor.DEFAULT):
		super().__init__(formatter)
		self.color: ConsoleColor = color

	@override
	def initialize(self):
		pass

	@override
	def teardown(self):
		pass

	@override
	def flush(self):
		sys.stdout.flush()

	@override
	def append(self, record: LogRecord):
		"""Append a log record to the console with colors (placeholder implementation)."""
		formatted_record = self.formatter.format(record)
		colored_record = f"{self.color.value}{formatted_record}{ConsoleColor.RESET.value}"
		sys.stdout.write(colored_record + '\n')
		self.flush()

	def set_color(self, color: ConsoleColor):
		"""Set the color for the console appender."""
		self.color = color
		