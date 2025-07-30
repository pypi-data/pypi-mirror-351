"""
This module provides a decorator function that securely checks if a certain necessary library is installed before importing it.
"""
import importlib
from functools import wraps
from typing import Callable, TypeVar
T = TypeVar('T', bound=Callable)

def secure_import(module_name: str) -> Callable[[T], T]:
    """
    Decorator to securely import a module, ensuring it is installed before proceeding.

    Args:
        module_name (str): The name of the module to import.

    Returns:
        Callable: A decorator that checks for the module's availability.
    """
    def decorator(func: T) -> T:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                importlib.import_module(module_name)
                return func(*args, **kwargs)
            except ImportError as e:
                print(f"Module '{module_name}' is not installed!")
                return None
        return wrapper
    return decorator


def _silent_secure_import(module_name: str) -> Callable[[T], T]:
    """
    Decorator to silently import a module, ensuring it is installed before proceeding.
    Used by the general seeder function to avoid printing errors if the module is not available.

    Args:
        module_name (str): The name of the module to import.

    Returns:
        Callable: A decorator that checks for the module's availability without printing errors.
    """
    def decorator(func: T) -> T:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                importlib.import_module(module_name)
            except ImportError:
                pass  # Silently ignore the ImportError
            return func(*args, **kwargs)
        return wrapper
    return decorator


def _exception_catcher(package_name: str, func: T) -> T:
    """
    Wrapper function that catches exceptions raised by the wrapped function and logs them.
    Ensures that saatgut doesn't terminate the program if an error occurs during the import or execution of the function.

    Args:
        func (Callable): The function to wrap.
    Returns:
        Callable: The wrapped function that catches exceptions.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred while seeding {package_name}: {e}")
            return None
    return wrapper
