# -*- coding: utf-8 -*-
"""Test funcs from statement_theoremns_dot_sage."""

from pathlib import Path

import pytest
from sage.all import *
from sage.crypto.boolean_function import BooleanFunction


def load_init() -> None:
    current_path: Path = Path(__file__).resolve().parent
    init_path = current_path.parent / 'init_files.py'

    if init_path.exists() is False:
        init_path = Path(__file__).resolve().parent / 'init_files.py'

    if init_path:
        load(str(init_path))

    else:
        print('Warning: init_files.py not found')


load_init()


@count_time()
def check_list() -> list:
    al_list: list = []
    n: int = 1
    for i in range(1 << (1 << n)):
        hex_str: str = format(i, f'0{(1 << n) // 4}x')
        f = BooleanFunction(hex_str)
        for k in range(1 << (1 << n)):
            hex_str_2: str = format(k, f'0{(1 << n) // 4}x')
            f2 = BooleanFunction(hex_str_2)
            res = get_distance_between_functions(f, f2)
            print(res)
            # print(hex_str, hex_str_2)
            #if res is not None:
            #    al_list.append([hex_str, hex_str_2])

    return al_list

#res = check_list()
#print(res) 