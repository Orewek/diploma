# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-order
"""Main module."""
import itertools
import math
import operator
import sys
import time as tm
from typing import TYPE_CHECKING

from sage.combinat.matrices.hadamard_matrix import hadamard_matrix
from sage.crypto.boolean_function import (
    BooleanFunction,
    random_boolean_function,
)
from sage.rings.integer import Integer

if TYPE_CHECKING:
    from sage.matrix.matrix_integer_dense import Matrix_integer_dense
    from sage.modules.vector_mod2_dense import Vector_mod_2_dense
    from sage.rings.finite_rings.integer_mod import IntegerMod_Int
    from sage.rings.polynomial.pbori import BooleanPolynomial
    from sage.rings.polynomial.pbori.pbori import BooleanMonomial, BooleanPolynomialRing

from pathlib import Path

from src.decorators import log_calls
from logger_config import main_log


@log_calls(logger_name=main_log, level='DEBUG')
def sac(bool_func: 'BooleanFunction') -> int:
    """Calculate SAC (strict avalanche criterion) for function.

    Args:
    -----
        bool_func: Boolean Function

    Returns:
    --------
        degree k/SAC(k); 0 <= k < number of variables.
    """
    number_of_variables: int = bool_func.nvariables()
    main_log.debug(
        'Got a bool function: hex({hex_value}) num_val({number_of_variables})',
        hex_value=bool_func.truth_table(format='hex'),
        number_of_variables=number_of_variables,
    )
    poly: 'BooleanPolynomial' = bool_func.algebraic_normal_form()
    variables_of_bool_func: tuple['BooleanMonomial'] = poly.parent().gens()
    for k_degree in range(1, number_of_variables):
        # Going through all combinations of k variables that we are going to fix
        for indices in itertools.combinations(range(number_of_variables), k_degree):
            # That k variables that we have chosen need to equate to 0 or 1
            # There is 1 << k options to do that
            for values in itertools.product([0, 1], repeat=k_degree):
                # Put variables that we have chosen into new polynomial
                sub_poly: 'BooleanPolynomial' = poly.subs(
                    {variables_of_bool_func[idx]: val for idx, val in zip(indices, values)},
                )
                sub_anf: 'BooleanPolynomial' = BooleanFunction(sub_poly).algebraic_normal_form()
                # sage still thinks that there are 'n' variables in polynomial even if some
                # variable is 'missing' it is does not matter so to get a true amount of
                # variables of subfunction (to correctly calculate truth table and derivatives)
                # we have to create a new polynomial Ring with 'n - k' degree and put the
                # variables that use the subfunction after that can create a new boolean
                # function with and an old anf and even sage was thinking about the wrong amount
                # of variables still and was correct
                used_vars: tuple['BooleanMonomial', ...] = sub_anf.variables()
                # Создаём новую функцию только от используемых переменных
                if len(used_vars) > 0:
                    new_r: 'BooleanPolynomialRing' = BooleanPolynomialRing(
                        len(used_vars),
                        names=[str(v) for v in used_vars],
                    )
                    sub_bf: 'BooleanFunction' = BooleanFunction(new_r(str(sub_anf)))

                else:
                    # if subfunction uses no variables (equals to constant)
                    # it means subfunction cant be balanced
                    main_log.debug(
                        'Subfunction is constant, returning k=({k})',
                        k=k_degree - 1,
                    )
                    return k_degree - 1

                act: tuple[int, ...] = sub_bf.autocorrelation()
                # calculate autocorrelation and look at derivatives that wt(u) = 1
                # so for n = 3 it is going to be [1 0 0] [0 1 0] [0 0 1]
                if all(act[1 << i] == 0 for i in range(sub_bf.nvariables())) is False:
                    main_log.debug(
                        'sub_func.derivatite(u) != 0, returning k=({k})',
                        k=k_degree - 1,
                    )
                    return k_degree - 1

    main_log.debug(
        'function passes all iterations, returning k=({k})',
        k=number_of_variables - 1,
    )
    return number_of_variables - 1


