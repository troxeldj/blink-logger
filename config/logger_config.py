from dataclasses import dataclass
from core.level import LoggingLevel
from typing import List
from appenders.base_appender import BaseAppender
from formatters.base_formatter import BaseFormatter

@dataclass
class LoggerConfig:
		"""
		Configuration class for the logger.
		"""
		name: str  
		level: LoggingLevel
		appenders: List[BaseAppender]
		formatter: BaseFormatter

		@classmethod
		def _validate_dict(self, dict_data: dict):
				"""
				Validate the dictionary data against the LoggerConfig structure.

				Args:
						dict_data (dict): Dictionary containing logger configuration data.

				Raises:
						ValueError: If the dictionary does not conform to the expected structure.
				"""
				if not isinstance(dict_data, dict):
						raise ValueError("Configuration data must be a dictionary.")
				_
		@classmethod
		def from_json(cls, json_path: str):
				"""
				Create a LoggerConfig instance from a JSON file.

				Args:
						json_path (str): Path to the JSON configuration file.

				Returns:
						LoggerConfig: An instance of LoggerConfig populated with data from the JSON file.
				"""
				# If file doesn't exist, throw an error
				import os 
				if not os.path.exists(json_path):
						raise FileNotFoundError(f"Configuration file {json_path} does not exist.")
				import json
				with open(json_path, 'r') as file:
						data = json.load(file)
				cls._validate_dict(data)


