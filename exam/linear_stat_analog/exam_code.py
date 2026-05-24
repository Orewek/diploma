# -*- coding: utf-8 -*-
"""Module for generating Boolean function tasks with linear stat. analogs."""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from random import randint

from sage.all import latex
from sage.crypto.boolean_function import BooleanFunction

# Константы
N_VARS_FUNC = 4
TT_SIZE = 2**N_VARS_FUNC


@dataclass
class BooleanVariant:
    """Class storing data for a Boolean function variant."""

    bool_func: BooleanFunction
    truth_table: list[int]
    anf_matrix: list[list[int]]

    @property
    def tt_str(self) -> str:
        """Return the truth table as a string."""
        return ''.join(map(str, self.truth_table))


def generate_boolean_function() -> 'BooleanFunction':
    """Generate a random Boolean function with nonlinearity at least 4.

    Returns:
    --------
        bool function
    """
    while True:
        truth_table = [randint(0, 1) for _ in range(TT_SIZE)]
        bool_func = BooleanFunction(truth_table)
        if bool_func.nonlinearity() >= 4:
            return bool_func


def compute_anf_matrix(truth_table: list[int]) -> list[list[int]]:
    """Compute the triangle matrix for determining the ANF.

    Args:
    -----
        truth_table: tt

    Returns:
    --------
        Triangle matrix
    """
    matrix = [list(truth_table)]
    current = list(truth_table)
    for _ in range(TT_SIZE - 1):
        next_row = [current[i] ^ current[i + 1] for i in range(len(current) - 1)]
        matrix.append(next_row)
        current = next_row

    return matrix


def get_latex_walsh_table(bool_func: BooleanFunction) -> str:
    """Generate rows for the Walsh-Hadamard transform LaTeX table.

    Args:
    -----
        bool_func: boolean function

    Returns:
    --------
        rows of W_f table
    """
    walsh_hadamard_values = bool_func.walsh_hadamard_transform()
    return '\n'.join(
        [
            f'        \\texttt{{{i:04b}}} & {walsh_hadamard_values[i]:2d} \\\\'
            for i in range(16)
        ],
    )


def find_best_linear_approximation(bool_func: BooleanFunction) -> str:
    """Return the vector and value of the best linear statistic analog.

    Args:
    -----
        bool_func: boolean function

    Returns:
    --------
        vector/value lin stat analog
    """
    walsh_hadamard_values = bool_func.walsh_hadamard_transform()
    max_val = max(abs(x) for x in walsh_hadamard_values)
    for i, val in enumerate(walsh_hadamard_values):
        if abs(val) == max_val:
            return f'{i:0{N_VARS_FUNC}b}'

    return ''


def build_latex_content(variants: list[BooleanVariant]) -> str:
    """Build the full LaTeX file content with answer keys.

    Args:
    -----
        variants: exam variants

    Returns:
    --------
        tasks and answers content
    """
    task_block = (
        r'\begin{enumerate}'
        r'\item Построить АНФ методом треугольника.'
        r'\item Найти нелинейность $N_f$.'
        r'\item Найти ближайший линейный статистический аналог.'
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
        best_linear = find_best_linear_approximation(v.bool_func)

        triangle_rows_list = [
            f"{step} & \\texttt{''.join(map(str, row))} \\\\"
            for step, row in enumerate(v.anf_matrix)
        ]
        triangle_rows = '\n'.join(triangle_rows_list)

        ans_block = f"""
        \\begin{{minipage}}{{\\linewidth}}
        \\noindent\\textbf{{\\fbox{{{i}}}}} \\texttt{{{v.tt_str}}} \\\\
        ${latex(v.bool_func.algebraic_normal_form())}$ \\\\
        $N_f = {non_linear}$ \\\\
        Ближайший аналог: $\\langle {best_linear}, x \\rangle$

        \\begin{{multicols}}{{2}}
        \\footnotesize
        \\begin{{tabular}}{{|c|c|}} \\hline
        $u$ & $W_f(u)$ \\\\ \\hline
        {walsh_rows}
        \\hline \\end{{tabular}}

        \\columnbreak

        \\begin{{tabular}}{{|r|l|}} \\hline
        \\multicolumn{{2}}{{|c|}}{{АНФ треугольник}} \\\\ \\hline
        {triangle_rows}
        \\hline \\end{{tabular}}
        \\end{{multicols}}
        \\hrule \\bigskip \\end{{minipage}}
        """
        answers.append(ans_block)

    return header + tasks + '\\small\n' + '\n'.join(answers) + r'\end{document}'


def compile_pdf(tex_path: Path) -> None:
    """Compile the LaTeX file into a PDF document.

    Args:
    -----
        text_path: path to a tex file
    """
    subprocess.run(
        ['pdflatex', '-interaction=nonstopmode', tex_path.name],
        cwd=tex_path.parent,
        capture_output=True,
        check=True,
    )


def main() -> None:
    """Main entry point to generate variants and build the PDF."""
    variant_count = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    variants: list[BooleanVariant] = []
    used_truth_tables: set[tuple[int, ...]] = set()

    while len(variants) < variant_count:
        bool_func = generate_boolean_function()

        tt = [int(element) for element in bool_func.truth_table()]
        tt_tuple = tuple(tt)
        if tt_tuple not in used_truth_tables:
            used_truth_tables.add(tt_tuple)
            variants.append(
                BooleanVariant(bool_func, tt, compute_anf_matrix(tt)),
            )

    script_path = Path(__file__).resolve().parent
    tex_file = script_path / 'boolean_tasks.tex'

    tex_file.write_text(build_latex_content(variants), encoding='utf-8')
    compile_pdf(tex_file)


if __name__ == '__main__':
    main()
