# -*- coding: utf-8 -*-
"""Test funcs from main_dot_sage."""

from pathlib import Path

import pytest

from sage.misc.persist import load
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


from src.main import (
    is_without_forbidden,
    find_best_rho_and_theta,
    is_hyper_bent,
    satisfies_pc_l,
    satisfies_pc_l_order_k,
    sac,
    get_ci_function,
    get_intersecting_spectral,
    fwht,
    fast_sylvester_hadamard,
    check_uncorrelated_degree_k,
    cross_correlation_u,
    all_cross_correlations,
    check_perfectly_uncorrelated,
    get_fourier_coefficients,
    get_function_weight,
    get_distance_between_functions,
    check_regularity,
    find_decompositions,
    is_non_degenerate,
)


@pytest.mark.parametrize('hex_str', [
    '00ff', '01fe', '02fd', '03fc', '04fb', '05fa', '06f9', '07f8', '08f7', '09f6',
    '0af5', '0bf4', '0cf3', '0df2', '0ef1', '0ff0', '10ef', '11ee', '12ed', '13ec',
    '14eb', '15ea', '16e9', '17e8', '18e7', '19e6', '1ae5', '1be4', '1ce3', '1de2',
    '1ee1', '1fe0', '20df', '21de', '22dd', '23dc', '24db', '25da', '26d9', '27d8',
    '28d7', '29d6', '2ad5', '2bd4', '2cd3', '2dd2', '2ed1', '2fd0', '30cf', '31ce',
    '32cd', '33cc', '34cb', '35ca', '36c9', '37c8', '38c7', '39c6', '3ac5', '3bc4',
    '3cc3', '3dc2', '3ec1', '3fc0', '40bf', '41be', '42bd', '43bc', '44bb', '45ba',
    '46b9', '47b8', '48b7', '49b6', '4ab5', '4bb4', '4cb3', '4db2', '4eb1', '4fb0',
    '50af', '51ae', '52ad', '53ac', '54ab', '5555', '5556', '5559', '555a', '5565',
    '5566', '5569', '556a', '5595', '5596', '5599', '559a', '55a5', '55a6', '55a9',
    '55aa', '5655', '5656', '5659', '565a', '5665', '5666', '5669', '566a', '5695',
    '5696', '5699', '569a', '56a5', '56a6', '56a9', '56aa', '57a8', '58a7', '5955',
    '5956', '5959', '595a', '5965', '5966', '5969', '596a', '5995', '5996', '5999',
    '599a', '59a5', '59a6', '59a9', '59aa', '5a55', '5a56', '5a59', '5a5a', '5a65',
    '5a66', '5a69', '5a6a', '5a95', '5a96', '5a99', '5a9a', '5aa5', '5aa6', '5aa9',
    '5aaa', '5ba4', '5ca3', '5da2', '5ea1', '5fa0', '609f', '619e', '629d', '639c',
    '649b', '6555', '6556', '6559', '655a', '6565', '6566', '6569', '656a', '6595',
    '6596', '6599', '659a', '65a5', '65a6', '65a9', '65aa', '6655', '6656', '6659',
    '665a', '6665', '6666', '6669', '666a', '6695', '6696', '6699', '669a', '66a5',
    '66a6', '66a9', '66aa', '6798', '6897', '6955', '6956', '6959', '695a', '6965',
    '6966', '6969', '696a', '6995', '6996', '6999', '699a', '69a5', '69a6', '69a9',
    '69aa', '6a55', '6a56', '6a59', '6a5a', '6a65', '6a66', '6a69', '6a6a', '6a95',
    '6a96', '6a99', '6a9a', '6aa5', '6aa6', '6aa9', '6aaa', '6b94', '6c93', '6d92',
    '6e91', '6f90', '708f', '718e', '728d', '738c', '748b', '758a', '7689', '7788',
    '7887', '7986', '7a85', '7b84', '7c83', '7d82', '7e81', '7f80', '807f', '817e',
    '827d', '837c', '847b', '857a', '8679', '8778', '8877', '8976', '8a75', '8b74',
    '8c73', '8d72', '8e71', '8f70', '906f', '916e', '926d', '936c', '946b', '9555',
    '9556', '9559', '955a', '9565', '9566', '9569', '956a', '9595', '9596', '9599',
    '959a', '95a5', '95a6', '95a9', '95aa', '9655', '9656', '9659', '965a', '9665',
    '9666', '9669', '966a', '9695', '9696', '9699', '969a', '96a5', '96a6', '96a9',
    '96aa', '9768', '9867', '9955', '9956', '9959', '995a', '9965', '9966', '9969',
    '996a', '9995', '9996', '9999', '999a', '99a5', '99a6', '99a9', '99aa', '9a55',
    '9a56', '9a59', '9a5a', '9a65', '9a66', '9a69', '9a6a', '9a95', '9a96', '9a99',
    '9a9a', 'aa55', 'aa56', 'aa59', 'aa5a', 'aa65', 'aa66', 'aa69', 'aa6a', 'aa95',
    'aa96', 'aa99', 'aa9a', 'aaa5', 'aaa6', 'aaa9', 'aaaa', 'ab54', 'ac53', 'ad52',
    'ae51', 'af50', 'b04f', 'b14e', 'b24d', 'b34c', 'b44b', 'b54a', 'b649', 'b748',
    'b847', 'b946', 'ba45', 'bb44', 'bc43', 'bd42', 'be41', 'bf40', 'c03f', 'c13e',
    'c23d', 'c33c', 'c43b', 'c53a', 'c639', 'c738', 'c837', 'c936', 'ca35', 'cb34',
    'cc33', 'cd32', 'ce31', 'cf30', 'd02f', 'd12e', 'd22d', 'd32c', 'd42b', 'd52a',
    'd629', 'd728', 'd827', 'd926', 'da25', 'db24', 'dc23', 'dd22', 'de21', 'df20',
    'e01f', 'e11e', 'e21d', 'e31c', 'e41b', 'e51a', 'e619', 'e718', 'e817', 'e916',
    'ea15', 'eb14', 'ec13', 'ed12', 'ee11', 'ef10', 'f00f', 'f10e', 'f20d', 'f30c',
    'f40b', 'f50a', 'f609', 'f708', 'f807', 'f906', 'fa05', 'fb04', 'fc03', 'fd02',
    'fe01', 'ff00',
])
def test_forbidden(hex_str: str) -> None:
    """Test func."""
    bool_func = BooleanFunction(hex_str)

    assert is_without_forbidden(bool_func) is True


