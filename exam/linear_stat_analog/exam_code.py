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
        binary_vector = f'{i:0{n}b}'

        reversed_index = int(binary_vector[::-1], 2)

        mobius_table.append((binary_vector, a[reversed_index]))

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

# Список активных задач. Чтобы убрать задачу из контрольной,
# просто закомментируй или удали соответствующую строку.
ACTIVE_TASKS = [
    'anf',           # Построить АНФ преобразованием Мёбиуса
    'nonlinearity',  # Найти нелинейность Nf
    'analogs',       # Найти линейные статистические аналоги
    # 'derivative',  # Вычислить дискретную производную \Delta_a f(x)
]

def build_latex_content(variants: list[BooleanVariant], active_tasks: list[str] = ACTIVE_TASKS) -> str:
    # 1. Динамически собираем блок заданий
    questions_latex = []
    if 'anf' in active_tasks:
        questions_latex.append(r'\item Построить АНФ преобразованием Мёбиуса.')
    if 'nonlinearity' in active_tasks:
        questions_latex.append(r'\item Найти нелинейность $N_f$.')
    if 'analogs' in active_tasks:
        questions_latex.append(r'\item Найти все линейные статистические аналоги.')
    if 'derivative' in active_tasks:
        questions_latex.append(r'\item Найти дискретную производную $\Delta_a f(x)$.')

    task_block = r'\begin{enumerate}' + ''.join(questions_latex) + r'\end{enumerate}' if questions_latex else ''

    header = (
        r'\documentclass[11pt]{article}'
        r'\usepackage[utf8]{inputenc}'
        r'\usepackage[russian]{babel}'
        r'\usepackage{amsmath,amssymb,amsfonts}'
        r'\usepackage{geometry}'
        r'\geometry{top=1.2cm,bottom=1.2cm,left=1.2cm,right=1.2cm}'
        r'\newcounter{NM}'
        r'\newcommand{\Ex}[1]{'
        r'\par\addtocounter{NM}{1}\noindent\parbox[c]{\columnwidth}{'
        r'\hrule height .5pt width \columnwidth\smallskip'
        r'\centerline{\sffamily\bfseries Вариант \arabic{NM}.}'
        r'\smallskip $f(x) = \mathtt{#1}$' + task_block +
        r'\hrule height .5pt width \columnwidth\bigskip}}'
        r'\begin{document}\pagestyle{empty}\twocolumn'
    )

    tasks = '\n'.join([f'\\Ex{{{v.tt_str[::-1]}}}' for v in variants])

    answers_header = r'\clearpage\onecolumn\centerline{\Large\bfseries Ответы}\bigskip'
    
    answers = []
    for i, v in enumerate(variants, 1):
        tt_rev = v.truth_table[::-1]
        
        # 2. Динамически собираем строчки с короткими ответами
        ans_header_info = []
        
        if 'anf' in active_tasks:
            anf_latex = get_anf_with_ones_indices(v.bool_func)
            ans_header_info.append(f'АНФ: ${anf_latex}$')
            
        if 'nonlinearity' in active_tasks:
            non_linear = v.bool_func.nonlinearity()
            ans_header_info.append(f'$N_f = {non_linear}$')
            
        if 'analogs' in active_tasks:
            analogs = find_linear_statistical_analogs(v.bool_func)
            analogs_latex = ', '.join([f'${a}$' for a in analogs]) if analogs else 'нет'
            ans_header_info.append(f'Аналоги: {analogs_latex}')

        if 'derivative' in active_tasks:
            ans_header_info.append(r'$\Delta_a f(x)$: (в разработке)')

        ans_header_latex = ' \\\\\n        '.join(ans_header_info)
        
        # 3. Динамически собираем большие таблицы с вычислениями
        table_blocks = []

        if 'analogs' in active_tasks:
            walsh_rows = get_latex_walsh_table(v.bool_func)
            walsh_steps = []
            walsh_hadamard_values = v.bool_func.walsh_hadamard_transform()
            for u_idx in range(16):
                u_str = f'{u_idx:04b}'
                matches = 0
                mismatches = 0
                for idx, val in enumerate(tt_rev):
                    u_dot_x = ((u_idx >> 3) & 1) & ((idx >> 3) & 1) ^ \
                              ((u_idx >> 2) & 1) & ((idx >> 2) & 1) ^ \
                              ((u_idx >> 1) & 1) & ((idx >> 1) & 1) ^ \
                              (u_idx & 1) & (idx & 1)
                    if val == u_dot_x:
                        matches += 1
                    else:
                        mismatches += 1
                w_val = walsh_hadamard_values[u_idx]
                walsh_steps.append(f'$W_f({u_str}) = {matches} - {mismatches} = {w_val}$')
            
            walsh_text = ' \\\\\n                '.join(walsh_steps)
            walsh_block = (
                "\\noindent\n"
                "\\begin{minipage}[t]{0.46\\linewidth}\n"
                "    \\begin{minipage}[t]{0.32\\linewidth}\n"
                "        \\vspace{0pt}\n"
                "        \\footnotesize\n"
                "        \\begin{tabular}{|c|c|} \\hline\n"
                "        $u$ & $W_f(u)$ \\\\ \\hline\n"
                f"        {walsh_rows}\n"
                "        \\hline \\end{tabular}\n"
                "    \\end{minipage}%\n"
                "    \\hfill\n"
                "    \\begin{minipage}[t]{0.66\\linewidth}\n"
                "        \\vspace{0pt}\n"
                "        \\scriptsize\n"
                f"        {walsh_text}\n"
                "    \\end{minipage}\n"
                "\\end{minipage}\n"
            )
            table_blocks.append(walsh_block)

        if 'anf' in active_tasks:
            mobius_rows_list = []
            mobius_steps = []
            
            for g_idx in range(16):
                g_vector = f'{g_idx:04b}'
                subset_terms = []
                calculated_coeff = 0
                
                for idx in range(16):
                    if (idx & g_idx) == idx:
                        val = int(tt_rev[idx])
                        subset_terms.append(f'f({idx:04b})')
                        calculated_coeff ^= val
                
                term_str = ' \\oplus '.join(subset_terms)
                
                mobius_rows_list.append(f'\\texttt{{{g_vector}}} & {calculated_coeff} \\\\')
                mobius_steps.append(f'$c_{{{g_vector}}} = {term_str} = {calculated_coeff}$')

            mobius_rows = '\n'.join(mobius_rows_list)
            mobius_text = ' \\\\\n'.join(mobius_steps)
            
            mobius_block = (
                "\\noindent\n"
                "\\begin{minipage}[t]{0.25\\linewidth}\n"
                "    \\vspace{0pt}\n"
                "    \\footnotesize\n"
                "    \\centering\n"
                "    \\begin{tabular}[t]{|c|c|} \\hline\n"
                "    \\multicolumn{2}{|c|}{Преобр. Мёбиуса} \\\\ \\hline\n"
                "    $g$ & $c_g$ \\\\ \\hline\n"
                f"    {mobius_rows}\n"
                "    \\hline \\end{tabular}\n"
                "\\end{minipage}%\n"
                "\\hfill\n"
                "\\begin{minipage}[t]{0.72\\linewidth}\n"
                "    \\vspace{0pt}\n"
                "    \\raggedright\n"
                "    \\scriptsize\n"
                f"    {mobius_text}\n"
                "\\end{minipage}\n"
            )
            table_blocks.append(mobius_block)
            
        # Собираем таблицы рядом
        tables_latex = '\n\n\\vspace{5mm}\n\n'.join(table_blocks)
        
        block_content = f"""
        \\textbf{{\\fbox{{{i}}}}} \\texttt{{{v.tt_str[::-1]}}} \\\\[1mm]
        {ans_header_latex} \\\\[2mm]
        {tables_latex}
        \\vfill
        """
        
        # Оборачиваем в minipage шириной в текст, чтобы прижать всё к левому краю
        ans_block = f"""
        \\noindent
        \\begin{{minipage}}[t]{{\\textwidth}}
        {block_content.strip()}
        \\end{{minipage}}
        """
        
        if i % 2 == 0 and i < len(variants):
            ans_block += r'\newpage'

        answers.append(ans_block)            

    return header + tasks + '\n' + answers_header + '\n'.join(answers) + r'\end{document}'

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
