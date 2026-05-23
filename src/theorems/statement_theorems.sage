# -*- coding: utf-8 -*-
"""Theorems that must be satisfied under some condition."""

import operator

from decorators import log_calls

from logger_config import main_log

from sage.crypto.boolean_function import BooleanFunction


@log_calls(logger_name=main_log, level='DEBUG')
def theorem_convolution(
        bool_func_1: 'BooleanFunction',
        bool_func_2: 'BooleanFunction',
) -> bool | None:
    """Verify convolution theorem.
    W_{h}(u) = (1/2^n) * sum_x(W_f(x) * W_g(x+u))
    Where h(x) = f(x)+g(x)

    Args:
        bool_func_1: Boolean Function (f)
        bool_func_2: Boolean Function (g)

    Returns:
        True if func's satisfy the theorem, false otherwise
    """
    main_log.debug(
        'Got 2 bool_funcs: (hex({hexval1}) n_vals({nval1}))&(hex({hexval2}) n_vals2({nvals2}))',
        hexval1=bool_func_1.truth_table(format='hex'),
        nval1=bool_func_1.nvariables(),
        hexval2=bool_func_2.truth_table(format='hex'),
        nvals2=bool_func_2.nvariables(),
    )
    if check_func_equal_amount_vars(bool_func_1, bool_func_2, main_log) is False:
        return None

    number_of_variables: int = bool_func_1.nvariables()
    h: 'BooleanFunction' = BooleanFunction(
        [
            operator.xor(bool_func_1(i), bool_func_2(i))
            for i in range(1 << number_of_variables)
        ],
    )

    w_f: list[int] = list(bool_func_1.walsh_hadamard_transform())
    w_g: list[int] = list(bool_func_2.walsh_hadamard_transform())
    w_h: list[int] = list(h.walsh_hadamard_transform())
    main_log.debug('Calculated w_h: {w_h}', w_h=w_h)

    w_h_from_convolution: list[int] = []
    for u_derivative in range(1 << number_of_variables):
        total = sum(
            w_f[x] * w_g[operator.xor(x, u_derivative)]
            for x in range(1 << number_of_variables)
        )
        w_h_from_convolution.append(total / (1 << number_of_variables))

    main_log.debug(
        'Calculated w_h from convolution: {w_h_from_convolution}',
        w_h_from_convolution=w_h_from_convolution,
    )
    return w_h == w_h_from_convolution
