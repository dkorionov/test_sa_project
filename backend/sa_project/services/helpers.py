from functools import wraps
from typing import List


def prefetch_related(related_fields: List[str]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            queryset = func(*args, **kwargs)
            return queryset.prefetch_related("".join(related_fields))

        return wrapper

    return decorator


def select_related(related_fields: List[str]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            queryset = func(*args, **kwargs)
            return queryset.select_related("".join(related_fields))

        return wrapper

    return decorator