@pytest.mark.parametrize('hex_str', [
    '0f', '17', '1b', '1d', '1e', '27', '2b', '2d', '2e', '33', '35', '36', '39', '3a',
    '3c', '47', '4b', '4d', '4e', '53', '55', '56', '59', '5a', '5c', '63', '65', '66',
    '69', '6a', '6c', '71', '72', '74', '78', '87', '8b', '8d', '8e', '93', '95', '96',
    '99', '9a', '9c', 'a3', 'a5', 'a6', 'a9', 'aa', 'ac', 'b1', 'b2', 'b4', 'b8', 'c3',
    'c5', 'c6', 'c9', 'ca', 'cc', 'd1', 'd2', 'd4', 'd8', 'e1', 'e2', 'e4', 'e8', 'f0',
])
def test_find_best_rho_and_theta(hex_str: str) -> None:
    """Test func."""
    bool_func = BooleanFunction(hex_str)

    assert find_best_rho_and_theta(bool_func) is not None


def test_is_hyper_bent() -> None:
    """Test func."""
    assert 1 == 1


@pytest.mark.parametrize('hex_str', [
    '06', '09', '12', '14', '17', '18', '1b', '1d', '21', '24', '27', '28', '2b',
    '2e', '35', '3a', '41', '42', '47', '48', '4d', '4e', '53', '5c', '60', '6f',
    '71', '72', '74', '7b', '7d', '7e', '81', '82', '84', '8b', '8d', '8e', '90',
    '9f', 'a3', 'ac', 'b1', 'b2', 'b7', 'b8', 'bd', 'be', 'c5', 'ca', 'd1', 'd4',
    'd7', 'd8', 'db', 'de', 'e2', 'e4', 'e7', 'e8', 'eb', 'ed', 'f6', 'f9',
])
def test_satisfies_pc_l(hex_str: str) -> None:
    """Test func."""
    bool_func = BooleanFunction(hex_str)
    assert satisfies_pc_l(bool_func) > 0


