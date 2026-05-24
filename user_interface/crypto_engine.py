import os
import sys
import time
from sage.crypto.boolean_function import random_boolean_function
from sage.crypto.boolean_function import BooleanFunction

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.main import sac


def _format_result(sac_order, b):
    b_hex = b.truth_table(format='hex')
    return (
        f"SAC Order (l):               {sac_order}\n\n"
        f"Function Vector (Hex):\n\n{b_hex}"
    )

def analyze_boolean_function_stream(n_vars, l_min, l_max, timeout):
    start_time = time.time()
    
    if n_vars < 5:
        total_functions = 1 << (1 << n_vars)
        hex_len = (1 << n_vars) // 4
        for i in range(total_functions):
            if time.time() - start_time > float(timeout):
                raise TimeoutError(f"Searching took more than {timeout} seconds...")
            
            hex_str = f"{i:0{hex_len}x}"
            b = BooleanFunction(hex_str)
            sac_order = sac(b)
            if l_min <= sac_order <= l_max:
                # Используем помощника
                yield 0, _format_result(sac_order, b) 
                return
                
        raise ValueError("Full search completed. No function found.")

    else:
        while True:
            if time.time() - start_time > float(timeout):
                raise TimeoutError(f"Searching took more than {timeout} seconds...")
                
            b = random_boolean_function(n_vars)
            sac_order = sac(b)
            
            if l_min <= sac_order <= l_max:
                # Используем помощника
                yield 0, _format_result(sac_order, b)
                return