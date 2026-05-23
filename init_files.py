# -*- coding: utf-8 -*-
"""Load some files with functions."""
import sys
from pathlib import Path

from sage.misc.persist import load


if 'INIT_FILES_LOADED' not in globals():
    globals()['INIT_FILES_LOADED'] = True

    current_path = Path(__file__).resolve().parent
    last_folder = current_path.name

    if last_folder in ['src', 'archive', 'tests']:
        project_root = current_path.parent
    else:
        project_root = current_path

    sys.path.append(str(project_root / 'src'))

    load(str(project_root / 'src/some_checks.py'))
    load(str(project_root / 'src/decorators.py'))
