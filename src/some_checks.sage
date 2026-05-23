# -*- coding: utf-8 -*-
# mypy: disable-error-code="import-not-found"
"""Verification for many things in code."""


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sage.crypto.boolean_function import BooleanFunction
    from loguru._logger import Logger


def check_func_equal_amount_vars(
        bool_func_1: 'BooleanFunction',
        bool_func_2: 'BooleanFunction',
        log: 'Logger | None' = None,
) -> bool:
    """check if f and g have same amount of variables

    Args:
    -----
        bool_func_1: Boolean Function (f)
        bool_func_2: Boolean Function (g)
        log: logger that log error (if logger exists)

    Returns:
    --------
        list of all cross correlations of f and g by all possible derivatives u
    """
    res: bool = bool_func_1.nvariables() == bool_func_2.nvariables()

    if res is False and log is not None:
        log.debug('Bool Functions dont have same amount of variables')

    return res
