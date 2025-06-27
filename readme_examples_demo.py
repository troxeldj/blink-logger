#!/usr/bin/env python3
"""
README Examples Demo - Showcasing the new Pythonic features
"""

print("=== README Examples Demo ===\n")

# 1. Zero Configuration Logging
print("1. Zero Configuration Logging:")
from __init__ import get_global_logger

logger = get_global_logger()
logger.info("Hello, World! 👋")
print()

# 2. Function Decorators
print("2. Function Decorators:")
from decorators import logged, timed, performance_monitor, debug_logged
from core.level import LoggingLevel

@logged()
def process_data(data):
    return [x * 2 for x in data]

@logged(level=LoggingLevel.DEBUG, message="Processing user data")
def process_user(name, age):
    return f"User {name} is {age} years old"

@timed()
def expensive_operation():
    import time
    time.sleep(0.05)
    return "completed"

@performance_monitor()
def complex_calculation(n):
    return sum(range(n))

# Use them naturally
result = process_data([1, 2, 3, 4])
print(f"Process data result: {result}")

user = process_user("Alice", 30)
print(f"Process user result: {user}")

expensive_operation()
complex_calculation(100)
print()

# 3. Error Handling Decorator
print("3. Error Handling Decorator:")
from decorators import error_handler

@error_handler(reraise=False)
def might_fail(value):
    if value < 0:
        raise ValueError("Negative values not allowed")
    return value * 2

result_fail = might_fail(-5)  # Logs error, returns None
result_success = might_fail(10)  # Returns 20
print(f"Failed result: {result_fail}, Success result: {result_success}")
print()

# 4. Combining Decorators
print("4. Combining Decorators:")

@logged()
@timed() 
@error_handler(reraise=False)
def full_featured_function(x, y):
    """This function is logged, timed, and error-handled!"""
    if x < 0 or y < 0:
        raise ValueError("Negative inputs not allowed")
    import time
    time.sleep(0.02)  # Simulate work
    return x * y + 42

result = full_featured_function(10, 5)
print(f"Full featured result: {result}")

# Try with error
error_result = full_featured_function(-1, 5)
print(f"Error result: {error_result}")
print()

# 5. Advanced: Custom Global Logger Configuration
print("5. Advanced: Custom Global Logger Configuration:")
from managers.global_manager import GlobalManager
from appenders.file_appender import FileAppender
from formatters.json_formatter import JSONFormatter

# Get and customize the global logger at runtime
global_logger = GlobalManager.get_global_logger()

# Add file logging to global logger (temporarily for demo)
file_appender = FileAppender("demo.log", JSONFormatter())
global_logger.add_appender(file_appender)

global_logger.info("This goes to both console and file!")

# Decorators automatically use the updated global logger
@logged()
def my_function():
    return "This will be logged to console AND file!"

result = my_function()
print(f"My function result: {result}")

# Clean up - remove file appender
global_logger.remove_appender(file_appender)
print()

# 6. Real-world example: Web Application Setup
print("6. Real-world example: Web Application Setup:")

@logged()
@timed()
@error_handler(reraise=False)
def process_user_request(user_id, action):
    """Process user request with full logging."""
    if action == "invalid":
        raise ValueError("Invalid action requested")
    return f"Processed {action} for user {user_id}"

@performance_monitor()
def database_query(sql, params):
    """Execute database query with monitoring."""
    import time
    time.sleep(0.01)  # Simulate DB query
    return f"Query result for: {sql}"

# Use normally - everything is automatically logged
result = process_user_request(123, "login")
print(f"User request result: {result}")

data = database_query("SELECT * FROM users WHERE id = ?", [123])
print(f"Database result: {data}")

# Test error handling
error_result = process_user_request(456, "invalid")
print(f"Error request result: {error_result}")

print("\n=== Demo Complete! ===")
print("Check 'demo.log' file for JSON formatted logs!")
