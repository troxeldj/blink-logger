import sys
import os

# Fix import path if run as a script
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataclasses import dataclass
from core.level import LoggingLevel
from typing import List
from appenders.base_appender import BaseAppender
from formatters.base_formatter import BaseFormatter
from formatters import all_formatter_strings
from appenders import all_appender_strings

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
		def _parse_formatter(cls, formatter_data: dict[str, str]):
			all_formatters = all_formatter_strings 
			if(formatter_data is None or not isinstance(formatter_data, dict)):
				raise ValueError("Formatter data must be a dictionary.")
			if 'type' not in formatter_data:
				raise ValueError("Formatter data must contain a 'type' key.")
			formatter_type = formatter_data.get('type', 'SimpleFormatter')
			if formatter_type not in all_formatters:
				raise ValueError(f"Formatter type '{formatter_type}' is not recognized.")
			# Create an instance of the formatter using the from_dict method
			formatter_class = all_formatters[formatter_type]
			formatter_instance = formatter_class.from_dict(formatter_data)
			if not isinstance(formatter_instance, BaseFormatter):
				raise TypeError(f"Formatter instance must be of type BaseFormatter, got {type(formatter_instance)}")
			return formatter_instance
		
		@classmethod
		def _parse_appenders(cls, appenders_data: List[dict]) -> List[BaseAppender]:
				"""
				Parse a list of appender configurations and return a list of BaseAppender instances
				Args:
						appenders_data (List[dict]): List of appender configurations.
				Returns:
						List[BaseAppender]: List of BaseAppender instances.
				"""
				if appenders_data is None or not isinstance(appenders_data, list):
						raise ValueError("Appenders data must be a list.")
				appenders = []
				for appender_data in appenders_data:
						if not isinstance(appender_data, dict):
								raise ValueError("Each appender configuration must be a dictionary.")
						if 'type' not in appender_data:
								raise ValueError("Appender configuration must contain a 'type' key.")
						appender_type = appender_data.get('type', 'ConsoleAppender')
						if appender_type not in all_appender_strings:
								raise ValueError(f"Appender type '{appender_type}' is not recognized.")
						# Create an instance of the appender using the from_dict method
						appender_class = all_appender_strings[appender_type]
						appender_instance = appender_class.from_dict(appender_data)
						if not isinstance(appender_instance, BaseAppender):
								raise TypeError(f"Appender instance must be of type BaseAppender, got {type(appender_instance)}")
						appenders.append(appender_instance)
				# Return the list of appender instances
				return appenders


			

		@classmethod
		def from_json(cls, json_path: str) -> 'LoggerConfig':
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
				# Create LoggerConfig instance from the loaded data
				return cls(
						name=data['name'],
						level=LoggingLevel[data['level'].upper()],
						formatter=cls._parse_formatter(data['formatter']),
						appenders=cls._parse_appenders(data.get('appenders'))
				)



if __name__ == "__main__":
	# Example usage
	config_name: str = "simple_config.json"
	base_dir: str = os.path.dirname(os.path.abspath(__file__))
	json_path: str = os.path.join(base_dir, "config", 'logger_config.json')
	config = LoggerConfig.from_json(json_path)
	print(config)