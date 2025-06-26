from appenders.base_appender import BaseAppender
from typing import Union
from formatters.base_formatter import BaseFormatter
from typing import override, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from filters.base_filter import BaseFilter


class FileAppender(BaseAppender):
		"""Appender that writes log records to a file."""
		
		def __init__(self, file_path: str, formatter: Union[BaseFormatter, None] = None, filters: Optional[List["BaseFilter"]] = None):
				super().__init__(formatter, filters)
				self.file_path = file_path
				self.file = None
				self.initialize()
			
		def __del__(self):
				"""Ensure the file is closed when the appender is deleted."""
				self.teardown()

		@override
		def initialize(self):
				"""Open the file for writing."""
				self.file = open(self.file_path, 'a')

		@override
		def teardown(self):
				"""Close the file."""
				if self.file:
						self.file.close()

		@override
		def flush(self):
				"""Flush the file buffer."""
				if self.file:
						self.file.flush()

		@override
		def append(self, record):
				"""Append a log record to the file."""
				formatted_record = self.formatter.format(record)
				if self.file:
						if self.filters:
								if not all(f.should_log(record) for f in self.filters):
										return
						self.file.write(formatted_record + '\n')
						self.flush()