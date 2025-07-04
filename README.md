# blink-logger 📝

A pure object-oriented Python logging library built from scratch with a focus on simplicity and power.

## 🚀 Quick Setup

### Prerequisites
- Python 3.8 or higher (as specified in setup.py)

### Installation

**Option 1: Development Installation (Recommended)**
```bash
# Clone the repository
git clone https://github.com/troxeldj/blink-logger.git
cd blink-logger

# Install in development mode with all dependencies
pip install -e .[dev]

# Note: if using zsh you need quotes around the .[dev] like
pip install -e".[dev]"

# Or install requirements manually
pip install -r requirements.txt

# Verify installation by running tests
python -m pytest tests/ -v
```


### Dependencies
- **Core**: No external dependencies for basic logging functionality
- **Development**: `pytest` for testing, `mysql-connector-python` for database appenders
- **Testing**: `pytest>=6.0` for running the test suite

### Verify Installation
```python
# Test basic functionality
from __init__ import get_global_logger

logger = get_global_logger()
logger.info("🎉 blink-logger is working!")
# Should output: [2025-06-29T10:30:15.123456 INFO]: 🎉 blink-logger is working!
```

## ✨ What's New - Global Logger & Decorators

**Database Logging Support** 🗄️
```python
# MySQL and SQLite appenders for persistent logging
from appenders.mysql_appender import MySQLAppender
from appenders.sqlite_appender import SQLiteAppender
from builders.logger_builder import LoggerBuilder

# Log to MySQL database
mysql_logger = (LoggerBuilder()
    .set_name("mysql-logger")
    .add_appender(MySQLAppender(
        host="localhost",
        user="logger",
        password="password",
        database="logs"
    ))
    .build())

# Log to SQLite file
sqlite_logger = (LoggerBuilder()
    .set_name("sqlite-logger")
    .add_appender(SQLiteAppender("app.db"))
    .build())

mysql_logger.info("Logged to MySQL!")
sqlite_logger.info("Logged to SQLite!")
```

**Zero Configuration Logging** 🚀
```python
# Just import and log - it's that simple!
from __init__ import get_global_logger

logger = get_global_logger()
logger.info("Hello, World! 👋")
# Output: [2025-06-26T19:46:44.527147 INFO]: Hello, World! 👋
```

**Instant Function Logging** 🎯
```python
from decorators import logged, timed, performance_monitor

@logged()
def calculate_sum(a, b):
    return a + b

@timed()
def slow_process():
    import time; time.sleep(0.1)
    return "done"

result = calculate_sum(10, 20)  # Automatically logged!
slow_process()  # Automatically timed!
```

## Features

- 🚀 **Zero Config** - Works out of the box with global logger
- ⚡ **Smart Decorators** - `@logged`, `@timed`, `@performance_monitor` and more
- 🎨 **Beautiful Output** - Colored terminal output for better readability
- 🗄️ **Database Support** - MySQL and SQLite appenders for persistent logging
- 📁 **Multiple Outputs** - Console, file, and composite appenders
- 🔧 **Builder Pattern** - Fluent, chainable logger construction when you need it
- 🌍 **Global Management** - Centralized logger registry and management
- 🧩 **Modular Design** - Clean separation of concerns with dependency injection
- 📊 **Multiple Formats** - Simple text and JSON formatting options
- 🔍 **Advanced Filtering** - Keyword and level-based filtering

## Installation

```bash
# Clone the repository
git clone https://github.com/troxeldj/blink-logger.git
cd blink-logger

# Install dependencies (if any)
pip install -r requirements.txt

# Install pre-commit hooks (after installing deps)
pre-commit install

# Run tests to verify installation
python -m pytest tests/ -v
```

## Quick Start - The Pythonic Way

### 1. Simple Logging (Zero Configuration)

```python
# Import and use - no setup required!
from __init__ import get_global_logger

logger = get_global_logger()

# All standard log levels work
logger.debug("Debug info")
logger.info("Application started")
logger.warning("This is a warning")
logger.error("Something went wrong")
logger.critical("Critical error!")
```

### 2. Function Decorators (Instant Logging)

