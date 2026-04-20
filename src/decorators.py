# -*- coding: utf-8 -*-
# pylint: disable="wrong-import-order"
# flake8: noqa
"""Count how long func was working."""

import functools
import time as tm
from typing import ParamSpec, TypeVar, Callable

P = ParamSpec('P')
R = TypeVar('R')


def count_time(time_arg: str = 's') -> Callable[[Callable[P, R]], Callable[P, R]]:
    """ How much time func was working
    
    Args:
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
            print(f"\n{func.__name__} {elapsed:.2f}{time_arg}\n")

            return result
        return wrapper
    return decorator