from appenders.base_appender import BaseAppender
from typing import Union
from formatters.base_formatter import BaseFormatter
from typing import override, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from filters.base_filter import BaseFilter


class FileAppender(BaseAppender):
    """Appender that writes log records to a file."""

    def __init__(
        self,
        file_path: str,
        formatter: Union[BaseFormatter, None] = None,
        filters: Optional[List["BaseFilter"]] = None,
    ):
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
        self.file = open(self.file_path, "a")

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
            self.file.write(formatted_record + "\n")
            self.flush()

    @classmethod
    @override
    def from_dict(cls, data: dict) -> "FileAppender":
        """Create a FileAppender instance from a dictionary."""
        file_path = data.get("file_path")
        if not file_path:
            raise ValueError("FileAppender requires 'file_path' in configuration.")
        formatter_data = data.get("formatter", {})
        formatter = BaseFormatter.from_dict(formatter_data)
        filters_data = data.get("filters", [])
        filters = [BaseFilter.from_dict(f) for f in filters_data]
        return cls(file_path, formatter, filters)

    @override
    def to_dict(self) -> dict:
        """Convert the instance to a dictionary representation."""
        return {
            "type": "FileAppender",
            "file_path": self.file_path,
            "formatter": self.formatter.to_dict(),
            "filters": [f.to_dict() for f in self.filters],
        }
