"""
Decorator wrappers for logging function calls and performance monitoring.

This module provides decorators that make it easy to add logging to functions
using the global logger or custom loggers.
"""

import functools
import time
from typing import Callable, Any, Optional
from managers.global_manager import GlobalManager
from core.level import LoggingLevel


def logged(level: LoggingLevel = LoggingLevel.INFO, 
      message: Optional[str] = None,
      include_args: bool = True,
      include_result: bool = True):
  """
  Decorator to log function calls.
  
  Args:
    level: The logging level to use (default: INFO)
    message: Custom message template (default: auto-generated)
    include_args: Whether to include function arguments in the log
    include_result: Whether to include the return value in the log
  
  Example:
    @logged()
    def add(a, b):
      return a + b
      
    @logged(level=LoggingLevel.DEBUG, message="Calculating sum")
    def calculate(x, y):
      return x + y
  """
  def decorator(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
      logger = GlobalManager.get_global_logger()
      
      # Build log message
      func_name = func.__name__
      
      if message:
        call_msg = message
      else:
        call_msg = f"Calling function '{func_name}'"
      
      if include_args and (args or kwargs):
        args_str = ", ".join([repr(arg) for arg in args])
        kwargs_str = ", ".join([f"{k}={repr(v)}" for k, v in kwargs.items()])
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))
        call_msg += f" with args: ({all_args})"
      
      # Log function call
      logger.log(level, call_msg)
      
      # Execute function
      try:
        result = func(*args, **kwargs)
        
        if include_result:
          result_msg = f"Function '{func_name}' returned: {repr(result)}"
          logger.log(level, result_msg)
        
        return result
        
      except Exception as e:
        error_msg = f"Function '{func_name}' raised exception: {type(e).__name__}: {e}"
        logger.error(error_msg)
        raise
        
    return wrapper
  return decorator


def timed(level: LoggingLevel = LoggingLevel.INFO,
     threshold_ms: Optional[float] = None):
  """
  Decorator to log function execution time.
  
  Args:
    level: The logging level to use (default: INFO)
    threshold_ms: Only log if execution time exceeds this threshold in milliseconds
  
  Example:
    @timed()
    def slow_function():
      time.sleep(1)
      
    @timed(threshold_ms=100, level=LoggingLevel.WARNING)
    def potentially_slow():
      # Only logs if takes more than 100ms
      pass
  """
  def decorator(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
      logger = GlobalManager.get_global_logger()
      func_name = func.__name__
      
      start_time = time.perf_counter()
      
      try:
        result = func(*args, **kwargs)
        return result
      finally:
        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000
        
        # Only log if no threshold or threshold exceeded
        if threshold_ms is None or execution_time_ms >= threshold_ms:
          time_msg = f"Function '{func_name}' executed in {execution_time_ms:.2f}ms"
          logger.log(level, time_msg)
          
    return wrapper
  return decorator


def performance_monitor(level: LoggingLevel = LoggingLevel.DEBUG):
  """
  Decorator that combines logging and timing for comprehensive performance monitoring.
  
  Args:
    level: The logging level to use (default: DEBUG)
  
  Example:
    @performance_monitor()
    def complex_calculation(data):
      return sum(data)
  """
  def decorator(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
      logger = GlobalManager.get_global_logger()
      func_name = func.__name__
      
      # Log function entry
      logger.log(level, f"ENTER: {func_name}")
      
      start_time = time.perf_counter()
      
      try:
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000
        
        # Log successful exit with timing
        logger.log(level, f"EXIT: {func_name} (success, {execution_time_ms:.2f}ms)")
        return result
        
      except Exception as e:
        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000
        
        # Log exception exit with timing
        logger.log(level, f"EXIT: {func_name} (exception: {type(e).__name__}, {execution_time_ms:.2f}ms)")
        raise
        
    return wrapper
  return decorator


def debug_logged(func: Callable) -> Callable:
  """
  Convenience decorator for debug-level logging with full details.
  Equivalent to @logged(level=LoggingLevel.DEBUG, include_args=True, include_result=True)
  """
  return logged(level=LoggingLevel.DEBUG, include_args=True, include_result=True)(func)


def error_handler(reraise: bool = False, level: LoggingLevel = LoggingLevel.ERROR):
  """
  Decorator to log exceptions without stopping execution (optionally).
  
  Args:
    reraise: Whether to re-raise the exception after logging (default: True)
    level: The logging level for error messages
  
  Example:
    @error_handler(reraise=False)
    def might_fail():
      raise ValueError("Something went wrong")
      # Logs the error but doesn't crash the program
  """
  def decorator(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
      logger = GlobalManager.get_global_logger()
      func_name = func.__name__
      
      try:
        return func(*args, **kwargs)
      except Exception as e:
        error_msg = f"Exception in '{func_name}': {type(e).__name__}: {e}"
        logger.log(level, error_msg)
        
        if reraise:
          raise
        else:
          return None
          
    return wrapper
  return decorator

def combine_decorators(*decorators: Callable) -> Callable:
  """
		Combine multiple decorators into one.
		
		Args:
				*decorators: List of decorators to combine
		
		Example:
				@combine_decorators(logged(), timed())
				def my_function():
						pass
		"""
  def combined_decorator(func: Callable) -> Callable:
    for decorator in reversed(decorators):
      func = decorator(func)
    return func
  return combined_decorator