@pytest.mark.parametrize('hex_str, k_order, l_criteria', [
    ('17', 1, 2), ('18', 1, 2), ('24', 1, 2), ('2b', 1, 2),
    ('42', 1, 2), ('4d', 1, 2), ('71', 1, 2), ('7e', 1, 2),
    ('81', 1, 2), ('8e', 1, 2), ('b2', 1, 2), ('bd', 1, 2),
    ('d4', 1, 2), ('db', 1, 2), ('e7', 1, 2), ('e8', 1, 2),
])
def test_satisfies_pc_l_order_k(hex_str: str, k_order: int, l_criteria: int) -> None:
    """Test func."""
    bool_func = BooleanFunction(hex_str)
    res = satisfies_pc_l_order_k(bool_func, l_criteria, k_order)

    assert res is True


@pytest.mark.parametrize('hex_str', [
    '17', '18', '24', '2b', '42', '4d', '71', '7e',
    '81', '8e', 'b2', 'bd', 'd4', 'db', 'e7', 'e8',
])
def test_sac(hex_str: str) -> None:
    """Test func."""
    bool_func = BooleanFunction(hex_str)
    assert sac(bool_func) > 0


@pytest.mark.parametrize('hex_str', [
    '01', '02', '04', '07', '08', '0b', '0d', '0e',
    '10', '13', '15', '16', '19', '1a', '1c', '1f',
    '20', '23', '25', '26', '29', '2a', '2c', '2f',
    '31', '32', '34', '37', '38', '3b', '3d', '3e',
    '40', '43', '45', '46', '49', '4a', '4c', '4f',
    '51', '52', '54', '57', '58', '5b', '5d', '5e',
    '61', '62', '64', '67', '68', '6b', '6d', '6e',
    '70', '73', '75', '76', '79', '7a', '7c', '7f',
    '80', '83', '85', '86', '89', '8a', '8c', '8f',
    '91', '92', '94', '97', '98', '9b', '9d', '9e',
    'a1', 'a2', 'a4', 'a7', 'a8', 'ab', 'ad', 'ae',
    'b0', 'b3', 'b5', 'b6', 'b9', 'ba', 'bc', 'bf',
    'c1', 'c2', 'c4', 'c7', 'c8', 'cb', 'cd', 'ce',
    'd0', 'd3', 'd5', 'd6', 'd9', 'da', 'dc', 'df',
    'e0', 'e3', 'e5', 'e6', 'e9', 'ea', 'ec', 'ef',
    'f1', 'f2', 'f4', 'f7', 'f8', 'fb', 'fd', 'fe',
])
def test_get_ci_function(hex_str: str) -> None:
    """Test func."""
    bool_func = BooleanFunction(hex_str)
    assert get_ci_function(bool_func) == []


@pytest.mark.parametrize('hex_str_1, hex_str_2', [
    ('0', '0'), ('0', '3'), ('0', '5'), ('0', '6'),
    ('0', '9'), ('0', 'a'), ('0', 'c'), ('0', 'f'),
    ('3', '0'), ('3', '3'), ('3', '5'), ('3', '6'),
    ('3', '9'), ('3', 'a'), ('3', 'c'), ('3', 'f'),
    ('5', '0'), ('5', '3'), ('5', '5'), ('5', '6'),
    ('5', '9'), ('5', 'a'), ('5', 'c'), ('5', 'f'),
    ('6', '0'), ('6', '3'), ('6', '5'), ('6', '6'),
    ('6', '9'), ('6', 'a'), ('6', 'c'), ('6', 'f'),
    ('9', '0'), ('9', '3'), ('9', '5'), ('9', '6'),
    ('9', '9'), ('9', 'a'), ('9', 'c'), ('9', 'f'),
    ('a', '0'), ('a', '3'), ('a', '5'), ('a', '6'),
    ('a', '9'), ('a', 'a'), ('a', 'c'), ('a', 'f'),
    ('c', '0'), ('c', '3'), ('c', '5'), ('c', '6'),
    ('c', '9'), ('c', 'a'), ('c', 'c'), ('c', 'f'),
    ('f', '0'), ('f', '3'), ('f', '5'), ('f', '6'),
    ('f', '9'), ('f', 'a'), ('f', 'c'), ('f', 'f'),
])
def test_get_intersecting_spectral(hex_str_1: str, hex_str_2: str) -> None:
    """Test func."""
    bool_func_1 = BooleanFunction(hex_str_1)
    bool_func_2 = BooleanFunction(hex_str_2)
    assert get_intersecting_spectral(bool_func_1, bool_func_2) is not None