```python
from decorators import logged, timed, performance_monitor, debug_logged
from core.level import LoggingLevel

# Basic function logging
@logged()
def process_data(data):
    return [x * 2 for x in data]

# Custom logging with level and message
@logged(level=LoggingLevel.DEBUG, message="Processing user data")
def process_user(name, age):
    return f"User {name} is {age} years old"

# Performance timing
@timed()
def expensive_operation():
    import time
    time.sleep(0.1)
    return "completed"

# Detailed performance monitoring
@performance_monitor()
def complex_calculation(n):
    return sum(range(n))

# Debug logging with detailed info
@debug_logged()
def api_call(endpoint, params):
    return f"GET {endpoint} with {params}"

# Use them naturally
result = process_data([1, 2, 3, 4])  # Logs input and output
user = process_user("Alice", 30)     # Custom debug message
expensive_operation()                # Times execution
complex_calculation(1000)            # Monitors entry/exit
api_call("/users", {"limit": 10})    # Debug details
```

### 3. Error Handling Decorator

```python
from decorators import error_handler

@error_handler(reraise=False)
def might_fail(value):
    if value < 0:
        raise ValueError("Negative values not allowed")
    return value * 2

# Errors are automatically logged, function returns None on failure
result = might_fail(-5)  # Logs error, returns None
success = might_fail(10) # Returns 20
```

### 4. Combining Decorators (Stack Them!)

```python
from decorators import logged, timed, error_handler

@logged()
@timed()
@error_handler(reraise=False)
def full_featured_function(x, y):
    """This function is logged, timed, and error-handled!"""
    if x < 0 or y < 0:
        raise ValueError("Negative inputs not allowed")
    import time
    time.sleep(0.05)  # Simulate work
    return x * y + 42

# Call it normally - all decorators work together
result = full_featured_function(10, 5)
# Logs: function call, timing, and result
# Handles: any errors gracefully
# Returns: computed result or None if error
```

### 5. Using Custom Loggers with Decorators

All decorators support an optional `logger` parameter to use a specific logger instead of the global one:

```python
from decorators import logged, timed, performance_monitor, debug_logged, error_handler
from builders.logger_builder import LoggerBuilder
from appenders.file_appender import FileAppender
from formatters.simple_formatter import SimpleFormatter

# Create a custom logger for specific components
api_logger = (LoggerBuilder()
    .set_name("API")
    .add_appender(FileAppender("api.log", SimpleFormatter()))
    .build())

# Use decorators with custom logger
@logged(logger=api_logger)
@timed(logger=api_logger)
def api_endpoint(request):
    """This logs to api.log instead of global logger"""
    return f"Processing {request}"

@performance_monitor(logger=api_logger, message="Database operation")
def database_call(query):
    """Custom logger with custom message"""
    return f"Executing: {query}"

# Without logger parameter, uses global logger (default behavior)
@logged()  # Uses global logger
def regular_function():
    return "This uses the global logger"

# Call functions - they log to different destinations
api_endpoint("user_data")      # Logs to api.log
database_call("SELECT * FROM users")  # Logs to api.log
regular_function()             # Logs to global logger (console by default)
```

## Advanced Usage - When You Need More Power

### 1. Custom Global Logger Configuration

```python
from managers.global_manager import GlobalManager
from appenders.file_appender import FileAppender
from formatters.json_formatter import JSONFormatter

# Get and customize the global logger at runtime
global_logger = GlobalManager.get_global_logger()

# Add file logging to global logger
file_appender = FileAppender("app.log", JSONFormatter())
global_logger.add_appender(file_appender)

# Now all logging goes to both console and file
global_logger.info("This goes everywhere!")

# Decorators automatically use the updated global logger
@logged()
def my_function():
    return "This will be logged to console AND file!"
```

### 2. Builder Pattern for Complex Loggers

```python
from builders.logger_builder import LoggerBuilder
from appenders.console_appender import ColoredConsoleAppender
from appenders.file_appender import FileAppender
from appenders.composite_appender import CompositeAppender
from formatters.simple_formatter import SimpleFormatter
from formatters.json_formatter import JSONFormatter
from filters.keyword_filter import KeywordFilter
from filters.level_filter import LevelFilter
from core.level import LoggingLevel
from core.color import ConsoleColor

# Build a sophisticated logger
logger = (LoggerBuilder()
    .set_name("advanced-app")
    .set_level(LoggingLevel.DEBUG)
    .add_appender(
        ColoredConsoleAppender(
            formatter=SimpleFormatter(),
            color=ConsoleColor.CYAN,
            filters=[
                LevelFilter(LoggingLevel.INFO),  # Console: INFO and above
                KeywordFilter(["user", "auth"])  # Console: Only user/auth messages
            ]
        )
    )
    .add_appender(
        FileAppender(
            file_path="debug.log",
            formatter=JSONFormatter()
            # File gets ALL messages (no filters)
        )
    )
    .build())

# Use your custom logger
logger.debug("Database connection opened")  # Only to file
logger.info("User login successful")        # To both (has keywords)
logger.error("Authentication failed")       # To both (has keywords + level)
```

