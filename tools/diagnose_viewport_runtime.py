import argparse
import json
import sys
from pathlib import Path

from s_usd_desktop.runtime import bootstrap_openusd_runtime, detect_runtime_capabilities


def main():
    parser = argparse.ArgumentParser(
        description="Inspect and bootstrap the OpenUSD viewport runtime."
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--no-bootstrap", action="store_true", help="Inspect the active environment only.")
    parser.add_argument("--runtime-root", help="Explicit complete OpenUSD runtime root.")
    arguments = parser.parse_args()
    bootstrap = None

    if not arguments.no_bootstrap:
        bootstrap = bootstrap_openusd_runtime(
            project_root=Path(__file__).resolve().parents[1],
            runtime_root=arguments.runtime_root
        )

    application = _ensure_gui_application()
    capabilities = detect_runtime_capabilities()

    if arguments.json:
        data = capabilities.to_dict()
        data["bootstrap"] = {
            "applied": bootstrap.applied if bootstrap else False,
            "root": str(bootstrap.layout.root) if bootstrap and bootstrap.layout else "",
            "message": bootstrap.message if bootstrap else "Bootstrap disabled"
        }
        print(json.dumps(data, indent=2))
    else:
        if bootstrap:
            print(bootstrap.message)
            print()
        print(capabilities.diagnostic_text())

    del application
    return 0 if capabilities.viewport_available else 1


def _ensure_gui_application():
    from PySide6.QtGui import QGuiApplication
    return QGuiApplication.instance() or QGuiApplication(sys.argv[:1])


if __name__ == "__main__":
    raise SystemExit(main())