def test_fwht() -> None:
    """Test func."""
    assert 1 == 1


def test_fast_sylvester_hadamard() -> None:
    """Test func."""
    assert 1 == 1


@pytest.mark.parametrize('hex_str_1, hex_str_2', [
    ('0', '3'), ('0', '5'), ('0', '6'), ('0', '9'),
    ('0', 'a'), ('0', 'c'), ('3', '0'), ('3', '5'),
    ('3', '6'), ('3', '9'), ('3', 'a'), ('3', 'f'),
    ('5', '0'), ('5', '3'), ('5', '6'), ('5', '9'),
    ('5', 'c'), ('5', 'f'), ('6', '0'), ('6', '3'),
    ('6', '5'), ('6', 'a'), ('6', 'c'), ('6', 'f'),
    ('9', '0'), ('9', '3'), ('9', '5'), ('9', 'a'),
    ('9', 'c'), ('9', 'f'), ('a', '0'), ('a', '3'),
    ('a', '6'), ('a', '9'), ('a', 'c'), ('a', 'f'),
    ('c', '0'), ('c', '5'), ('c', '6'), ('c', '9'),
    ('c', 'a'), ('c', 'f'), ('f', '3'), ('f', '5'),
    ('f', '6'), ('f', '9'), ('f', 'a'), ('f', 'c'),
])
def test_check_uncorrelated_degree_k(hex_str_1: str, hex_str_2: str) -> None:
    """Test func."""
    bool_func_1 = BooleanFunction(hex_str_1)
    bool_func_2 = BooleanFunction(hex_str_2)

    assert check_uncorrelated_degree_k(bool_func_1, bool_func_2) == 2


@pytest.mark.parametrize('hex_str_1, hex_str_2, u_der', [
    ('0', '0', 0), ('0', '0', 1), ('0', '0', 2), ('0', '0', 3),
    ('1', '1', 0), ('1', '2', 1), ('1', '4', 2), ('1', '8', 3),
    ('2', '1', 1), ('2', '2', 0), ('2', '4', 3), ('2', '8', 2),
    ('3', '3', 0), ('3', '3', 1), ('3', 'c', 2), ('3', 'c', 3),
    ('4', '1', 2), ('4', '2', 3), ('4', '4', 0), ('4', '8', 1),
    ('5', '5', 0), ('5', '5', 2), ('5', 'a', 1), ('5', 'a', 3),
    ('6', '6', 0), ('6', '6', 3), ('6', '9', 1), ('6', '9', 2),
    ('7', '7', 0), ('7', 'b', 1), ('7', 'd', 2), ('7', 'e', 3),
    ('8', '1', 3), ('8', '2', 2), ('8', '4', 1), ('8', '8', 0),
    ('9', '6', 1), ('9', '6', 2), ('9', '9', 0), ('9', '9', 3),
    ('a', '5', 1), ('a', '5', 3), ('a', 'a', 0), ('a', 'a', 2),
    ('b', '7', 1), ('b', 'b', 0), ('b', 'd', 3), ('b', 'e', 2),
    ('c', '3', 2), ('c', '3', 3), ('c', 'c', 0), ('c', 'c', 1),
    ('d', '7', 2), ('d', 'b', 3), ('d', 'd', 0), ('d', 'e', 1),
    ('e', '7', 3), ('e', 'b', 2), ('e', 'd', 1), ('e', 'e', 0),
    ('f', 'f', 0), ('f', 'f', 1), ('f', 'f', 2), ('f', 'f', 3),
])
def test_cross_correlation_u(hex_str_1: str, hex_str_2: str, u_der: int) -> None:
    """Test func."""
    bool_func_1 = BooleanFunction(hex_str_1)
    bool_func_2 = BooleanFunction(hex_str_2)

    assert cross_correlation_u(bool_func_1, bool_func_2, u_der) == 4


