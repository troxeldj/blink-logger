# Decorator to mark a function as throwing specific exceptions.
# This can be used for documentation or static analysis purposes.
# Example usage:
# @throws(ValueError, KeyError)
# def my_function():
#     raise ValueError("An error occurred")
def throws(*exceptions: type[BaseException]):
    def decorator(func):
        func.__throws__ = exceptions
        return func
    return decorator

def params(*args, **kwargs):
		"""
		Decorator to mark a function as having specific parameters.
		This can be used for documentation or static analysis purposes.
		
		Example usage:
		@params(user_id=int, action=str)
		def log_action(user_id, action):
				pass
		"""
		def decorator(func):
				func.__params__ = {'args': args, 'kwargs': kwargs}
				return func
		return decorator