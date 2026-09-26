import importlib
import os
from pathlib import Path
import platform
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

REQUIRED_MODULES = (
    "alembic",
    "fastapi",
    "httpx",
    "multipart",
    "pydantic_settings",
    "pytest",
    "PySide6",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "sqlalchemy",
    "uvicorn"
)

OPENUSD_CORE_MODULES = (
    "pxr.Sdf",
    "pxr.Usd",
    "pxr.UsdGeom",
    "pxr.UsdShade"
)

OPTIONAL_VIEWPORT_MODULES = (
    "pxr.UsdImagingGL",
    "pxr.Usdviewq"
)


def probe(name):
    try:
        module = importlib.import_module(name)
    except Exception as error:
        return False, f"{type(error).__name__}: {error}"

    version = getattr(module, "__version__", "")
    return True, str(version or "available")


def bootstrap_openusd():
    try:
        from s_usd_desktop.runtime.bootstrap import bootstrap_openusd_runtime

        result = bootstrap_openusd_runtime(strict=False)
    except Exception as error:
        print(
            "[FAILED] OpenUSD runtime bootstrap: "
            f"{type(error).__name__}: {error}"
        )
        return False

    status = "OK" if result.applied else "FAILED"
    print(f"[{status}] OpenUSD runtime bootstrap: {result.message}")
    return result.applied


def main():
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")
    print(f"Repository: {REPOSITORY_ROOT}")
    print(
        "QT_QPA_PLATFORM: "
        f"{os.environ.get('QT_QPA_PLATFORM', '<not set>')}"
    )
    print(
        "S_USDV_OPENUSD_ROOT: "
        f"{os.environ.get('S_USDV_OPENUSD_ROOT', '<not set>')}"
    )

    failures = []

    for name in REQUIRED_MODULES:
        available, detail = probe(name)
        print(f"[{'OK' if available else 'MISSING'}] {name}: {detail}")

        if not available:
            failures.append(name)

    if not bootstrap_openusd():
        failures.append("OpenUSD runtime bootstrap")

    for name in OPENUSD_CORE_MODULES:
        available, detail = probe(name)
        print(f"[{'OK' if available else 'MISSING'}] {name}: {detail}")

        if not available:
            failures.append(name)

    print("Optional embedded viewport modules:")

    for name in OPTIONAL_VIEWPORT_MODULES:
        available, detail = probe(name)
        status = "OK" if available else "OPTIONAL"
        print(f"[{status}] {name}: {detail}")

    if failures:
        print(
            "Environment check failed. Missing required components: "
            f"{', '.join(failures)}"
        )
        return 1

    print("Environment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())