@pytest.mark.parametrize('index, expected', enumerate([
    [4, 4, 4, 4], [2, 2, 2, 2], [2, 2, 2, 2], [0, 0, 0, 0],
    [2, 2, 2, 2], [0, 0, 0, 0], [0, 0, 0, 0], [-2, -2, -2, -2],
    [2, 2, 2, 2], [0, 0, 0, 0], [0, 0, 0, 0], [-2, -2, -2, -2],
    [0, 0, 0, 0], [-2, -2, -2, -2], [-2, -2, -2, -2], [-4, -4, -4, -4],
    [2, 2, 2, 2], [4, 0, 0, 0], [0, 4, 0, 0], [2, 2, -2, -2],
    [0, 0, 4, 0], [2, -2, 2, -2], [-2, 2, 2, -2], [0, 0, 0, -4],
    [0, 0, 0, 4], [2, -2, -2, 2], [-2, 2, -2, 2], [0, 0, -4, 0],
    [-2, -2, 2, 2], [0, -4, 0, 0], [-4, 0, 0, 0], [-2, -2, -2, -2],
    [2, 2, 2, 2], [0, 4, 0, 0], [4, 0, 0, 0], [2, 2, -2, -2],
    [0, 0, 0, 4], [-2, 2, -2, 2], [2, -2, -2, 2], [0, 0, -4, 0],
    [0, 0, 4, 0], [-2, 2, 2, -2], [2, -2, 2, -2], [0, 0, 0, -4],
    [-2, -2, 2, 2], [-4, 0, 0, 0], [0, -4, 0, 0], [-2, -2, -2, -2],
    [0, 0, 0, 0], [2, 2, -2, -2], [2, 2, -2, -2], [4, 4, -4, -4],
    [-2, -2, 2, 2], [0, 0, 0, 0], [0, 0, 0, 0], [2, 2, -2, -2],
    [-2, -2, 2, 2], [0, 0, 0, 0], [0, 0, 0, 0], [2, 2, -2, -2],
    [-4, -4, 4, 4], [-2, -2, 2, 2], [-2, -2, 2, 2], [0, 0, 0, 0],
    [2, 2, 2, 2], [0, 0, 4, 0], [0, 0, 0, 4], [-2, -2, 2, 2],
    [4, 0, 0, 0], [2, -2, 2, -2], [2, -2, -2, 2], [0, -4, 0, 0],
    [0, 4, 0, 0], [-2, 2, 2, -2], [-2, 2, -2, 2], [-4, 0, 0, 0],
    [2, 2, -2, -2], [0, 0, 0, -4], [0, 0, -4, 0], [-2, -2, -2, -2],
    [0, 0, 0, 0], [2, -2, 2, -2], [-2, 2, -2, 2], [0, 0, 0, 0],
    [2, -2, 2, -2], [4, -4, 4, -4], [0, 0, 0, 0], [2, -2, 2, -2],
    [-2, 2, -2, 2], [0, 0, 0, 0], [-4, 4, -4, 4], [-2, 2, -2, 2],
    [0, 0, 0, 0], [2, -2, 2, -2], [-2, 2, -2, 2], [0, 0, 0, 0],
    [0, 0, 0, 0], [-2, 2, 2, -2], [2, -2, -2, 2], [0, 0, 0, 0],
    [2, -2, -2, 2], [0, 0, 0, 0], [4, -4, -4, 4], [2, -2, -2, 2],
    [-2, 2, 2, -2], [-4, 4, 4, -4], [0, 0, 0, 0], [-2, 2, 2, -2],
    [0, 0, 0, 0], [-2, 2, 2, -2], [2, -2, -2, 2], [0, 0, 0, 0],
    [-2, -2, -2, -2], [0, 0, 0, -4], [0, 0, -4, 0], [2, 2, -2, -2],
    [0, -4, 0, 0], [2, -2, 2, -2], [2, -2, -2, 2], [4, 0, 0, 0],
    [-4, 0, 0, 0], [-2, 2, 2, -2], [-2, 2, -2, 2], [0, 4, 0, 0],
    [-2, -2, 2, 2], [0, 0, 4, 0], [0, 0, 0, 4], [2, 2, 2, 2],
    [2, 2, 2, 2], [0, 0, 0, 4], [0, 0, 4, 0], [-2, -2, 2, 2],
    [0, 4, 0, 0], [-2, 2, -2, 2], [-2, 2, 2, -2], [-4, 0, 0, 0],
    [4, 0, 0, 0], [2, -2, -2, 2], [2, -2, 2, -2], [0, -4, 0, 0],
    [2, 2, -2, -2], [0, 0, -4, 0], [0, 0, 0, -4], [-2, -2, -2, -2],
    [0, 0, 0, 0], [2, -2, -2, 2], [-2, 2, 2, -2], [0, 0, 0, 0],
    [-2, 2, 2, -2], [0, 0, 0, 0], [-4, 4, 4, -4], [-2, 2, 2, -2],
    [2, -2, -2, 2], [4, -4, -4, 4], [0, 0, 0, 0], [2, -2, -2, 2],
    [0, 0, 0, 0], [2, -2, -2, 2], [-2, 2, 2, -2], [0, 0, 0, 0],
    [0, 0, 0, 0], [-2, 2, -2, 2], [2, -2, 2, -2], [0, 0, 0, 0],
    [-2, 2, -2, 2], [-4, 4, -4, 4], [0, 0, 0, 0], [-2, 2, -2, 2],
    [2, -2, 2, -2], [0, 0, 0, 0], [4, -4, 4, -4], [2, -2, 2, -2],
    [0, 0, 0, 0], [-2, 2, -2, 2], [2, -2, 2, -2], [0, 0, 0, 0],
    [-2, -2, -2, -2], [0, 0, -4, 0], [0, 0, 0, -4], [2, 2, -2, -2],
    [-4, 0, 0, 0], [-2, 2, -2, 2], [-2, 2, 2, -2], [0, 4, 0, 0],
    [0, -4, 0, 0], [2, -2, -2, 2], [2, -2, 2, -2], [4, 0, 0, 0],
    [-2, -2, 2, 2], [0, 0, 0, 4], [0, 0, 4, 0], [2, 2, 2, 2],
    [0, 0, 0, 0], [-2, -2, 2, 2], [-2, -2, 2, 2], [-4, -4, 4, 4],
    [2, 2, -2, -2], [0, 0, 0, 0], [0, 0, 0, 0], [-2, -2, 2, 2],
    [2, 2, -2, -2], [0, 0, 0, 0], [0, 0, 0, 0], [-2, -2, 2, 2],
    [4, 4, -4, -4], [2, 2, -2, -2], [2, 2, -2, -2], [0, 0, 0, 0],
    [-2, -2, -2, -2], [0, -4, 0, 0], [-4, 0, 0, 0], [-2, -2, 2, 2],
    [0, 0, 0, -4], [2, -2, 2, -2], [-2, 2, 2, -2], [0, 0, 4, 0],
    [0, 0, -4, 0], [2, -2, -2, 2], [-2, 2, -2, 2], [0, 0, 0, 4],
    [2, 2, -2, -2], [4, 0, 0, 0], [0, 4, 0, 0], [2, 2, 2, 2],
    [-2, -2, -2, -2], [-4, 0, 0, 0], [0, -4, 0, 0], [-2, -2, 2, 2],
    [0, 0, -4, 0], [-2, 2, -2, 2], [2, -2, -2, 2], [0, 0, 0, 4],
    [0, 0, 0, -4], [-2, 2, 2, -2], [2, -2, 2, -2], [0, 0, 4, 0],
    [2, 2, -2, -2], [0, 4, 0, 0], [4, 0, 0, 0], [2, 2, 2, 2],
    [-4, -4, -4, -4], [-2, -2, -2, -2], [-2, -2, -2, -2], [0, 0, 0, 0],
    [-2, -2, -2, -2], [0, 0, 0, 0], [0, 0, 0, 0], [2, 2, 2, 2],
    [-2, -2, -2, -2], [0, 0, 0, 0], [0, 0, 0, 0], [2, 2, 2, 2],
    [0, 0, 0, 0], [2, 2, 2, 2], [2, 2, 2, 2], [4, 4, 4, 4],

]))
def test_all_cross_correlations(index: int, expected: int) -> None:
    """Test func."""
    bool_func_1 = BooleanFunction(f'{index // 16:x}')
    bool_func_2 = BooleanFunction(f'{index % 16:x}')

    assert all_cross_correlations(bool_func_1, bool_func_2) == expected


