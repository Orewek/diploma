# -*- coding: utf-8 -*-
"""Count how long func was working."""

import functools
import time as tm

from collections.abc import Callable

import logging
from typing import ParamSpec, TypeVar

P = ParamSpec('P')
R = TypeVar('R')


def count_time(time_arg: str = 's') -> Callable[[Callable[P, R]], Callable[P, R]]:
    """How much time func was working.

    Args:
    -----
        time_arg: ('min', 's', 'ms', 'us')
    """
    time_dict: dict[str, float] = {
        'min': 60,
        's': 1,
        'ms': 1e-3,
        'us': 1e-6,
    }
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start: float = tm.perf_counter()
            result: R = func(*args, **kwargs)
            elapsed: float = (tm.perf_counter() - start) / time_dict.get(time_arg, 1.0)
            print(f'\n{func.__name__} {elapsed:.2f}{time_arg}\n')

            return result
        return wrapper
    return decorator


def log_calls(
        logger_name: logging.Logger = logging.getLogger(),
        level: str = 'INFO',
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            log_method = getattr(logger_name, level.lower(), logger_name.info)
            func_name: str = func.__name__
            log_method('Start ({%s})', func_name)
            try:
                result: R = func(*args, **kwargs)
                log_method('End ({%s})', func_name)
                return result
            except Exception as e:
                logger_name.error('Error in {1}: {2}', func_name, e)
                raise
        return wrapper
    return decorator
