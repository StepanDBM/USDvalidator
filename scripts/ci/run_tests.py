import os
from pathlib import Path
import sys

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))


def prepend_environment_path(name, path):
    value = str(Path(path).resolve())
    existing = [
        item
        for item in os.environ.get(name, "").split(os.pathsep)
        if item
    ]
    normalized = os.path.normcase(os.path.abspath(value))
    existing = [
        item
        for item in existing
        if os.path.normcase(os.path.abspath(item)) != normalized
    ]
    os.environ[name] = os.pathsep.join([value, *existing])


def bootstrap_openusd():
    from s_usd_desktop.runtime.bootstrap import bootstrap_openusd_runtime

    result = bootstrap_openusd_runtime(strict=False)

    if not result.applied or result.layout is None:
        print(f"OpenUSD runtime bootstrap failed: {result.message}")
        return None

    print(f"OpenUSD runtime bootstrap passed: {result.message}")
    return result.layout


def verify_child_environment(layout):
    print(f"OpenUSD Python root: {layout.python_root}")
    print(
        "PYTHONPATH contains OpenUSD: "
        f"{str(layout.python_root) in os.environ.get('PYTHONPATH', '')}"
    )
    print(
        "S_USDV_OPENUSD_ROOT available to tests: "
        f"{'S_USDV_OPENUSD_ROOT' in os.environ}"
    )


def main():
    os.chdir(REPOSITORY_ROOT)
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    layout = bootstrap_openusd()

    if layout is None:
        return 1

    # New Python subprocesses do not inherit this process's sys.path.
    # The tooltip tests start separate Python interpreters, so expose both
    # the repository and OpenUSD Python packages through PYTHONPATH.
    prepend_environment_path("PYTHONPATH", REPOSITORY_ROOT)
    prepend_environment_path("PYTHONPATH", layout.python_root)

    # The explicit path has completed its purpose. Removing it prevents the
    # runtime-discovery tests from preferring the real installation over the
    # temporary test installation.
    os.environ.pop("S_USDV_OPENUSD_ROOT", None)

    verify_child_environment(layout)

    arguments = sys.argv[1:] or [
        "tests/service",
        "tests/desktop",
        "-v"
    ]
    return pytest.main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())