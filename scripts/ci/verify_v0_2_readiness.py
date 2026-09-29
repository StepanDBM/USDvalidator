import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_VERSION = "0.2.0"
REQUIRED_FILES = (
    "docs/v0_2_release_contract.md",
    "docs/v0_2_readiness_report.md",
    "docs/v0_2_threat_review.md",
    "docs/storage_providers.md",
    "docs/validation_jobs.md",
    "docs/project_administration.md",
    "migrations/versions/0008_add_project_administration.py",
    "tests/release/test_v0_2_migration_compatibility.py",
    "tests/release/test_v0_2_contracts.py",
)
REQUIRED_TEST_MODULES = (
    "tests/service/test_authentication.py",
    "tests/service/test_authorization.py",
    "tests/service/test_storage_provider_contract.py",
    "tests/service/test_validation_jobs.py",
    "tests/service/test_project_administration.py",
    "tests/desktop/test_desktop_authentication.py",
)


@dataclass(frozen=True, slots=True)
class Check:
    name: str
    passed: bool
    detail: str


def read_service_version():
    namespace = {}
    config_path = REPOSITORY_ROOT / "s_usd_service" / "config.py"
    exec(compile(config_path.read_text(encoding="utf-8"), str(config_path), "exec"), namespace)
    return namespace["ServiceSettings"]().service_version


def run_command(name, command):
    result = subprocess.run(command, cwd=REPOSITORY_ROOT, text=True, capture_output=True, check=False)
    detail = (result.stdout + result.stderr).strip()
    return Check(name, result.returncode == 0, detail[-4000:])


def static_checks():
    files = tuple(path for path in REQUIRED_FILES if not (REPOSITORY_ROOT / path).is_file())
    test_modules = tuple(path for path in REQUIRED_TEST_MODULES if not (REPOSITORY_ROOT / path).is_file())
    version = read_service_version()
    return [
        Check("release artifacts", not files, "complete" if not files else f"missing: {', '.join(files)}"),
        Check(
            "acceptance test modules",
            not test_modules,
            "complete" if not test_modules else f"missing: {', '.join(test_modules)}",
        ),
        Check("release version", version == EXPECTED_VERSION, f"configured={version}, expected={EXPECTED_VERSION}"),
    ]


def main():
    parser = argparse.ArgumentParser(description="Verify S-USDv v0.2 release readiness.")
    parser.add_argument("--full", action="store_true", help="Run quality, security, and complete test gates.")
    parser.add_argument("--json", type=Path, help="Write a machine-readable result outside source control.")
    args = parser.parse_args()

    checks = static_checks()
    checks.append(
        run_command(
            "release acceptance tests",
            [sys.executable, "-m", "pytest", "tests/release", "-q"],
        )
    )
    if args.full:
        checks.extend(
            [
                run_command(
                    "ruff lint",
                    [sys.executable, "-m", "ruff", "check", "s_usd_core", "s_usd_service", "s_usd_desktop"],
                ),
                run_command(
                    "ruff format",
                    [sys.executable, "-m", "ruff", "format", "--check", "s_usd_core", "s_usd_service", "s_usd_desktop"],
                ),
                run_command(
                    "bandit",
                    [
                        sys.executable,
                        "-m",
                        "bandit",
                        "-c",
                        "pyproject.toml",
                        "-r",
                        "s_usd_core",
                        "s_usd_service",
                        "s_usd_desktop",
                        "-ll",
                        "-ii",
                    ],
                ),
                run_command("dependency consistency", [sys.executable, "-m", "pip", "check"]),
                run_command("complete test suite", [sys.executable, "scripts/ci/run_tests.py", "tests", "-q"]),
            ]
        )

    for check in checks:
        print(f"[{'PASS' if check.passed else 'FAIL'}] {check.name}: {check.detail}")
    passed = all(check.passed for check in checks)
    payload = {
        "schema": "s-usdv.v0_2_readiness/1.0",
        "release": EXPECTED_VERSION,
        "passed": passed,
        "checks": [asdict(check) for check in checks],
    }
    if args.json:
        args.json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
