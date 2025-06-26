# mypy: ignore-errors
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.level import LoggingLevel 
from core.record import LogRecord
from formatters.simple_formatter import SimpleFormatter 
from formatters.json_formatter import JSONFormatter

import pytest

# fixture for the LogRecord

@pytest.fixture
def log_record():
		return LogRecord(
				message="Test log message",
				level=LoggingLevel.INFO,
				source="test_source.py",
				metadata={"key": "value"}
		)


def test_simple_formatter(log_record):
		formatter = SimpleFormatter()
		formatted_record = formatter.format(log_record)
		
		assert isinstance(formatted_record, str)
		assert "Test log message" in formatted_record
		assert "INFO" in formatted_record
		# Note: Removed timestamp assertion since timestamp changes each run

def test_json_formatter(log_record):
	formatter = JSONFormatter()
	formatted_record = formatter.format(log_record)
	
	assert isinstance(formatted_record, str)
	assert '"message": "Test log message"' in formatted_record
	assert '"level": "INFO"' in formatted_record
	assert '"source": "test_source.py"' in formatted_record
	assert '"key": "value"' in formatted_record
	# Note: Removed timestamp assertion since timestamp changes each run
