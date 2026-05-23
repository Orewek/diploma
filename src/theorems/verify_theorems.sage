# -*- coding: utf-8 -*-
# mypy: disable-error-code="import-not-found"
"""Theorems that must be satisfied any time."""

from typing import TYPE_CHECKING

from decorators import log_calls

from logger_config import main_log

if TYPE_CHECKING:
    from sage.crypto.boolean_function import BooleanFunction


@log_calls(logger_name=main_log, level='DEBUG')
def verify_inequality(bool_func: 'BooleanFunction') -> bool:
    """Verify that cardinality of non-zero correlations * cardinality NW_f >= 2**n.

    Args:
    -----
        bool_func: Boolean Function (f)

    Returns:
    --------
        True/False
    """
    # note: non ci_f equals to NW_f
    # non ci_f = v_n - ci_f
    main_log.debug(
        'Got a bool function: hex({hex_value}) num_val({number_of_variables})',
        hex_value=bool_func.truth_table(format='hex'),
        number_of_variables=bool_func.nvariables(),
    )
    non_ci_f = (1 << bool_func.nvariables()) - len(get_ci_function(bool_func))
    n_delta_f = sum(1 for corr in bool_func.absolute_autocorrelation() if corr != 0)
    main_log.debug(
        'Calculated non_ci_f: {non_ci_f}; n_delta_f: {n_delta_f}',
        non_ci_f=non_ci_f,
        n_delta_f=n_delta_f,
    )

    return n_delta_f * non_ci_f >= (1 << bool_func.nvariables())


@log_calls(logger_name=main_log, level='DEBUG')
def max_sum_corr_theorem(
        bool_func_1: 'BooleanFunction',
        bool_func_2: 'BooleanFunction',
) -> bool | None:
    """Check theorem that sum cross_corr ** 2 <= 2^3n.

    Args:
    -----
        bool_func_1: Boolean Function (f)
        bool_func_2: Boolean Function (g)

    Returns:
    --------
        True/False, None if amount of variables in f and g not equal
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

    sum_sq_cross_corr: int = sum(x**2 for x in all_cross_correlations(bool_func_1, bool_func_2))
    main_log.debug(
        'Got the sum of x**2 of all cross_correlations: {sum_sq_cross_corr}',
        sum_sq_cross_corr=sum_sq_cross_corr,
    )

    return sum_sq_cross_corr <= (1 << (3 * bool_func_1.nvariables()))


@log_calls(logger_name=main_log, level='DEBUG')
def theorem_about_cross_correlation(
        bool_func_1: 'BooleanFunction',
        bool_func_2: 'BooleanFunction',
) -> bool | None:
    """Check that x * y = z.
    x = (vector of cross_correlations lenght of n)
    y = (hadamard matrix of order n)
    z = V_n: Walsh_hadamard coeff: (W_f(0) * W_g(0), ... , W_f(2^n - 1) * W_g(2^n - 1))

    Args:
    -----
        bool_func_1: Boolean Function (f)
        bool_func_2: Boolean Function (g)

    Returns:
    --------
        None if not equal variables, True if x * y = z, otherwise False
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

    vector_of_cross_correlations: list[int] | None = all_cross_correlations(
        bool_func_1,
        bool_func_2,
    )
    if vector_of_cross_correlations is None:
        return None

    bool_func_1_walsh_coef: list[int] = bool_func_1.walsh_hadamard_transform()
    bool_func_2_walsh_coef: list[int] = bool_func_2.walsh_hadamard_transform()

    walsh_coef_product: list[int] = [
        bool_func_1_walsh_coef[i] * bool_func_2_walsh_coef[i]
        for i in range(len(bool_func_1_walsh_coef))
    ]

    return fwht(vector_of_cross_correlations) == walsh_coef_product


@log_calls(logger_name=main_log, level='DEBUG')
def verify_parsevals_identity(w_walsh: tuple[int, ...], number_of_variables: int) -> bool:
    """Check are w_walsh coefficients correct by parseval's identity.

    Args:
    -----
        w_walsh: walsh coefficients
        number_of_variables:

    Returns:
        True if correct, otherwise False
    """
    main_log.debug('Got walsh coeff: {walsh_coef}', walsh_coef=w_walsh)

    return sum(coef**2 for coef in w_walsh) == (1 << (2 * number_of_variables))
