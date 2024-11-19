import os
import sys
from typing import Any, Callable


def blockPrint() -> None:
    """
    Redirects stdout to devnull to suppress print statements.
    """
    sys.stdout = open(os.devnull, 'w')


def enablePrint() -> None:
    """
    Restores stdout to its original state, enabling print statements.
    """
    sys.stdout = sys.__stdout__


def suppress_print(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator that suppresses print statements within the decorated function.

    Args:
        func (Callable): The function to be decorated.

    Returns:
        Callable: The wrapped function with suppressed print statements.
    """
    def wrapper(*args, **kwargs) -> Any:
        blockPrint()
        try:
            result = func(*args, **kwargs)
        finally:
            enablePrint()
        return result
    return wrapper
