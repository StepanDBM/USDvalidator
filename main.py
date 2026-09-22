from pathlib import Path

from s_usd_desktop.runtime import bootstrap_openusd_runtime


PROJECT_ROOT = Path(__file__).resolve().parent
bootstrap_openusd_runtime(project_root=PROJECT_ROOT)

from s_usd_desktop.app import main


if __name__ == "__main__":
    raise SystemExit(main())
