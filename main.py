from builders.logger_builder import LoggerBuilder
from formatters.simple_formatter import SimpleFormatter
from appenders.file_appender import FileAppender
from core.level import LoggingLevel
from core.logger import Logger


if __name__ == "__main__":
	myLogger: Logger = LoggerBuilder() \
		.set_name("MyLogger") \
		.set_level(LoggingLevel.DEBUG) \
		.set_formatter(SimpleFormatter()) \
		.add_appender(FileAppender("my_log.txt")) \
		.build()
	
	myLogger.log(LoggingLevel.INFO, "This is an info message.")

		
