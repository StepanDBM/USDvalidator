import importlib
import os
from pathlib import Path
import sys

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))


def prepend_environment_path(name, path):
    value = str(Path(path).resolve())
    existing = [item for item in os.environ.get(name, "").split(os.pathsep) if item]
    normalized = os.path.normcase(os.path.abspath(value))
    existing = [
        item for item in existing
        if os.path.normcase(os.path.abspath(item)) != normalized
    ]
    os.environ[name] = os.pathsep.join([value, *existing])


def prepare_openusd():
    try:
        importlib.import_module("pxr.Usd")
    except Exception:
        from s_usd_desktop.runtime.bootstrap import bootstrap_openusd_runtime
        result = bootstrap_openusd_runtime(strict=False)
        if not result.applied or result.layout is None:
            print(f"OpenUSD runtime bootstrap failed: {result.message}")
            return False

        print(f"OpenUSD runtime bootstrap passed: {result.message}")
        prepend_environment_path("PYTHONPATH", result.layout.python_root)
        print(f"OpenUSD Python root: {result.layout.python_root}")
    else:
        print("OpenUSD core available from the active Python environment")

    prepend_environment_path("PYTHONPATH", REPOSITORY_ROOT)
    os.environ.pop("S_USDV_OPENUSD_ROOT", None)
    print(f"S_USDV_OPENUSD_ROOT available to tests: {'S_USDV_OPENUSD_ROOT' in os.environ}")
    return True


def main():
    os.chdir(REPOSITORY_ROOT)
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    if not prepare_openusd():
        return 1

    arguments = sys.argv[1:] or ["tests", "-v"]
    return pytest.main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
