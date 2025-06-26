# TODO
from enum import Enum


class BaseEvent:
		"""
		Base class for all events.
		"""

		def __init__(self, event_type: str, data: dict = None):
				self.event_type = event_type
				self.data = data if data is not None else {}

		def __repr__(self):
				return f"BaseEvent(event_type={self.event_type}, data={self.data})"
		
