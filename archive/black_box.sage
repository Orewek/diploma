# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-order
"""check module."""

from pathlib import Path
import itertools
import operator
import zlib
from typing import TYPE_CHECKING

from sage.crypto.boolean_function import BooleanFunction

if TYPE_CHECKING:
    from sage.rings.rational import Rational

def load_init():
    current_path: Path = Path(__file__).resolve().parent
    init_path = current_path.parent / 'init_files.sage'

    if init_path.exists() is False:
        init_path = Path(__file__).resolve().parent / 'init_files.sage'

    if init_path:
        load(str(init_path))

    else:
        print('Warning: init_files.sage not found')


load_init()


def check_degree_r(
        ttf: list[bool | None],
        number_of_variables: int,
        degree_r: int,
) -> tuple[bool, list[float]]:
    """Check if function f that we might doesnt know for sure has deg = r.

    Args:
    -----
        ttf: truth table of function f
        number_of_variables:
        degree_r: number that might be equal to deg(f)

    Returns:
    --------
        tuple with False/True statment for each r and probability of it
        If prob != 1 that means that we cant say for sure is conclusion correct
        even 1 missing value can change the parity, so changes are 50/50
        No matter how many values from ttf are missing its always going to be 1/2
        So prob just shows percent of values that not missing as p/(p + q), where
        p - non-missing values, q - missing values, p + q - all values
    """
    def get_monomial_tt(
            indices: tuple[int, ...],
            number_of_variables: int,
    ) -> 'BooleanFunction':
        """Get monoms with indices from the tuple x_i*x_j*etc.

        Args:
        -----
            indices: monom's indices
            number_of_variables:

        Returns:
        --------
            Monom
        """
        # truth table for monom
        tt: list[int] = []
        for i in range(1 << number_of_variables):
            # all variables from monom must be equal to 1
            # we going through truth_table of f and look where those indices = 1
            # for example monom x0 * x1, we choose all f(x) where x0 = x1 = 1
            tt.append(all((i >> j) & 1 for j in indices))

        return BooleanFunction(tt)

    def calculate_f_xor_g_parity(
            ttf: list[bool | None],
            g: 'BooleanFunction',
    ) -> tuple[int, 'Rational']:
        """Caclulate sum(f(i)_xor_g(i) for i in range 2**n)).

        Args:
        -----
            ttf: truth table of function f
            g: monom

        Returns:
        --------
            parity of f_xor_g and p/(p+q) of non-missing/missing values
        """
        f_xor_g: int = sum(
            operator.__and__(x, y)
            for x, y in zip(ttf, g.truth_table())
            if x is not None
        )
        info_bits = sum(
            1 for x, y in zip(ttf, g.truth_table())
            if x is not None and y is True
        )
        no_info_bits = sum(
            1 for x, y in zip(ttf, g.truth_table())
            if x is None and y is True
        )
        prob: 'Rational' = (
            info_bits / (info_bits + no_info_bits)
            if (info_bits + no_info_bits) > 0
            else 0
        )
        return f_xor_g % 2, prob

    probability_data: list['Rational'] = []
    temp_prob: list['Rational'] = []
    # 1. f * g = 0 for all g: deg(g) = n - r - 1
    if number_of_variables - degree_r - 1 >= 0:
        all_zero: bool = True
        # all combinations of indices for monoms of deg n - r - 1
        for combo in itertools.combinations(
            range(number_of_variables),
            number_of_variables - degree_r - 1,
        ):
            g: 'BooleanFunction' = get_monomial_tt(combo, number_of_variables)
            parity, prob = calculate_f_xor_g_parity(ttf, g)
            temp_prob.append(prob)
            if parity == 1:
                all_zero = False
                break

        avg_p: 'Rational' = sum(temp_prob) / len(temp_prob) if temp_prob else 1.0
        probability_data.append(avg_p)
        if not all_zero:
            return False, probability_data

    # 2. f * g != for some g: deg(g) = n - r
    if number_of_variables - degree_r >= 0:
        found_nonzero: bool = False
        temp_prob = []
        for combo in itertools.combinations(
            range(number_of_variables),
            number_of_variables - degree_r,
        ):
            g = get_monomial_tt(combo, number_of_variables)
            parity, prob = calculate_f_xor_g_parity(ttf, g)
            temp_prob.append(prob)
            if parity == 1:
                found_nonzero = True

        avg_p = sum(temp_prob) / len(temp_prob) if temp_prob else 1.0
        probability_data.append(avg_p)
        if not found_nonzero:
            return False, probability_data

    return True, probability_data


def black_box(x: int) -> bool | None:
    """Get the a value of f(x).
    Dont know what the function is.
    We get only a partion of information.

    Args:
    -----
        x: number of the bit of f from truth table

    Returns:
        value of f(x)
    """
    hex_str: str = '963c5af066ccaaff'
    val: int = int(hex_str, 16)
    # setting what what percent of the truth table we know
    # on the right side of the equation percent of truth_table we know
    if (zlib.crc32(bytes([x])) % 100) > 100:
        return None

    return bool((val >> x) & 1)


if __name__ == "__main__":
    number_of_variables = 6

    low_bound = 0
    high_bound = number_of_variables
    seen_true = False
    ttf: list[bool | None] = [black_box(i) for i in range(1 << number_of_variables)]
    for degree_r in range(0, number_of_variables + 1):
        label, points = check_degree_r(ttf, number_of_variables, degree_r)
        if label is True and all(p == 1 for p in points):
            low_bound = degree_r
            high_bound = min(degree_r, high_bound)
            seen_true = True

        if all(p == 1 for p in points) and seen_true is False:
            low_bound = degree_r
            high_bound = number_of_variables

    if low_bound == high_bound:
        print(f'def(f) = {low_bound}')
    else:
        print(f'{low_bound} <= deg(f) <= {high_bound}')
