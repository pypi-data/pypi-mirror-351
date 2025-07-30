import functools
import logging
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def disney_property(
    refresh: bool = True, default_value: Optional[T] = None
) -> Callable[[Callable[[Any], Optional[T]]], property]:
    def decorator(func: Callable) -> property:
        @functools.wraps(func)
        def wrapper(self) -> Optional[T]:
            if refresh:
                self.refresh()
            try:
                return func(self)
            except (KeyError, TypeError, ValueError):
                return default_value

        wrapper.__annotations__ = func.__annotations__
        wrapper.__doc__ = func.__doc__
        return property(wrapper)

    return decorator


def json_property(func: Callable) -> property:
    @property
    @functools.wraps(func)
    def wrapper(self) -> Any:
        try:
            return func(self)
        except (KeyError, TypeError, ValueError):
            return None

    return wrapper
