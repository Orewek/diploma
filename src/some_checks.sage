# -*- coding: utf-8 -*-
# pylint: disable="wrong-import-order"
# mypy: disable-error-code="import-not-found"
"""Verification for many things in code."""


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sage.crypto.boolean_function import BooleanFunction


def check_func_equal_amount_vars(
        bool_func_1: 'BooleanFunction',
        bool_func_2: 'BooleanFunction',
) -> bool:
    """check if f and g have same amount of variables

    Args:
    -----
        bool_func_1: Boolean Function (f)
        bool_func_2: Boolean Function (g)

    Returns:
    --------
        list of all cross correlations of f and g by all possible derivatives u
    """
    return bool_func_1.nvariables() == bool_func_2.nvariables()
