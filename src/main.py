# -*- coding: utf-8 -*-
"""Main module."""
import itertools
import math
import operator
import sys
import time as tm
from pathlib import Path
from typing import TYPE_CHECKING

from sage.all import gcd
from sage.arith.functions import lcm
from sage.combinat.matrices.hadamard_matrix import hadamard_matrix
from sage.crypto.boolean_function import (
    BooleanFunction,
    random_boolean_function,
)
from sage.matrix.constructor import matrix
from sage.misc.persist import load
from sage.modules.free_module import VectorSpace
from sage.modules.free_module_element import vector
from sage.rings.finite_rings.finite_field_constructor import GF
from sage.rings.integer import Integer
from sage.rings.polynomial.pbori.pbori import BooleanMonomial, BooleanPolynomialRing
from sage.rings.rational_field import QQ

if TYPE_CHECKING:
    from sage.matrix.matrix_integer_dense import Matrix_integer_dense
    from sage.modules.vector_mod2_dense import Vector_mod_2_dense
    from sage.rings.finite_rings.integer_mod import IntegerMod_Int
    from sage.rings.polynomial.pbori import BooleanPolynomial


def load_init() -> None:
    current_path: Path = Path(__file__).resolve().parent
    init_path = current_path.parent / 'init_files.py'

    if not init_path.exists():
        init_path = Path(__file__).resolve().parent / 'init_files.py'

    if init_path:
        load(str(init_path))

    else:
        print('Warning: init_files.py not found')


load_init()

from some_checks import check_func_equal_amount_vars

from decorators import log_calls

from logger_config import main_log


def is_without_forbidden(bool_func: 'BooleanFunction') -> bool:
    """Check if function is forbidden.

    Args:
    -----
        bool_func: Boolean Function

    Returns:
    --------
        True/False
    """
    number_of_variables = bool_func.nvariables()
    u_last = vector(GF(2), [0] * (number_of_variables - 1) + [1])
    u_first = vector(GF(2), [1] + [0] * (number_of_variables - 1))

    return any(
        [
            get_function_weight(bool_func.derivative(u_first)) == (1 << number_of_variables),
            get_function_weight(bool_func.derivative(u_last)) == (1 << number_of_variables),
        ]
    )


def find_best_rho_and_theta(bool_func: 'BooleanFunction') -> None | dict:
    """Find rho and theha that.

    Args:
    -----
        bool_func: Boolean Function

    Returns:
    --------
        None or rho and theha that covers sequence
    """
    num_vars = int(bool_func.nvariables())
    num_states = 1 << num_vars
    # all f(u)
    derivatives_tt = []
    for i in range(num_states):
        bits = Integer(i).bits()
        u_list = bits[:num_vars] + [0] * (num_vars - len(bits))
        derivatives_tt.append(list(bool_func.derivative(u_list).truth_table()))
    # Make matrix M, where x dots is the rows, derivatives u is the columns
    rows = [
        [int(derivatives_tt[u_idx][x_idx]) for u_idx in range(num_states)]
        for x_idx in range(num_states)
    ]
    qq_matrix = matrix(QQ, rows)
    vector_of_ones = vector(QQ, [1] * num_states)
    if qq_matrix.rank() != qq_matrix.augment(vector_of_ones).rank():
        return None

    # Find a solution for rho = 1
    theta_sol = qq_matrix.solve_right(vector_of_ones)
    # Make theta and rho integers
    common_den = lcm([x.denominator() for x in theta_sol])

    return {
        'rho': int(common_den),
        'theta': {i: int(val) for i, val in enumerate(theta_sol * common_den) if val != 0},
    }


