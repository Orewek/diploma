# -*- coding: utf-8 -*-
"""Test funcs from verify_theoremns_dot_py."""

from pathlib import Path

import pytest

from sage.misc.persist import load
from sage.crypto.boolean_function import random_boolean_function

from src.theorems.verify_theorems import (
    verify_inequality,
    max_sum_corr_theorem,
    theorem_about_cross_correlation,
    verify_parsevals_identity,
)


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

AMOUNT_OF_VARS: int = 10
AMOUNT_OF_TESTS: int = 128


@pytest.mark.parametrize('_', range(AMOUNT_OF_TESTS))
def test_verify_inequality(_: int) -> None:
    """Test func."""
    bool_func_1 = random_boolean_function(AMOUNT_OF_VARS)

    assert verify_inequality(bool_func_1) is True


@pytest.mark.parametrize('_', range(AMOUNT_OF_TESTS))
def test_max_sum_corr_theorem(_: int) -> None:
    """Test func."""
    bool_func_1 = random_boolean_function(AMOUNT_OF_VARS)
    bool_func_2 = random_boolean_function(AMOUNT_OF_VARS)

    assert max_sum_corr_theorem(bool_func_1, bool_func_2) is True


@pytest.mark.parametrize('_', range(AMOUNT_OF_TESTS))
def test_theorem_about_cross_correlation(_: int) -> None:
    """Test func."""
    bool_func_1 = random_boolean_function(AMOUNT_OF_VARS)
    bool_func_2 = random_boolean_function(AMOUNT_OF_VARS)

    assert theorem_about_cross_correlation(bool_func_1, bool_func_2) is True


@pytest.mark.parametrize('_', range(AMOUNT_OF_TESTS))
def test_verify_parsevals_identity(_: int) -> None:
    """Test func."""
    bool_func_1 = random_boolean_function(AMOUNT_OF_VARS)

    assert verify_parsevals_identity(bool_func_1.walsh_hadamard_transform(), 10) is True
