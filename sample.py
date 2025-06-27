from factories.logger_factory import LoggerFactory
from core.level import LoggingLevel
from managers.global_manager import GlobalManager

if __name__ == "__main__":
	GlobalManager.get_global_logger().info("This is a test log message from the sample script.")