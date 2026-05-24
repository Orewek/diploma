# -*- coding: utf-8 -*-
"""module for crypto analyze and output the result."""
import multiprocessing
import time as tm

from sage.crypto.boolean_function import (
    BooleanFunction,
    random_boolean_function,
)

from src.main import (
    find_best_rho_and_theta,
    is_without_forbidden,
    sac,
)

def _format_result(
        sac_order: int | str,
        is_wf: bool | str,
        bool_func: 'BooleanFunction',
        rt_data: None | dict | str,
) -> str:
    """Format the compiled crypto properties of a bool func into a multiline string.

    Args:
    -----
        sac_order:
        is_wf:
        bool_func:
        rt_data:

    Returns:
    --------
        output text
    """
    hex_str: str = bool_func.truth_table(format='hex')
    
    lines = [""]
    if sac_order != "Skipped":
        lines.append(f"        SAC(l):                      {sac_order}")
    if is_wf != "Skipped":
        lines.append(f"        Without Forbidden:           {is_wf}")
    if rt_data != "Skipped":
        lines.append(f"        Rho and Theta:               {rt_data}")
        
    lines.append(f"        Function (Hex):              {hex_str}")
    lines.append("        ")
    
    return "\n".join(lines)


def search_worker(
        queue: multiprocessing.Queue,
        amount_of_variables: int,
        l_criteria_min: int | None,
        l_criteria_max: int | None,
        timeout: float,
        forbidden_filter: None | bool,
        rt_filter: str,
        params: dict,
) -> None:
    """Generate rand bool func & filter them by strict crypto properties until timeout.

    Args:
    -----
        queue: multiprocessing.Queue
        amount_of_variables: int
        l_criteria_min: int
        l_criteria_max: int
        timeout: float
        forbidden_filter: None/bool
        rt_filter: str
    """
    try:
        start_time: float = tm.time()

        while True:
            # if reach time limit -> stop calculation
            if tm.time() - start_time > float(timeout):
                return

            bool_func: 'BooleanFunction' = random_boolean_function(amount_of_variables)

            if params.get('use_sac', True):
                sac_order = sac(bool_func)
                if not l_criteria_min <= sac_order <= l_criteria_max:
                    continue
            else:
                sac_order = "Skipped"

            if params.get('use_forbidden', True):
                is_wf = is_without_forbidden(bool_func)
                if forbidden_filter is not None and is_wf != forbidden_filter:
                    continue
            else:
                is_wf = "Skipped"

            if params.get('use_rt', True):
                rt_result = find_best_rho_and_theta(bool_func)
                if rt_filter == 'Exist' and rt_result is None:
                    continue
                if rt_filter == 'Not' and rt_result is not None:
                    continue
            else:
                rt_result = "Skipped"

            queue.put({
                'text': _format_result(
                    sac_order,
                    is_wf,
                    bool_func,
                    rt_result,
                ),
            })
            return
    finally:
        return
