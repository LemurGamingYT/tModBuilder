from typing import Callable, Union
from functools import wraps


def overload(base: Union[Callable, None] = None):
    def decorator(func: Callable):
        if base is not None:
            getattr(func, 'overloads', []).append(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            functions = [func] + getattr(func, 'overloads', [])
            for f in functions:
                try:
                    return f(*args, **kwargs)
                except TypeError:
                    pass
            
            raise TypeError(f'No overload for {func.__name__}')
        
        return wrapper
    
    return decorator