### 3. Multiple Output Destinations

```python
from builders.logger_builder import LoggerBuilder
from appenders.console_appender import ColoredConsoleAppender
from appenders.file_appender import FileAppender
from appenders.composite_appender import CompositeAppender
from formatters.simple_formatter import SimpleFormatter
from formatters.json_formatter import JSONFormatter
from core.color import ConsoleColor

# Multiple appenders in one logger
console = ColoredConsoleAppender(
    formatter=SimpleFormatter(),
    color=ConsoleColor.GREEN
)

json_file = FileAppender("app.json", JSONFormatter())
text_file = FileAppender("app.log", SimpleFormatter())

# Combine all outputs
logger = (LoggerBuilder()
    .set_name("multi-output")
    .add_appender(console)
    .add_appender(json_file)
    .add_appender(text_file)
    .build())

logger.info("This message goes to console, JSON file, AND text file!")
```

### 4. Smart Filtering

```python
from builders.logger_builder import LoggerBuilder
from appenders.console_appender import ConsoleAppender
from filters.keyword_filter import KeywordFilter
from filters.level_filter import LevelFilter
from formatters.simple_formatter import SimpleFormatter
from core.level import LoggingLevel

# Create filtered appenders
error_only = ConsoleAppender(
    formatter=SimpleFormatter(),
    filters=[LevelFilter(LoggingLevel.ERROR)]  # Only errors
)

database_only = ConsoleAppender(
    formatter=SimpleFormatter(),
    filters=[KeywordFilter(["database", "sql", "query"])]  # Only DB messages
)

# Logger with multiple filtered outputs
logger = (LoggerBuilder()
    .set_name("filtered-app")
    .add_appender(error_only)
    .add_appender(database_only)
    .build())

logger.info("User logged in")                    # Not shown (no keywords, not error)
logger.info("Database connection established")   # Shown by database_only
logger.error("Failed to connect to database")   # Shown by BOTH (error + has keyword)
logger.debug("SQL query executed")              # Shown by database_only
```

### 5. Global Logger Management

```python
from managers.global_manager import GlobalManager
from builders.logger_builder import LoggerBuilder
from appenders.console_appender import ConsoleAppender
from formatters.simple_formatter import SimpleFormatter

# All loggers auto-register globally
app_logger = (LoggerBuilder()
    .set_name("app")
    .add_appender(ConsoleAppender(SimpleFormatter()))
    .build())

db_logger = (LoggerBuilder()
    .set_name("database")
    .add_appender(ConsoleAppender(SimpleFormatter()))
    .build())

# Access global manager
manager = GlobalManager.get_instance()
print(f"Total loggers: {len(manager)}")  # Includes global + app + database

# Retrieve any logger by name
retrieved = manager.get_logger("app")
retrieved.info("Retrieved from global manager!")

# List all logger names
for name in manager:
    print(f"Logger: {name}")
```

## Configuration Files (Advanced)

```python
# For complex setups, use configuration files
from config.logger_config import LoggerConfig

# Define in JSON
config_data = {
    "name": "production-app",
    "level": "INFO",
    "appenders": [
        {
            "type": "ColoredConsoleAppender",
            "color": "GREEN",
            "formatter": {"type": "SimpleFormatter"}
        },
        {
            "type": "FileAppender",
            "file_path": "production.log",
            "formatter": {"type": "JSONFormatter"}
        }
    ]
}

# Load configuration
config = LoggerConfig.from_dict(config_data)
logger = LoggerBuilder().from_config(config).build()
```

## Available Components

### Log Levels
```python
from core.level import LoggingLevel

LoggingLevel.DEBUG     # Detailed diagnostic information
LoggingLevel.INFO      # General information messages
LoggingLevel.WARNING   # Warning messages
LoggingLevel.ERROR     # Error messages
LoggingLevel.CRITICAL  # Critical error messages
```

