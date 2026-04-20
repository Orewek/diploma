from pathlib import Path
import sys

if 'INIT_FILES_LOADED' not in globals():
    globals()['INIT_FILES_LOADED'] = True

    current_path = Path(__file__).resolve().parent
    last_folder = current_path.name

    if last_folder in ['src', 'archive']:
        project_root = current_path.parent
    else:
        project_root = current_path

    sys.path.append(str(project_root / 'src'))

    load(str(project_root / "src/some_checks.sage"))
    load(str(project_root / "src/main.sage"))
