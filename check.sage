# -*- coding: utf-8 -*-
# mypy: disable-error-code="import-not-found"
"""check module."""

from pathlib import Path

import operator
import itertools

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sage.rings.polynomial.pbori import BooleanPolynomial
    from sage.rings.polynomial.pbori.pbori import BooleanMonomial, BooleanPolynomialRing

from sage.crypto.boolean_function import BooleanFunction

from src.logger_config import main_log


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

if __name__ == "__main__":
    a = BooleanFunction('6395')
    b = BooleanFunction('1616')

    f = BooleanFunction('963c5af066ccaaff')
    res = is_hyper_bent(f)
    print(res)
# x = BooleanPolynomialRing(3, 'x').gens()
# f = BooleanFunction('963c5af066ccaaff')
# f = BooleanFunction(x[0]*x[1] + x[0]*x[2] + x[1]*x[2] + 1)
# print('f ANF:', f.algebraic_normal_form())

# for i in range(256):
#     hex_str = f"{i:02x}"
#     f = BooleanFunction(hex_str)
#     res = sac(f)
#     if res == 1:
#         print(i, f.algebraic_normal_form())


#[23] [k=1] x0*x1 + x0*x2 + x1*x2 + 1
#[24] [k=1] x0*x1 + x0*x2 + x1*x2 + x2
#[36] [k=1] x0*x1 + x0*x2 + x1*x2 + x1
#[43] [k=1] x0*x1 + x0*x2 + x1*x2 + x1 + x2 + 1
#[66] [k=1] x0*x1 + x0*x2 + x0 + x1*x2
#[77] [k=1] x0*x1 + x0*x2 + x0 + x1*x2 + x2 + 1
#[113] [k=1] x0*x1 + x0*x2 + x0 + x1*x2 + x1 + 1
#[126] [k=1] x0*x1 + x0*x2 + x0 + x1*x2 + x1 + x2
#[129] [k=1] x0*x1 + x0*x2 + x0 + x1*x2 + x1 + x2 + 1
#[142] [k=1] x0*x1 + x0*x2 + x0 + x1*x2 + x1
#[178] [k=1] x0*x1 + x0*x2 + x0 + x1*x2 + x2
#[189] [k=1] x0*x1 + x0*x2 + x0 + x1*x2 + 1
#[212] [k=1] x0*x1 + x0*x2 + x1*x2 + x1 + x2
#[219] [k=1] x0*x1 + x0*x2 + x1*x2 + x1 + 1
#[231] [k=1] x0*x1 + x0*x2 + x1*x2 + x2 + 1
#[232] [k=1] x0*x1 + x0*x2 + x1*x2


# bent n = 6
#963c5af066ccaaff
#963c5af066ccaa00



#['0356', '0359', '0365', '036a', '0395',
# '039a', '03a6', '03a9', '0536', '0539', '0563',
# '056c', '0593', '059c', '05c6', '05c9', '0635',
# '063a', '0653', '065c']


#linear_functions = []
#for i in range(65536):
#    hex_str = format(i, '04x')
#    f = BooleanFunction(hex_str)
#    wf = f.walsh_hadamard_transform()
#    if abs(max(wf)) == 16:
#        linear_functions.append(hex_str)
# ['0000', '0ff0', '33cc', '3c3c',
# '55aa', '5a5a', '6666', '6996',
# '9696', '9966', 'a55a', 'aaaa',
# 'c33c', 'cccc', 'f0f0', 'ff00']
# print(f"{linear_functions}")