### Colors
```python
from core.color import ConsoleColor

ConsoleColor.RED, ConsoleColor.GREEN, ConsoleColor.YELLOW
ConsoleColor.BLUE, ConsoleColor.MAGENTA, ConsoleColor.CYAN
ConsoleColor.WHITE, ConsoleColor.DEFAULT
```

### Decorators
```python
from decorators import (
    logged,              # Basic function call logging
    timed,              # Execution time measurement
    performance_monitor, # Detailed entry/exit monitoring
    debug_logged,       # Debug-level detailed logging
    error_handler       # Automatic error handling and logging
)
```

### Appenders
```python
from appenders import (
    ConsoleAppender,        # Standard console output
    ColoredConsoleAppender, # Colored console output
    FileAppender,          # File output
    MySQLAppender,         # MySQL database output
    SQLiteAppender,        # SQLite database output
    CompositeAppender      # Multiple appenders combined
)
```

## Real-World Examples

### Web Application Setup
```python
from __init__ import get_global_logger
from decorators import logged, timed, error_handler
from managers.global_manager import GlobalManager
from appenders.file_appender import FileAppender
from formatters.json_formatter import JSONFormatter

# Configure global logger for production
global_logger = GlobalManager.get_global_logger()
global_logger.add_appender(FileAppender("app.log", JSONFormatter()))

# Now all decorators automatically log to console AND file
@logged()
@timed()
@error_handler(reraise=False)
def process_user_request(user_id, action):
    """Process user request with full logging."""
    # Your business logic here
    return f"Processed {action} for user {user_id}"

@performance_monitor()
def database_query(sql, params):
    """Execute database query with monitoring."""
    # Database logic here
    return "query_result"

# Use normally - everything is automatically logged
result = process_user_request(123, "login")
data = database_query("SELECT * FROM users WHERE id = ?", [123])
```

### Microservice Logging
```python
from __init__ import get_global_logger
from decorators import logged, performance_monitor
from core.level import LoggingLevel

# Service-wide logging setup
logger = get_global_logger()
logger.info("Microservice starting up")

@logged(level=LoggingLevel.INFO, message="API endpoint called")
@performance_monitor()
def api_endpoint(request_data):
    """REST API endpoint with full observability."""
    # Process request
    return {"status": "success", "data": request_data}

@logged()
def background_task(job_id):
    """Background job with logging."""
    # Long-running task
    return f"Job {job_id} completed"

# Everything is automatically logged and monitored
api_endpoint({"user": "alice", "action": "get_profile"})
background_task("cleanup-001")
```

## Development

### Running Tests
```bash
# Run all 307 tests
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_decorators.py -v
python -m pytest tests/test_global_manager.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Project Structure
```
blink-logger/
├── core/              # Core logging components
├── appenders/         # Output destinations
├── formatters/        # Message formatting
├── filters/           # Message filtering
├── decorators/        # Function decorators ✨ NEW
├── builders/          # Fluent construction
├── managers/          # Logger management including global ✨ ENHANCED
├── config/            # Configuration support
└── tests/             # Comprehensive test suite (307 tests!)
```

## Why blink-logger?

### Simple Things Are Simple
```python
# Other logging libraries:
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Hello")

# blink-logger:
from __init__ import get_global_logger
get_global_logger().info("Hello")
```

### Powerful Things Are Possible
```python
# Want instant function logging? Just add a decorator!
@logged()
def my_function(): pass

# Want multi-output with filtering? Build it fluently!
logger = (LoggerBuilder()
    .set_name("app")
    .add_appender(console_with_color_filtering)
    .add_appender(file_with_json_formatting)
    .build())
```

### Everything Just Works Together
- Global logger works with decorators automatically
- Custom loggers integrate with global management
- All components are composable and extensible
- Zero circular imports, clean architecture

## Status

🚧 **Hobby Project - Not for Production** 🚧

This is a personal learning project I built for fun and experimentation. While it has comprehensive features and tests, **don't use it in production** unless you enjoy living dangerously! 😄

**Current State:**
- 307 tests passing ✅
- Comprehensive feature coverage ✅
- Clean architecture with zero circular imports ✅
- Fun learning experiment with OOP design patterns ✅

**Coming Eventually (Maybe):**
- Event system integration
- More decorator varieties
- Configuration file templates
- Performance optimizations
- More over-engineering because why not 🤷‍♂️

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`python -m pytest tests/`)
6. Submit a pull request

## License

This project is open source. See the LICENSE file for details.

---

*Made with ☕, Python, and a healthy dose of thoughtful engineering*
