#!/usr/bin/env python3
"""
Test script for decorator functionality
"""

import sys
import os
import time

# Add the parent directory to the path to allow imports from the main library
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decorators import (
    logged, timed, performance_monitor, debug_logged, error_handler
)
from managers.global_manager import GlobalManager
from core.level import LoggingLevel

# Global logger access function
def get_global_logger():
    return GlobalManager.get_global_logger()

print('✅ Decorator imports successful!')

# Test basic logging decorator
@logged()
def add_numbers(a, b):
    """Simple function to test basic logging."""
    return a + b

# Test timed decorator
@timed()
def slow_operation():
    """Function that takes some time."""
    time.sleep(0.1)  # 100ms
    return "completed"

# Test performance monitor
@performance_monitor()
def complex_calculation(numbers):
    """Function for performance monitoring."""
    return sum(x**2 for x in numbers)

# Test debug logging
@debug_logged
def detailed_function(name, age):
    """Function with detailed debug logging."""
    return f"Hello {name}, you are {age} years old"

# Test error handler
@error_handler(reraise=False)
def might_fail(should_fail=False):
    """Function that might raise an exception."""
    if should_fail:
        raise ValueError("Something went wrong!")
    return "success"

# Test combinations
@timed(threshold_ms=50)
@logged(level=LoggingLevel.INFO, message="Executing combined function")
def combined_decorators(x, y):
    """Function with multiple decorators."""
    time.sleep(0.06)  # 60ms - above threshold
    return x * y

def test_decorators():
    """Test all decorator functionality."""
    print("\n=== Testing Decorators ===")
    
    # Test global logger access
    global_logger = get_global_logger()
    global_logger.info("Testing decorator functionality")
    
    # Test basic logging
    print("\n1. Testing @logged decorator:")
    result = add_numbers(5, 3)
    print(f"   Result: {result}")
    
    # Test timing
    print("\n2. Testing @timed decorator:")
    result = slow_operation()
    print(f"   Result: {result}")
    
    # Test performance monitoring
    print("\n3. Testing @performance_monitor decorator:")
    result = complex_calculation([1, 2, 3, 4, 5])
    print(f"   Result: {result}")
    
    # Test debug logging
    print("\n4. Testing @debug_logged decorator:")
    result = detailed_function("Alice", 25)
    print(f"   Result: {result}")
    
    # Test error handling
    print("\n5. Testing @error_handler decorator:")
    result1 = might_fail(should_fail=False)
    print(f"   Success result: {result1}")
    
    result2 = might_fail(should_fail=True)
    print(f"   Error result: {result2}")
    
    # Test combined decorators
    print("\n6. Testing combined decorators:")
    result = combined_decorators(4, 7)
    print(f"   Result: {result}")
    
    print("\n✅ All decorator tests completed!")

if __name__ == "__main__":
    test_decorators()
