# Decorator to mark a function as throwing specific exceptions.
# This can be used for documentation or static analysis purposes.
# Example usage:
# @throws(ValueError, KeyError)
# def my_function():
#   raise ValueError("An error occurred")
def throws(*exceptions: type[BaseException]):
    def decorator(func):
        func.__throws__ = exceptions
        return func

    return decorator


"""
# Decorator to mark a function as having specific parameters.
# This can be used for documentation or static analysis purposes.
# Example usage:
# @params(user_id=int, action=str)
# def log_action(user_id, action):
#   pass
"""


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
        func.__params__ = {"args": args, "kwargs": kwargs}
        return func

    return decorator


def returns(return_type: type):
    """
    Decorator to mark a function as returning a specific type.
    This can be used for documentation or static analysis purposes.

    Example usage:
    @returns(str)
    def get_username(user_id):
            return "username"
    """

    def decorator(func):
        func.__return_type__ = return_type
        return func

    return decorator


def deprecated(message: str):
    """
    Decorator to mark a function as deprecated.
    This can be used for documentation or static analysis purposes.

    Example usage:
    @deprecated("This function will be removed in future versions.")
    def old_function():
            pass
    """

    def decorator(func):
        func.__deprecated__ = message
        return func

    return decorator


def metadata(**kwargs):
    """
    Decorator to add metadata to a function.
    This can be used for documentation or static analysis purposes.

    Example usage:
    @metadata(author="John Doe", version="1.0")
    def my_function():
            pass
    """

    def decorator(func):
        func.__metadata__ = kwargs
        return func

    return decorator


def example(input: str, output: str):
    """
    Decorator to provide an example input and output for a function.
    This can be used for documentation or static analysis purposes.

    Example usage:
    @example(input="Hello, World!", output="Hello, World!")
    def greet(name):
            return f"Hello, {name}!"
    """

    def decorator(func):
        func.__example__ = {"input": input, "output": output}
        return func

    return decorator
