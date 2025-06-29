import sys
import os
from managers.global_manager import GlobalManager

# Fix import path if run as a script
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataclasses import dataclass
from core.level import LoggingLevel
from typing import List
from appenders.base_appender import BaseAppender
from appenders import all_appender_strings

@dataclass
class LoggerConfig:
		"""
		Configuration class for the logger.
		"""
		name: str  
		level: LoggingLevel
		appenders: List[BaseAppender]


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
						appenders=cls._parse_appenders(data.get('appenders'))
				)

		def to_logger(self):
			from core import Logger
			return Logger(
				name=config.name,
				level=config.level,
				appenders=config.appenders
      )



if __name__ == "__main__":
	# Example usage
	config_name: str = "simple_config.json"
	base_dir: str = os.path.dirname(os.path.abspath(__file__))
	json_path: str = os.path.join(base_dir, "test_configs", config_name)
	config: LoggerConfig = LoggerConfig.from_json(json_path)
	logger = config.to_logger()
	logger.error("test msg")
	print(config)
	print(GlobalManager.get_instance().loggers)