@log_calls(logger_name=main_log, level='DEBUG')
def verify_inequality(bool_func: 'BooleanFunction') -> bool:
    """Verify that cardinality of non-zero correlations * cardinality NW_f >= 2**n

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
    non_ci_f = (1 << bool_func.nvariables()) - len(get_CI_function(bool_func))
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
def get_CI_function(bool_func: 'BooleanFunction') -> list[int]:
    """Get CI_f of the function.

    Args:
    -----
        bool_func: Boolean Function (f)

    Returns:
    --------
        list of all u_deviratives that W_f(u) = 0
    """
    main_log.debug(
        'Got a bool function: hex({hex_value}) num_val({number_of_variables})',
        hex_value=bool_func.truth_table(format='hex'),
        number_of_variables=bool_func.nvariables(),
    )
    ci_f: list[int] = [_ for _, val in enumerate(bool_func.walsh_hadamard_transform()) if val == 0]
    main_log.debug('Calculated the ci_f: {ci_f}', ci_f=ci_f)

    return ci_f


@log_calls(logger_name=main_log, level='DEBUG')
def get_intersecting_spectral(
        bool_func_1: 'BooleanFunction',
        bool_func_2: 'BooleanFunction',
) -> set | bool | None:
    """Calculate intersecting spectral.

    Args:
    -----
        bool_func_1: Boolean Function (f)
        bool_func_2: Boolean Function (g)

    Returns:
    --------
        set if intersecting correlated, otherwise False
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

    ci_f = set(get_CI_function(bool_func_1))
    ci_g = set(get_CI_function(bool_func_2))

    intersection = ci_f.intersection(ci_g)
    main_log.debug('Calculated intersection: {intersection}', intersection=intersection)

    return intersection if intersection else False


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
        w_h_from_convolution.append(total // (1 << number_of_variables))

    main_log.debug(
        'Calculated w_h from convolution: {w_h_from_convolution}',
        w_h_from_convolution=w_h_from_convolution,
    )
    return w_h == w_h_from_convolution


@log_calls(logger_name=main_log, level='DEBUG')
def fwht(vector: list[int]) -> list[int]:
    """Fast Walsh-hadamard transofrmation.
    Muptiply vector of len 2^n on hadamard matrix of order 2^n

    Advantage of that method compared to simple creation of H of order n
    is that we dont need to create the whole matrix.
    By that we use O(N*logN) of memory instead of O(N*N).

    Args:
    -----
        Vector:

    Returns:
    --------
        vector * hadamard matrix
    """
    # Method that used to calculate the vector called
    # Butterfly algorithm / FFT
    number_of_components: int = len(vector)
    step = 1
    while step < number_of_components:
        for i in range(0, number_of_components, step << 1):
            for j in range(i, i + step):
                x = vector[j]
                y = vector[j + step]
                vector[j] = x + y
                vector[j + step] = x - y

        step <<= 1

    return vector


@log_calls(logger_name=main_log, level='DEBUG')
def theorem_about_cross_correlation(
        bool_func_1: 'BooleanFunction',
        bool_func_2: 'BooleanFunction',
) -> bool | None:
    """Check that x * y = z.
    x = (vector of cross_correlations lenght of n)
    y = (hadamard matrix of order n)
    z = vector of length n: Walsh_hadamard coeff: (W_f(0) * W_g(0), ... , W_f(2^n - 1) * W_g(2^n - 1))

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
def fast_sylvester_hadamard(matrix_order: int) -> 'Matrix_integer_dense':
    """Get a hadammard matrix type of sylvester.

    Args:
    -----
        matrix_order: order of the matrix 2**n.

    Returns:
        hadammard matrix
    """
    # [!] possible to calculate the matrix if matrix order <= 13
    # using standard method and hoping for the best
    if matrix_order >= 14:
        return hadamard_matrix(1 << matrix_order)

    if matrix_order == 0:
        return matrix([[1]])

    h_prev = fast_sylvester_hadamard(matrix_order - 1)

    return block_matrix(
        [
            [h_prev,  h_prev],
            [h_prev, -h_prev],
        ],
    )


@log_calls(logger_name=main_log, level='DEBUG')
def check_uncorrelated_degree_k(
        bool_func_1: 'BooleanFunction',
        bool_func_2: 'BooleanFunction',
) -> int | None:
    """Check what degree of uncorrelation between 2 bool_func's.

    Args:
    -----
        bool_func_1: Boolean Function (f)
        bool_func_2: Boolean Function (g)

    Returns:
    --------
        uncorrelated degree of k between f and g
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

    for k_degree in range(number_of_variables + 1):
        for u_derivative in range(1 << number_of_variables):
            if (
                bin(u_derivative)[2:].count('1') <= k_degree
                and cross_correlation_u(bool_func_1, bool_func_2, u_derivative) != 0
            ):
                return max(k_degree - 1, 0)

    return number_of_variables


@log_calls(logger_name=main_log, level='DEBUG')
def cross_correlation_u(
        bool_func_1: 'BooleanFunction',
        bool_func_2: 'BooleanFunction',
        u_derivative: int,
) -> int | None:
    """Calculate cross correlation between 2 bool_func's by derivative u.

    Args:
    -----
        bool_func_1: Boolean Function (f)
        bool_func_2: Boolean Function (g)
        u_derivative: derivative (vector with len n)

    Returns:
    --------
        cross correlation between f and g with derivative u
    """
    main_log.debug(
        'Got 2 bool_funcs: (hex({hexval1}) n_vals({nval1}))&(hex({hexval2}) n_vals2({nvals2})) '
        'derivative u:({u_derivative}: {u_derivative_V_n})',
        hexval1=bool_func_1.truth_table(format='hex'),
        nval1=bool_func_1.nvariables(),
        hexval2=bool_func_2.truth_table(format='hex'),
        nvals2=bool_func_2.nvariables(),
        u_derivative=u_derivative,
        u_derivative_V_n=bin(u_derivative)[2:],
    )
    if check_func_equal_amount_vars(bool_func_1, bool_func_2, main_log) is False:
        return None

    number_of_variables: int = bool_func_1.nvariables()
    tt_f: list[int] = [int(v) for v in bool_func_1.truth_table()]
    tt_g: list[int] = [int(v) for v in bool_func_2.truth_table()]

    total: int = 0
    for x_int in range(1 << number_of_variables):
        # xor x + u
        idx_shifted: int = operator.xor(x_int, u_derivative)

        # xor f(x) + g(x + u)
        val: int = (tt_f[x_int] + tt_g[idx_shifted]) % 2

        if val == 1:
            total -= 1
        else:
            total += 1

    main_log.debug('Returning calculation value {total}', total=total)
    return total


@log_calls(logger_name=main_log, level='DEBUG')
def all_cross_correlations(
        bool_func_1: 'BooleanFunction',
        bool_func_2: 'BooleanFunction',
) -> list[int] | None:
    """Calculate all correlatiions between 2 bool_func's by all derivatives u.

    Args:
    -----
        bool_func_1: Boolean Function (f)
        bool_func_2: Boolean Function (g)

    Returns:
    --------
        list of all cross correlations of f and g by all possible derivatives u
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

    return [
        cross_correlation_u(bool_func_1, bool_func_2, u)
        for u in range(1 << bool_func_1.nvariables())
    ]


@log_calls(logger_name=main_log, level='DEBUG')
def check_perfectly_uncorrelated(
        bool_func_1: 'BooleanFunction',
        bool_func_2: 'BooleanFunction',
) -> bool | None:
    """Find out are 2 bool_func's perfectly uncorrelated or not.

    Args:
    -----
        bool_func_1: Boolean Function (f)
        bool_func_2: Boolean Function (g)

    Returns:
    --------
        True if perfectly correlated, otherwise False
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

    return not any(all_cross_correlations(bool_func_1, bool_func_2))


@log_calls(logger_name=main_log, level='DEBUG')
def get_dot_product_functions(
        bool_func_1: 'BooleanFunction',
        bool_func_2: 'BooleanFunction',
) -> 'IntegerMod_Int':
    """Product 2 bool_func's.

    Args:
    -----
        bool_func_1: Boolean Function (f)
        bool_func_2: Boolean Function (g)

    Returns:
    --------
        transfer 2 bool_func's to vector and product them by components
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

    vector_1: 'Vector_mod_2_dense' = vector(GF(2), bool_func_1.truth_table())
    vector_2: 'Vector_mod_2_dense' = vector(GF(2), bool_func_2.truth_table())
    main_log.debug(
        'Returning: {vector_1_dot_vector_2}',
        vector_1_dot_vector_2=vector_1*vector_2,
    )

    return vector_1 * vector_2


@log_calls(logger_name=main_log, level='DEBUG')
def check_parsevals_identity(w_walsh: tuple[int, ...], number_of_variables: int) -> bool:
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


@log_calls(logger_name=main_log, level='DEBUG')
def get_fourier_coefficients(bool_func: 'BooleanFunction') -> list[int]:
    """Get fourier coefficients.

    Args:
    -----
        bool_func: Boolean Function

    Returns:
    --------
        list of fourier coefficients
    """
    main_log.debug(
        'Got a bool function: hex({hex_value}) num_val({number_of_variables})',
        hex_value=bool_func.truth_table(format='hex'),
        number_of_variables=bool_func.nvariables(),
    )
    number_of_variables: int = bool_func.nvariables()
    w_walsh: tuple[int, ...] = bool_func.walsh_hadamard_transform()

    w_fourier: list[int] = []
    for u_derivative, walsh_val in enumerate(w_walsh):
        # W_walsh(u) = 2^n * delta(u) - 2 * W_fourier(u)
        # Dirac delta function
        delta_u = 1 if u_derivative == 0 else 0
        fourier_val: int = ((1 << number_of_variables) * delta_u - walsh_val) // 2
        w_fourier.append(fourier_val)

    main_log.debug('Returning Fourier coeff: {w_fourier}', w_fourier=w_fourier)

    return w_fourier


@log_calls(logger_name=main_log, level='DEBUG')
def get_function_weight(bool_func: 'BooleanFunction') -> int:
    """Get a weight of the function.

    Args:
    -----
        bool_func: Boolean Function

    Returns:
    --------
        weight of the function
    """
    main_log.debug(
        'Got a bool function: hex({hex_value}) num_val({number_of_variables})',
        hex_value=bool_func.truth_table(format='hex'),
        number_of_variables=bool_func.nvariables(),
    )
    return sum(bool_func.truth_table())


@log_calls(logger_name=main_log, level='DEBUG')
def get_distance_between_functions(
        bool_func_1: 'BooleanFunction',
        bool_func_2: 'BooleanFunction',
) -> int:
    """Calculate distance between 2 bool_func's.

    Args:
    -----
        bool_func_1: Boolean Function (f)
        bool_func_2: Boolean Function (g)

    Returns:
    --------
        distance
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

    table_1: tuple[int, ...] = bool_func_1.truth_table()
    table_2: tuple[int, ...] = bool_func_2.truth_table()
    return sum(1 for i in range(len(table_1)) if table_1[i] != table_2[i])


@log_calls(logger_name=main_log, level='DEBUG')
def check_regularity(
        bool_func: 'BooleanFunction',
) -> tuple[bool, tuple[int, int]] | tuple[bool, None]:
    """Find is function a c-regular.

    Args:
    -----
        bool_func: Boolean function

    Returns:
    --------
        False and None|True and c0 c1 value
    """
    main_log.debug(
        'Got a bool function: hex({hex_value}) num_val({number_of_variables})',
        hex_value=bool_func.truth_table(format='hex'),
        number_of_variables=bool_func.nvariables(),
    )
    number_of_variables: int = bool_func.nvariables()
    truth_table: tuple[int, ...] = tuple(int(x) for x in bool_func.truth_table())

    c0, c1 = None, None

    for i in range(1 << number_of_variables):
        # vertices of hypercube (str if bits)

        current_val: int = truth_table[i]
        count = sum(
            1 for bit in range(number_of_variables)
            if truth_table[operator.xor(i, 1 << bit)] != current_val
        )
        # regularity check
        if current_val == 0:
            if c0 is None:
                c0 = count
            elif c0 != count:
                main_log.debug('c0 is not regular')
                return False, None
        else:
            if c1 is None:
                c1 = count
            elif c1 != count:
                main_log.debug('c1 is not regular')
                return False, None

    return True, (c0, c1)


@log_calls(logger_name=main_log, level='DEBUG')
def find_decompositions(
        bool_func: 'BooleanFunction',
        number_of_variables: int,
        all_decompositions: bool,
) -> None:
    """Find all decompositions of the function (if exists).

    Args:
    -----
        func: function created by truthtable
        number_of_variables: amount of variables into function
        all_decompositions: Find first decompositions or all of them
    """
    # make sure that we got function of n variables
    main_log.debug(
        'Got a bool function: hex({hex_value}) num_val({number_of_variables})',
        hex_value=bool_func.truth_table(format='hex'),
        number_of_variables=bool_func.nvariables(),
    )
    truth_table: tuple[bool, ...] = bool_func.truth_table()
    if len(truth_table) < (1 << number_of_variables):
        main_log.error(
            'Truth table shorter than required: '
            '{len_tt} < 2^{number_of_variables} ({number_of_variables_2_n})',
            len_tt=len(truth_table),
            number_of_variables=number_of_variables,
            number_of_variables_2_n=(1 << number_of_variables),
        )
        return

    h_x = find_decompose(
        number_of_variables,
        truth_table,
        all_decompositions,
    )
    if not h_x:
        main_log.debug('Function is not decomposable')
        return

    degenerative_decomposition: list[tuple[int, int]] = [h[0] for h in h_x if h[-1] == 1]
    classic_decomposition: list[tuple[int, int]] = [h[0] for h in h_x if h[-1] == 2]
    main_log.debug(
        'degenerative decompose h(x): {degenerative_decomposition} '
        'classic decompose h(x): {classic_decomposition}',
        degenerative_decomposition=degenerative_decomposition,
        classic_decomposition=classic_decomposition,
    )


@log_calls(logger_name=main_log, level='DEBUG')
def find_decompose(
        number_of_variables: int,
        truth_table: tuple[bool, ...],
        all_decompositions: bool,
) -> list[list[tuple[int, int]] | int]:
    """Try to find decompose of the function.

    Args:
    -----
        number_of_variables:
        truth_table:
        all_decompositions: True if need to find all of them

    Returns:
    --------
        tuple of h(s) or -1 of not decomposable
    """
    variables: list[int] = list(range(number_of_variables))
    decompositions: list[list[tuple[int, int] | int]] = []
    # 1 < s < n - 1
    for s in range(2, number_of_variables - 1):
        # subset_indices is indexes that goes into s
        for subset_indices in itertools.combinations(variables, s):
            # remaining_indices that goes to g
            # general view f(x_1 ... x_n) = g(h(x_1 ... x_s), x_s+1, ..., x_n)
            remaining_indices: list[int] = [i for i in variables if i not in subset_indices]
            subfunctions = set()

            # go through all possible combinations [x_s+1 ... x_n]
            for y_val in range(1 << (number_of_variables - s)):
                column: list[bool] = []
                # go through all possible combinations [x_1 ... x_s]
                for x_val in range(1 << s):
                    # empty vector of len n
                    full_input: list[int] = [0] * number_of_variables
                    for i, index in enumerate(subset_indices):
                        # x_val values go into column
                        full_input[index] = (x_val >> (s - 1 - i)) & 1

                    for i, index in enumerate(remaining_indices):
                        # y_val (remaining) values go into column
                        full_input[index] = (y_val >> (number_of_variables - s - 1 - i)) & 1

                    # list[bool] -> list[int(0/1)] -> int
                    index_in_truth_table = sum(
                        full_input[j] << (number_of_variables - 1 - j)
                        for j in range(number_of_variables)
                    )
                    # getting value from table, index this int number
                    column.append(truth_table[index_in_truth_table])
                # do this for each y_val, in result get the set of unique vectors
                subfunctions.add(tuple(column))

            # h(x) can have 3 states
            # subfunction = 1, this means h(x) doesnt change the outcome/function is degenerate
            # subfunction = 2, h(x) gives 0/1 and that means that we can decompose the function
            # subfunction > 3, means that we cant decompose that function by h(s*) (s* variables)
            if len(subfunctions) <= 2:
                decompositions.append([subset_indices, len(subfunctions)])

                if not all_decompositions:
                    main_log.debug(
                        'all_decompositions is False, returning {decompositions}',
                        decompositions=decompositions,
                    )
                    return decompositions

    main_log.debug(
        'all_decompositions is True, returning {decompositions}',
        decompositions=decompositions,
    )

    return decompositions


@log_calls(logger_name=main_log, level='DEBUG')
def get_cardinality_functions(
        number_of_variables: int,
) -> None:
    """Get amount of specific functions with n variables.

    Args:
    -----
        number_of_variables: amount of variables in function

    Return:
    -------
        Amount of functions of each type
    """
    all_functions: int = 1 << (1 << number_of_variables)
    balanced_functions: int = math.comb(1 << number_of_variables, 1 << (number_of_variables - 1))
    non_degenerative_functions: int = sum(
        ((-1)**(number_of_variables - k) * math.comb(number_of_variables, k) * 1 << (1 << k))
        for k in range(number_of_variables + 1)
    )
    functionally_separable_functions_upper_bound: int = sum(
        math.comb(number_of_variables, s) * 1 << (1 << s) * 1 << (1 << (number_of_variables - s + 1))
        for s in range(2, number_of_variables - 1)
    )
    affine_functions: int = 1 << (number_of_variables + 1)
    linear_functions: int = 1 << number_of_variables
    symmetrical_functions: int = 1 << (number_of_variables + 1)


def count_amount_test() -> None:
    number_of_variables = 3
    total = 1 << (1 << number_of_variables)
    count = 0
    start_time = tm.time()
    update_step = max(1, total // 1000)

    for i in range(total):
        if is_non_degenerate(i, number_of_variables):
            count += 1

        # note: same as  i % update_step == 0 or i == total - 1:
        if i & (update_step - 1) == 0:
            elapsed = tm.time() - start_time
            percent = float((i + 1) / total * 100)

            if i > 0:
                eta = (elapsed / i) * (total - i)
                eta_str = f'{int(eta // 60)}m {int(eta % 60)}s'
            else:
                eta_str = 'Calculating...'

            sys.stdout.write(
                f"\rProgress: {percent:.2f}% | Elapsed: {elapsed:.2f}s | Lasts: {eta_str} {' ' * 6}",
            )
            sys.stdout.flush()

    print(f'\nTotal: {count}')


@log_calls(logger_name=main_log, level='DEBUG')
def is_non_degenerate(f_int: int, number_of_variables: Integer) -> bool:
    """Check if function not degenerate.

    Args:
    -----
        f_int: function with n variables
        number_of_variables: amount of variables in function

    Returns:
    --------
        bool is degenerate or not
    """
    # Check each variable (i)
    for i in range(number_of_variables):
        is_essential = False
        # distance between 2 vectors that are different only in x_index component
        step = 1 << i

        for j in range(1 << number_of_variables):
            # comparing function value in those 2 vectors
            # if they are not equal then variable is essential
            # note: same as (j // step) % 2 == 0
            # note: same as table[j] != table[j + step]
            if not (j & step) and ((f_int >> j) & 1) != ((f_int >> (j + step)) & 1):
                is_essential = True
                break

        if not is_essential:
            return False

    return True


def random_shit() -> None:
    B: 'BooleanFunction' = random_boolean_function(Integer(5))

    f_absolute_correlation_values: list[tuple[Integer, Integer]] = sorted(
        B.absolute_autocorrelation().items(),
    )
    f_absolute_indicator: Integer = B.absolute_indicator()
    f_absolute_walsh_spectrum: list[tuple[Integer, Integer]] = sorted(
        B.absolute_walsh_spectrum().items(),
    )
    f_algebraic_degree: Integer = B.algebraic_degree()
    f_algebraic_immunity: Integer = B.algebraic_immunity()
    f_algebraic_normal_form: 'BooleanPolynomial' = B.algebraic_normal_form()
    f_annihilator: 'BooleanPolynomial | None' = B.annihilator(2)
    f_autocorrelation: dict[Integer, Integer] = B.autocorrelation()
    f_correlation_immunity: Integer = B.correlation_immunity()
    f_derivative: BooleanFunction = B.derivative(1)
    f_has_linear_structure: bool = B.has_linear_structure()
    f_is_balanced: bool = B.is_balanced()
    f_is_bent: bool = B.is_bent()
    f_is_linear_structure: bool = B.is_linear_structure(1)
    f_is_plateaued: bool = B.is_plateaued()
    f_is_symmetric: bool = B.is_symmetric()
    f_linear_structures: list[Integer] = B.linear_structures()
    f_nonlinearity: Integer = B.nonlinearity()
    f_nvariables: Integer = B.nvariables()
    f_resiliency_order: Integer = B.resiliency_order()
    f_sum_of_square_indicator: Integer = B.sum_of_square_indicator()
    f_truth_table: list[int] = B.truth_table('int')
    f_walsh_hadamard_transform: dict[Integer, Integer] = B.walsh_hadamard_transform()

    print(
        f"""
        {f_absolute_correlation_values}
        {f_absolute_indicator}
        {f_absolute_walsh_spectrum}
        {f_algebraic_degree}
        {f_algebraic_immunity}
        {f_algebraic_normal_form}
        {f_annihilator}
        {f_autocorrelation}
        {f_correlation_immunity}
        {f_derivative}
        {f_has_linear_structure}
        {f_is_balanced}
        {f_is_bent}
        {f_is_linear_structure}
        {f_is_plateaued}
        {f_is_symmetric}
        {f_linear_structures}
        {f_nonlinearity}
        {f_nvariables}
        {f_resiliency_order}
        {f_sum_of_square_indicator}
        {f_truth_table}
        {f_walsh_hadamard_transform}
        """,
    )


def load_init():
    if getattr(load_init, "done", False):
        return
    current_path: Path = Path(__file__).resolve().parent
    init_path = current_path.parent / 'init_files.sage'

    if init_path.exists() is False:
        init_path = Path(__file__).resolve().parent / 'init_files.sage'

    if init_path:
        load(str(init_path))
        load_init.done = True

    else:
        print('Warning: init_files.sage not found')


load_init()
