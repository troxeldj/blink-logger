from factories.logger_factory import LoggerFactory
from core.level import LoggingLevel
from managers.global_manager import GlobalManager
from appenders.composite_appender import CompositeAppender
from appenders.console_appender import ConsoleAppender

if __name__ == "__main__":
	(
		GlobalManager
		.get_global_logger()
		.info("This is a test log message from the sample script.")
	)
	LoggerFactory.create_logger(
  name="SampleLogger",
	  level=LoggingLevel.INFO,
  appenders=[
    CompositeAppender(
      appenders=[
        ConsoleAppender()
      ]
    )
  ]
		).error("This is an error message from the sample script.")