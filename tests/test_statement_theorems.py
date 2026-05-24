# -*- coding: utf-8 -*-
"""Test funcs from statement_theoremns_dot_py."""

from pathlib import Path

import pytest

from sage.misc.persist import load
from sage.crypto.boolean_function import (
    BooleanFunction,
    random_boolean_function,
)

from src.theorems.statement_theorems import theorem_convolution


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

@pytest.mark.parametrize('run_id', range(128))
def test_theorem_convolution(run_id: int) -> None:
    """Test func."""
    bool_func_1 = random_boolean_function(8)
    bool_func_2 = random_boolean_function(8)

    assert theorem_convolution(bool_func_1, bool_func_2) is True
