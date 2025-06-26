# import override
from appenders.base_appender import BaseAppender
from core.record import LogRecord
from formatters.base_formatter import BaseFormatter
from core.color import ConsoleColor
from typing import Union, Optional, List, TYPE_CHECKING
from typing import override
import sys

if TYPE_CHECKING:
    from filters.base_filter import BaseFilter

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
		