def is_hyper_bent(bool_func: 'BooleanFunction') -> bool:
    """Check if function is hyperbent. function must have even amount of variables.

    Args:
    -----
        bool_func: Boolean Function

    Returns:
    --------
        True/False
    """
    number_of_variables = bool_func.nvariables()
    if number_of_variables % 2 != 0:
        return False

    if not bool_func.is_bent():
        return False

    # Field and its elements
    gf_z = GF(1 << number_of_variables, 'z')
    # List all x from the field (corresponding to vectors from V_n)
    elements = list(gf_z)
    # Set of exponents s coprime to 2^n - 1
    # (In the simplest case, it is enough to check the s for which this is a permutation)
    target_walsh = 1 << (number_of_variables // 2)
    # Find П_n: s that gcd(s, 2^n - 1) == 1
    modulus = (1 << number_of_variables) - 1
    permutations_of_n_elements = [s for s in range(1, modulus) if gcd(s, modulus) == 1]

    tt = bool_func.truth_table()
    # Check for each s from П_п and each a from F_(2^n)
    for s_block_permutation in permutations_of_n_elements:
        for vector_of_gf_z in gf_z:
            # Calculate sum of W_f(a, s)
            current_sum = sum(
                # f(x) + Trace(a * x^s)
                (-1)**operator.xor(int(tt[i]), int((vector_of_gf_z * (x**s_block_permutation)).trace()))
                for i, x in enumerate(elements)
            )

            if abs(current_sum) != target_walsh:
                return False

    return True


@log_calls(logger_name=main_log, level='DEBUG')
def satisfies_pc_l(bool_func: 'BooleanFunction', l_criteria: int | None = None) -> bool | int:
    """Check if function satisfy PC(l).

    Args:
    -----
        bool_func: Boolean Function
        l_criteria: criteria l

    Returns:
    --------
        True/False for specified l or max l for the function
    """
    number_of_variables: int = bool_func.nvariables()
    if l_criteria is not None and (l_criteria < 1 or l_criteria > bool_func.nvariables()):
        main_log.warning(
            '1 <= l < number_of_variables not satisfied: l={l}; n:{num_vars}',
            l=l_criteria,
            num_vars=number_of_variables,
        )
        return False

    main_log.debug(
        'Got a bool function: hex({hex_value}); num_val({number_of_variables}); l({l})',
        hex_value=bool_func.truth_table(format='hex'),
        number_of_variables=number_of_variables,
        l=l_criteria,
    )
    # check is function satisfy PC(l)
    if l_criteria is not None:
        # all vectors of len n
        for derivative_u in VectorSpace(GF(2), number_of_variables):
            # all u that 1 <= wt(u) <= l
            if (
                1 <= derivative_u.hamming_weight() <= l_criteria
                and not bool_func.derivative(derivative_u).is_balanced()
            ):
                return False

        main_log.debug(
            'function satisfy PC({l}), returning True',
            l=l_criteria,
        )
        return True

    # find max l for function that PC(l) is satisfied
    for l_criteria in range(1, number_of_variables + 1):
        # all vectors of len n
        for derivative_u in VectorSpace(GF(2), number_of_variables):
            # all u that 1 <= wt(u) <= l
            if (
                derivative_u.hamming_weight() == l_criteria
                and not bool_func.derivative(derivative_u).is_balanced()
            ):
                main_log.debug('returning l={res}', res=l_criteria - 1)
                return l_criteria - 1

    main_log.debug(
        'function passes all iterations, returning l=({l})',
        l=number_of_variables,
    )
    return number_of_variables


def satisfies_pc_l_order_k(
        bool_func: 'BooleanFunction',
        l_criteria: int,
        k_order: int,
) -> bool:
    """Check that function satisfy PC(l) with k criterial.

    Args:
    -----
        bool_func: Boolean Function
        l_criteria: criteria l
        k_order: order k

    Returns:
    --------
        True/False
    """
    number_of_variables: int = bool_func.nvariables()
    main_log.debug(
        'Got hex({hex_value}); num_val({number_of_variables}); l({l}); k({k});',
        hex_value=bool_func.truth_table(format='hex'),
        number_of_variables=number_of_variables,
        l=l_criteria,
        k=k_order,
    )
    if not (
        1 <= k_order < number_of_variables and 1 <= l_criteria <= number_of_variables - k_order
    ):
        main_log.debug('1 <= k < n or 1 <= l <= n - k not satisfied')
        return False

    poly: 'BooleanPolynomial' = bool_func.algebraic_normal_form()
    variables_of_bool_func: tuple['BooleanPolynomial'] = poly.parent().gens()

    # Going through all combinations of k variables that we are going to fix
    for indices in itertools.combinations(range(number_of_variables), k_order):
        # That k variables that we have chosen need to equate to 0 or 1
        # There is 1 << k options to do that
        for values in itertools.product([0, 1], repeat=k_order):
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
            used_vars: tuple['BooleanPolynomial', ...] = sub_anf.variables()

            # subfunction is constant
            if len(used_vars) <= 1:
                main_log.debug('Subfunction is constant, returning False')
                return False

            new_r: 'BooleanPolynomialRing' = BooleanPolynomialRing(
                len(used_vars),
                names=[str(v) for v in used_vars],
            )
            sub_bf: 'BooleanFunction' = BooleanFunction(new_r(str(sub_anf)))
            # Check PC(l) for subfunction
            if not satisfies_pc_l(sub_bf, l_criteria=l_criteria):
                return False

    main_log.debug('Function satisfies PC({l}) of order k={k}', l=l_criteria, k=k_order)
    return True


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
    tt = bool_func.truth_table()
    for k_degree in range(1, number_of_variables):
        # Going through all combinations of k variables that we are going to fix
        for indices in itertools.combinations(range(number_of_variables), k_degree):
            # That k variables that we have chosen need to equate to 0 or 1
            # There is 1 << k options to do that
            for values in itertools.product([0, 1], repeat=k_degree):
                # Put variables that we have chosen into new polynomial
                mask = 0
                target_bits = 0
                for idx, val in zip(indices, values):
                    mask |= (1 << idx)
                    if val:
                        target_bits |= (1 << idx)

                sub_tt = tuple(
                    tt[i] for i in range(1 << number_of_variables)
                    if (i & mask) == target_bits
                )

                if not any(sub_tt) or all(sub_tt):
                    # if subfunction uses no variables (equals to constant)
                    # it means subfunction cant be balanced
                    main_log.debug(
                        'Subfunction is constant, returning k=({k})',
                        k=k_degree - 1,
                    )
                    return k_degree - 1

                sub_bf: 'BooleanFunction' = BooleanFunction(sub_tt)

                act: tuple[int, ...] = sub_bf.autocorrelation()
                # calculate autocorrelation and look at derivatives that wt(u) = 1
                # so for n = 3 it is going to be [1 0 0] [0 1 0] [0 0 1]
                if not all(act[1 << i] == 0 for i in range(sub_bf.nvariables())):
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
def get_ci_function(bool_func: 'BooleanFunction') -> list[int]:
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
    ci_f: list[int] = [
        _ for _, val in enumerate(bool_func.walsh_hadamard_transform())
        if val == 0
    ]
    main_log.debug('Calculated the ci_f: {ci_f}', ci_f=ci_f)

    return ci_f


@log_calls(logger_name=main_log, level='DEBUG')
def get_intersecting_spectral(
        bool_func_1: 'BooleanFunction',
        bool_func_2: 'BooleanFunction',
) -> set | None:
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
    if not check_func_equal_amount_vars(bool_func_1, bool_func_2, main_log):
        return None

    ci_f = set(get_ci_function(bool_func_1))
    ci_g = set(get_ci_function(bool_func_2))

    intersection = ci_f.intersection(ci_g)
    main_log.debug('Calculated intersection: {intersection}', intersection=intersection)

    return intersection if intersection else None


@log_calls(logger_name=main_log, level='DEBUG')
def fwht(vector: list[int]) -> list[int]:
    """Fast Walsh-hadamard transofrmation.
    Muptiply vector of len 2^n on hadamard matrix of order 2^n

    Advantage of that method compared to simple creation of H of order n
    is that we dont need to create the whole matrix.
    By that we use O(N*logN) of memory instead of O(N*N).

    Args:
    -----
        vector:

    Returns:
    --------
        vector * hadamard matrix
    """
    # Method that used to calculate the vector called
    # Butterfly algorithm / FFT
    number_of_components: int = len(vector)
    fwht_vector = vector.copy()
    step = 1
    while step < number_of_components:
        for i in range(0, number_of_components, step << 1):
            for j in range(i, i + step):
                x = fwht_vector[j]
                y = fwht_vector[j + step]
                fwht_vector[j] = x + y
                fwht_vector[j + step] = x - y

        step <<= 1

    return vector


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
    if matrix_order >= 12:
        return hadamard_matrix(1 << matrix_order)

    if matrix_order == 0:
        return matrix([[1]])

    h_prev = fast_sylvester_hadamard(matrix_order - 1)

    return block_matrix(
        [
            [h_prev,  h_prev],  # flake8:noqa
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
    if not check_func_equal_amount_vars(bool_func_1, bool_func_2, main_log):
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
    if not check_func_equal_amount_vars(bool_func_1, bool_func_2, main_log):
        return None

    number_of_variables: int = bool_func_1.nvariables()

    # pm1: plus minus 1
    f_pm1 = [1 if v == 0 else -1 for v in bool_func_1.truth_table()]
    g_pm1 = [1 if v == 0 else -1 for v in bool_func_2.truth_table()]

    total: int = sum(
        f_pm1[x_int] * g_pm1[operator.xor(x_int, u_derivative)]
        for x_int in range(1 << number_of_variables)
    )

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
    if not check_func_equal_amount_vars(bool_func_1, bool_func_2, main_log):
        return None

    w_f = bool_func_1.walsh_hadamard_transform()
    w_g = bool_func_2.walsh_hadamard_transform()
    w_product = [w_f[i] * w_g[i] for i in range(1 << bool_func_1.nvariables())]
    return [corr // (1 << bool_func_1.nvariables()) for corr in fwht(w_product)]


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
    if not check_func_equal_amount_vars(bool_func_1, bool_func_2, main_log):
        return None

    return not any(all_cross_correlations(bool_func_1, bool_func_2)[1:])


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
    if not check_func_equal_amount_vars(bool_func_1, bool_func_2, main_log):
        return None

    vector_1: 'Vector_mod_2_dense' = vector(GF(2), bool_func_1.truth_table())
    vector_2: 'Vector_mod_2_dense' = vector(GF(2), bool_func_2.truth_table())
    main_log.debug(
        'Returning: {vector_1_dot_vector_2}',
        vector_1_dot_vector_2=vector_1 * vector_2,
    )

    return vector_1 * vector_2


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
) -> int | None:
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
    if not check_func_equal_amount_vars(bool_func_1, bool_func_2, main_log):
        return None

    table_1: tuple[int, ...] = bool_func_1.truth_table()
    table_2: tuple[int, ...] = bool_func_2.truth_table()

    return sum(operator.xor(a, b) for a, b in zip(table_1, table_2))


@log_calls(logger_name=main_log, level='DEBUG')
def check_regularity(
        bool_func: 'BooleanFunction',
) -> tuple[bool, tuple[int | None, int | None]] | tuple[bool, None]:
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
        all_decompositions: bool = False,
) -> None | tuple[list[tuple[int, int]], ...]:
    """Find all decompositions of the function (if exists).

    Args:
    -----
        bool_func: function created by truthtable
        number_of_variables: amount of variables into function
        all_decompositions: Find first decompositions or all of them

    Returns:
    --------
        None | degerenative/classic decompositions
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
            number_of_variables_2_n=1 << number_of_variables,
        )
        return None

    h_x = find_decompose(
        number_of_variables,
        truth_table,
        all_decompositions,
    )
    if not h_x:
        main_log.debug('Function is not decomposable')
        return None

    # fictitious variable
    degenerative_decomposition: list[tuple[int, int]] = [h[0] for h in h_x if h[-1] == 1]
    # non-degenerate function
    classic_decomposition: list[tuple[int, int]] = [h[0] for h in h_x if h[-1] == 2]
    main_log.debug(
        'degenerative decompose h(x): {degenerative_decomposition} '
        'classic decompose h(x): {classic_decomposition}',
        degenerative_decomposition=degenerative_decomposition,
        classic_decomposition=classic_decomposition,
    )
    return degenerative_decomposition, classic_decomposition


@log_calls(logger_name=main_log, level='DEBUG')
def find_decompose(
        number_of_variables: int,
        truth_table: tuple[bool, ...],
        all_decompositions: bool,
) -> list[list[tuple[int, ...] | int]]:
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
    decompositions: list[list[tuple[int, ...] | int]] = []
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
def is_non_degenerate(bool_func: 'BooleanFunction', number_of_variables: int) -> bool:
    """Check if function not degenerate.

    Args:
    -----
        bool_func: boolean function
        number_of_variables: amount of variables in function

    Returns:
    --------
        True/False
    """
    return len(bool_func.algebraic_normal_form().variables()) == number_of_variables