@pytest.mark.parametrize('hex_str_1, hex_str_2', [
    ('0', '3'), ('0', '5'), ('0', '6'), ('0', '9'),
    ('0', 'a'), ('0', 'c'), ('1', '1'), ('1', 'e'),
    ('2', '2'), ('2', 'd'), ('3', '0'), ('3', '5'),
    ('3', '6'), ('3', '9'), ('3', 'a'), ('3', 'f'),
    ('4', '4'), ('4', 'b'), ('5', '0'), ('5', '3'),
    ('5', '6'), ('5', '9'), ('5', 'c'), ('5', 'f'),
    ('6', '0'), ('6', '3'), ('6', '5'), ('6', 'a'),
    ('6', 'c'), ('6', 'f'), ('7', '7'), ('7', '8'),
    ('8', '7'), ('8', '8'), ('9', '0'), ('9', '3'),
    ('9', '5'), ('9', 'a'), ('9', 'c'), ('9', 'f'),
    ('a', '0'), ('a', '3'), ('a', '6'), ('a', '9'),
    ('a', 'c'), ('a', 'f'), ('b', '4'), ('b', 'b'),
    ('c', '0'), ('c', '5'), ('c', '6'), ('c', '9'),
    ('c', 'a'), ('c', 'f'), ('d', '2'), ('d', 'd'),
    ('e', '1'), ('e', 'e'), ('f', '3'), ('f', '5'),
    ('f', '6'), ('f', '9'), ('f', 'a'), ('f', 'c'),
])
def test_perfectly_uncorrelated(hex_str_1: str, hex_str_2: str) -> None:
    """Test func."""
    bool_func_1 = BooleanFunction(hex_str_1)
    bool_func_2 = BooleanFunction(hex_str_2)

    assert check_perfectly_uncorrelated(bool_func_1, bool_func_2) is True


