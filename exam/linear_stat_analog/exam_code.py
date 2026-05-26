# -*- coding: utf-8 -*-
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from random import randint

from sage.all import latex
from sage.crypto.boolean_function import BooleanFunction
from sage.rings.polynomial.polynomial_ring_constructor import (
    BooleanPolynomialRing_constructor,
)

N_VARS_FUNC = 4
TT_SIZE = 2**N_VARS_FUNC


@dataclass
class BooleanVariant:
    bool_func: BooleanFunction
    truth_table: list[int]
    mobius_table: list[tuple[str, int]]

    @property
    def tt_str(self) -> str:
        return ''.join(map(str, self.truth_table))


def generate_boolean_function() -> 'BooleanFunction':
    while True:
        truth_table = [randint(0, 1) for _ in range(TT_SIZE)]
        bool_func = BooleanFunction(truth_table)
        if bool_func.nonlinearity() >= 4:
            return bool_func


def compute_mobius_transform(truth_table: list[int]) -> list[tuple[str, int]]:
    a = list(truth_table)
    n = N_VARS_FUNC

    for i in range(n):
        bit = 1 << i
        for j in range(1 << n):
            if j & bit:
                a[j] ^= a[j ^ bit]

    mobius_table = []
    for i in range(len(a)):
        binary_vector = f'{i:0{n}b}'[::-1]
        mobius_table.append((binary_vector, a[i]))

    return mobius_table


def get_latex_walsh_table(bool_func: BooleanFunction) -> str:
    walsh_hadamard_values = bool_func.walsh_hadamard_transform()
    return '\n'.join(
        [
            f'        \\texttt{{{i:04b}}} & {walsh_hadamard_values[i]:2d} \\\\'
            for i in range(16)
        ],
    )


def find_linear_statistical_analogs(bool_func: BooleanFunction) -> list[str]:
    """Находит все линейные статистические аналоги (аффинные функции)."""
    walsh_hadamard_values = bool_func.walsh_hadamard_transform()

    max_val = max(abs(int(x)) for x in walsh_hadamard_values)

    analogs = []
    for i, val in enumerate(walsh_hadamard_values):
        if abs(int(val)) == max_val:
            vector_str = f'{i:0{N_VARS_FUNC}b}'
            if val < 0:
                analogs.append(f'1 + \\langle {vector_str}, x \\rangle')
            else:
                analogs.append(f'\\langle {vector_str}, x \\rangle')

    return analogs


def get_anf_with_ones_indices(bool_func: BooleanFunction) -> str:
    poly = bool_func.algebraic_normal_form()

    new_names = [f'x_{i}' for i in range(1, N_VARS_FUNC + 1)]
    new_ring = BooleanPolynomialRing_constructor(N_VARS_FUNC, new_names)

    # {x0: x_1, x1: x_2, ...}
    substitution_dict = dict(zip(poly.parent().gens(), new_ring.gens()))

    substituted_poly = poly.subs(substitution_dict)

    return latex(substituted_poly)


def build_latex_content(variants: list[BooleanVariant]) -> str:
    task_block = (
        r'\begin{enumerate}'
        r'\item Построить АНФ преобразованием Мёбиуса.'
        r'\item Найти нелинейность $N_f$.'
        r'\item Найти все линейные статистические аналоги.'
        r'\end{enumerate}'
    )

    header = (
        r'\documentclass[11pt]{article}'
        r'\usepackage[utf8]{inputenc}'
        r'\usepackage[russian]{babel}'
        r'\usepackage{amsmath,amssymb,amsfonts}'
        r'\usepackage{geometry}'
        r'\usepackage{multicol}'
        r'\geometry{top=1.5cm,bottom=1.5cm,left=1.2cm,right=1.2cm}'
        r'\newcounter{NM}'
        r'\newcommand{\Ex}[1]{'
        r'\par\addtocounter{NM}{1}\noindent\parbox[c]{\columnwidth}{'
        r'\hrule height .5pt width \columnwidth\smallskip'
        r'\centerline{\sffamily\bfseries Вариант \arabic{NM}.}'
        r'\smallskip $f(x) = \mathtt{#1}$' + task_block +
        r'\hrule height .5pt width \columnwidth\bigskip}}'
        r'\begin{document}\pagestyle{empty}\twocolumn'
    )

    tasks = '\n'.join([f'\\Ex{{{v.tt_str}}}' for v in variants])

    answers = []
    for i, v in enumerate(variants, 1):
        walsh_rows = get_latex_walsh_table(v.bool_func)
        non_linear = v.bool_func.nonlinearity()
        analogs = find_linear_statistical_analogs(v.bool_func)
        analogs_latex = ', '.join([f'${a}$' for a in analogs])
        anf_latex = get_anf_with_ones_indices(v.bool_func)

        mobius_rows_list = [
            f'\\texttt{{{vector}}} & {coeff} \\\\'
            for vector, coeff in v.mobius_table
        ]
        mobius_rows = '\n'.join(mobius_rows_list)

        ans_block = f"""
        \\begin{{minipage}}{{\\linewidth}}
        \\noindent\\textbf{{\\fbox{{{i}}}}} \\texttt{{{v.tt_str}}} \\\\
        ${anf_latex}$ \\\\
        $N_f = {non_linear}$ \\\\
        {analogs_latex}

        \\begin{{multicols}}{{2}}
        \\footnotesize
        \\begin{{tabular}}{{|c|c|}} \\hline
        $u$ & $W_f(u)$ \\\\ \\hline
        {walsh_rows}
        \\hline \\end{{tabular}}

        \\columnbreak

        \\begin{{tabular}}{{|c|c|}} \\hline
        \\multicolumn{{2}}{{|c|}}{{Преобр. Мёбиуса}} \\\\ \\hline
        $g$ & $c_g$ \\\\ \\hline
        {mobius_rows}
        \\hline \\end{{tabular}}
        \\end{{multicols}}
        \\hrule \\bigskip \\end{{minipage}}
        """
        answers.append(ans_block)

    return header + tasks + '\\small\n' + '\n'.join(answers) + r'\end{document}'


def compile_pdf(tex_path: Path) -> None:
    subprocess.run(
        ['pdflatex', '-interaction=nonstopmode', tex_path.name],
        cwd=tex_path.parent,
        capture_output=True,
        check=True,
    )


def main() -> None:
    variant_count = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    variants: list[BooleanVariant] = []
    used_truth_tables: set[tuple[int, ...]] = set()

    while len(variants) < variant_count:
        bool_func = generate_boolean_function()

        tt = [int(element) for element in bool_func.truth_table()]
        tt_tuple = tuple(tt)
        if tt_tuple not in used_truth_tables:
            used_truth_tables.add(tt_tuple)
            variants.append(
                BooleanVariant(bool_func, tt, compute_mobius_transform(tt)),
            )

    script_path = Path(__file__).resolve().parent
    tex_file = script_path / 'boolean_tasks.tex'

    tex_file.write_text(build_latex_content(variants), encoding='utf-8')
    compile_pdf(tex_file)


if __name__ == '__main__':
    main()
