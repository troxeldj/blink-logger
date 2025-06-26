from factories.logger_factory import LoggerFactory
from core.level import LoggingLevel
from managers.global_manager import GlobalManager

if __name__ == "__main__":
	LoggerFactory.create_file_logger(
		"test_logger",
		LoggingLevel.INFO,
		"test.log"
	).log(
		None, 
		"This is a test log message.", 
		{"key": "value"}
	)

	print("Global Logger Instances:"  + 
			 len(GlobalManager.get_instance()).__str__())
		
