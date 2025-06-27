# blink-logger 📝

A pure object-oriented Python logging library built from scratch with a focus on simplicity and power.

## ✨ What's New - Global Logger & Decorators

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

- � **Zero Config** - Works out of the box with global logger
- ⚡ **Smart Decorators** - `@logged`, `@timed`, `@performance_monitor` and more
- 🎨 **Beautiful Output** - Colored terminal output for better readability
- 📄 **Multiple Outputs** - Console, file, and composite appenders
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
# Run all 256 tests
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
└── tests/             # Comprehensive test suite (256 tests!)
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

✅ **Production Ready Features**
- 256 tests passing
- Zero configuration global logger
- Smart decorators for functions
- Advanced filtering and formatting
- Multiple output destinations
- Global logger management
- Builder pattern for complex scenarios

🚧 **Coming Soon**
- Event system integration
- More decorator varieties
- Configuration file templates
- Performance optimizations

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
)
file_appender = FileAppender(
    file_path="debug.log",
    formatter=SimpleFormatter()
)

# Combine them
composite = CompositeAppender(appenders=[console_appender, file_appender])

logger = (LoggerBuilder()
    .set_name("multi-output")
    .set_level(LoggingLevel.DEBUG)
    .set_formatter(SimpleFormatter())
    .add_appender(composite)
    .build())

logger.log(LoggingLevel.INFO, "This goes to both console and file!")
```

#### Filtering Messages

```python
from builders.logger_builder import LoggerBuilder
from appenders.console_appender import ConsoleAppender
from formatters.simple_formatter import SimpleFormatter
from filters.keyword_filter import KeywordFilter
from filters.level_filter import LevelFilter
from core.level import LoggingLevel

# Create appender with filters
filtered_appender = ConsoleAppender(
    formatter=SimpleFormatter(),
    filters=[
        KeywordFilter(["error", "critical"]),  # Only messages containing these keywords
        LevelFilter(LoggingLevel.WARNING)      # Only WARNING level and above
    ]
)

logger = (LoggerBuilder()
    .set_name("filtered-logger")
    .set_level(LoggingLevel.DEBUG)
    .set_formatter(SimpleFormatter())
    .add_appender(filtered_appender)
    .build())

logger.log(LoggingLevel.INFO, "This will be filtered out")
logger.log(LoggingLevel.ERROR, "This error message will show")
```

#### Global Logger Management

```python
from managers.global_manager import GlobalManager
from builders.logger_builder import LoggerBuilder
from appenders.console_appender import ConsoleAppender
from formatters.simple_formatter import SimpleFormatter
from core.level import LoggingLevel

# Loggers are automatically registered globally when created
logger1 = (LoggerBuilder()
    .set_name("app-logger")
    .set_level(LoggingLevel.INFO)
    .set_formatter(SimpleFormatter())
    .add_appender(ConsoleAppender())
    .build())

# Access global manager
global_mgr = GlobalManager.get_instance()
print(f"Total loggers: {len(global_mgr)}")

# Retrieve logger by name
retrieved_logger = global_mgr.get_logger("app-logger")
retrieved_logger.log(LoggingLevel.INFO, "Retrieved from global manager!")
```

#### Convenience Functions

```python
# Use built-in convenience functions for quick setup
from __init__ import create_simple_logger, create_colored_logger
from core.level import LoggingLevel
from core.color import ConsoleColor

# Simple console logger
simple = create_simple_logger("simple", LoggingLevel.DEBUG)

# Colored console logger  
colored = create_colored_logger("colored", LoggingLevel.INFO, ConsoleColor.MAGENTA)

simple.log(LoggingLevel.INFO, "Simple logging")
colored.log(LoggingLevel.INFO, "Colored logging")
```

### Available Log Levels

```python
from core.level import LoggingLevel

# Available levels (in order of severity)
LoggingLevel.DEBUG     # Detailed diagnostic information
LoggingLevel.INFO      # General information messages
LoggingLevel.WARNING   # Warning messages
LoggingLevel.ERROR     # Error messages
LoggingLevel.CRITICAL  # Critical error messages
```

### Available Colors

```python
from core.color import ConsoleColor

# Available terminal colors
ConsoleColor.RED
ConsoleColor.GREEN  
ConsoleColor.YELLOW
ConsoleColor.BLUE
ConsoleColor.MAGENTA
ConsoleColor.CYAN
ConsoleColor.WHITE
ConsoleColor.DEFAULT
```

## Development

### Running Tests

The library includes a comprehensive test suite with 211+ tests covering all components:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_appenders.py -v
python -m pytest tests/test_filters.py -v
python -m pytest tests/test_builders.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Project Structure

```
blink-logger/
├── core/              # Core logging components
│   ├── logger.py      # Main Logger class
│   ├── level.py       # LoggingLevel enum
│   ├── record.py      # LogRecord data structure
│   └── color.py       # Console color definitions
├── appenders/         # Output destinations
│   ├── base_appender.py
│   ├── console_appender.py
│   ├── file_appender.py
│   └── composite_appender.py
├── formatters/        # Message formatting
│   ├── base_formatter.py
│   ├── simple_formatter.py
│   └── json_formatter.py
├── filters/           # Message filtering
│   ├── base_filter.py
│   ├── keyword_filter.py
│   └── level_filter.py
├── builders/          # Fluent construction
│   └── logger_builder.py
├── managers/          # Logger management
│   ├── log_manager.py
│   └── global_manager.py
└── utils/             # Utility decorators
    └── dec.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Status

🚧 **Work in Progress** 🚧

This is a hobby project I'm tinkering with. Don't use it in production unless you enjoy living dangerously.

- All 211 tests passing
- No circular import issues  
- Comprehensive feature coverage
- Fun learning experiment with OOP design patterns

## TODO

- An OOP event system
- A simple decorator wrapper
- more to come...

## Credits

- **Development**: Built with curiosity and too much free time (Credit to Google and StackOverflow)
- **Testing**: Comprehensive test suite developed with assistance from **Claude Sonnet 3.5** via GitHub Copilot Chat
- **Architecture**: Inspired by modern logging frameworks with a focus on clean, modular design

## License

This project is open source. See the LICENSE file for details.

---

*Made with ☕, Python, and a healthy dose of over-engineering*