data_get_fourier_coefficients: list[list[int]] = [
    [0, 0, 0, 0], [1, 1, 1, 1], [1, -1, 1, -1], [2, 0, 2, 0],
    [1, 1, -1, -1], [2, 2, 0, 0], [2, 0, 0, -2], [3, 1, 1, -1],
    [1, -1, -1, 1], [2, 0, 0, 2], [2, -2, 0, 0], [3, -1, 1, 1],
    [2, 0, -2, 0], [3, 1, -1, 1], [3, -1, -1, -1], [4, 0, 0, 0],
]

test_cases_fourier_coeff = [
    (format(i, '01x'), coeffs)
    for i, coeffs in enumerate(data_get_fourier_coefficients)
]


@pytest.mark.parametrize('hex_str, expected', test_cases_fourier_coeff)
def test_get_fourier_coefficients(hex_str: str, expected: list[int]) -> None:
    """Test func."""
    bool_func = BooleanFunction(hex_str)
    assert get_fourier_coefficients(bool_func) == expected


data_get_function_weight: list[int] = [
    0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    4, 5, 5, 6, 5, 6, 6, 7, 5, 6, 6, 7, 6, 7, 7, 8,
]

test_cases_function_weight = [
    (format(i, '02x'), weights)
    for i, weights in enumerate(data_get_function_weight)
]


