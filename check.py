# -*- coding: utf-8 -*-
"""check module."""

from pathlib import Path

import operator
import itertools

from sage.misc.persist import load

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sage.rings.polynomial.pbori import BooleanPolynomial
    from sage.rings.polynomial.pbori.pbori import BooleanMonomial, BooleanPolynomialRing

from sage.crypto.boolean_function import BooleanFunction

from src.logger_config import main_log
from src.main import sac


def load_init():
    current_path: Path = Path(__file__).resolve().parent
    init_path = current_path.parent / 'init_files.py'

    if not init_path.exists():
        init_path = Path(__file__).resolve().parent / 'init_files.py'

    if init_path:
        load(str(init_path))

    else:
        print('Warning: init_files.py not found')


load_init()


from multiprocessing import Process, cpu_count

def check_range_worker(start_idx, end_idx, n, core_id):
    hex_len = (1 << n) // 4
    core_range_size = end_idx - start_idx
    for i in range(start_idx, end_idx):
        hex_str = f"{i:0{hex_len}x}"
        
        f = BooleanFunction(hex_str)
        res = sac(f)
        
        if res > 0:
            steps_done = i - start_idx
            core_percent = (steps_done / core_range_size) * 100
            print(
                f"[Core {core_id} Found] {hex_str} (SAC order: {res}) | Core Progress: {core_percent:.3f}%"
            )

if __name__ == "__main__":
    n = 4
    total_functions = 1 << (1 << n)
    num_cores = 6
    
    step = total_functions // num_cores
    processes = []
    
    print(f"Starting multi-processing search on {num_cores} cores...")
    print(f"Total functions to check: {total_functions}")
    
    for core_id in range(num_cores):
        start = core_id * step
        end = (core_id + 1) * step if core_id < num_cores - 1 else total_functions
        
        p = Process(target=check_range_worker, args=(start, end, n, core_id + 1))
        processes.append(p)
        p.start()
        print(f"Core {core_id + 1} started. Range: {start} -> {end}")
        
    for p in processes:
        p.join()
 