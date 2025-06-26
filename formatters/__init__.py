# Log formatters
from .base_formatter import BaseFormatter
from .simple_formatter import SimpleFormatter
from .json_formatter import JSONFormatter
from typing import Dict


all_formatter_strings: Dict[str, BaseFormatter]  = {
    "SimpleFormatter": SimpleFormatter,
    "JSONFormatter": JSONFormatter,
}

__all__ = [
    "BaseFormatter",
    "SimpleFormatter",
    "JSONFormatter",
    "all_formatter_strings"
]