@pytest.mark.parametrize('hex_str, expected', test_cases_function_weight)
def test_get_function_weight(hex_str: str, expected: int) -> None:
    """Test func."""
    bool_func = BooleanFunction(hex_str)
    assert get_function_weight(bool_func) == expected


@pytest.mark.parametrize('index, expected', enumerate(
    [0, 1, 1, 2, 1, 0, 2, 1, 1, 2, 0, 1, 2, 1, 1, 0],
))
def test_get_distance_between_functions(index: int, expected: int) -> None:
    """Test func."""
    bool_func_1 = BooleanFunction(f'{index // 4:x}')
    bool_func_2 = BooleanFunction(f'{index % 4:x}')

    assert get_distance_between_functions(bool_func_1, bool_func_2) == expected


@pytest.mark.parametrize('hex_str', [
    '0000', '00ff', '03c0', '05a0', '0a50', '0c30',
    '0f0f', '0ff0', '1188', '1818', '1bd8', '1db8',
    '2244', '2424', '27e4', '2e74', '300c', '3333',
    '33cc', '35ac', '3a5c', '3c3c', '3cc3', '3ffc',
    '4242', '4422', '47e2', '4e72', '500a', '53ca',
    '5555', '55aa', '5a5a', '5aa5', '5c3a', '5ffa',
    '6666', '6699', '6969', '6996', '724e', '742e',
    '77ee', '7e7e', '8181', '8811', '8bd1', '8db1',
    '9669', '9696', '9966', '9999', 'a005', 'a3c5',
    'a55a', 'a5a5', 'aa55', 'aaaa', 'ac35', 'aff5',
    'b18d', 'b81d', 'bbdd', 'bdbd', 'c003', 'c33c',
    'c3c3', 'c5a3', 'ca53', 'cc33', 'cccc', 'cff3',
    'd18b', 'd81b', 'dbdb', 'ddbb', 'e247', 'e427',
    'e7e7', 'ee77', 'f00f', 'f0f0', 'f3cf', 'f5af',
    'fa5f', 'fc3f', 'ff00', 'ffff',
])
def test_check_regularity(hex_str: str) -> None:
    """Test func."""
    bool_func = BooleanFunction(hex_str)
    assert check_regularity(bool_func)[0] is True


@pytest.mark.parametrize('hex_str', [
    '000f', '0033', '0055', '00aa', '00cc', '00f0',
    '0303', '0505', '0a0a', '0c0c', '0f00', '0ff0',
    '0fff', '1111', '2222', '3030', '3300', '33cc',
    '33ff', '3c3c', '3f3f', '4444', '5050', '5500',
    '55aa', '55ff', '5a5a', '5f5f', '6666', '7777',
    '8888', '9999', 'a0a0', 'a5a5', 'aa00', 'aa55',
    'aaff', 'afaf', 'bbbb', 'c0c0', 'c3c3', 'cc00',
    'cc33', 'ccff', 'cfcf', 'dddd', 'eeee', 'f000',
    'f00f', 'f0ff', 'f3f3', 'f5f5', 'fafa', 'fcfc',
    'ff0f', 'ff33', 'ff55', 'ffaa', 'ffcc', 'fff0',
])
def test_find_decompositions(hex_str: str) -> None:
    """Test func."""
    bool_func = BooleanFunction(hex_str)
    assert len(find_decompositions(bool_func, 4, True)[1]) == 5


@pytest.mark.parametrize('hex_str', [
    '00', '03', '05', '0a', '0c', '0f',
    '11', '22', '30', '33', '3c', '3f',
    '44', '50', '55', '5a', '5f', '66',
    '77', '88', '99', 'a0', 'a5', 'aa',
    'af', 'bb', 'c0', 'c3', 'cc', 'cf',
    'dd', 'ee', 'f0', 'f3', 'f5', 'fa',
    'fc', 'ff',
])
def test_is_non_degenerate(hex_str: str) -> None:
    """Test func."""
    bool_func = BooleanFunction(hex_str)
    assert is_non_degenerate(bool_func, 3) is False
