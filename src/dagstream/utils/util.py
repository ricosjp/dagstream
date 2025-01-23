import types
from collections.abc import Callable


def get_function_name(user_function: Callable) -> str:
    if isinstance(user_function, types.FunctionType):
        return user_function.__name__
    else:
        return user_function.__class__.__name__
