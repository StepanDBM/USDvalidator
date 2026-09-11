import argparse
from pathlib import Path

from validation import PublishChecker
from validation.batch_validator import BatchValidator
from validation.profile_loader import ProfileLoader
from validation.profiles import DEFAULT_PROFILE


USD_EXTENSIONS = {".usd", ".usda", ".usdc", ".usdz"}


def print_report(report):
    summary = report.summary
    status = "PASSED" if report.publish_passed else "FAILED"

    print()
    print("USDvalidator Publish Check")
    print("=" * 60)
    print(f"Status: {status}")
    print(f"Source: {report.source_path}")
    print(f"Stage opened: {report.stage_opened}")
    print(f"Root layer: {report.root_layer or 'Unavailable'}")
    print()
    print("Results")
    print("-" * 60)

    for result in report.results:
        print(f"[{result.status.value}] {result.check_id}")
        print(f"  Severity: {result.severity.value}")
        print(f"  Message: {result.message}")

        if result.location:
            print(f"  Location: {result.location}")

        if result.layer:
            print(f"  Layer: {result.layer}")

        if result.suggestion:
            print(f"  Suggestion: {result.suggestion}")

        print()

    print("Summary")
    print("-" * 60)
    print(f"Checks: {summary.total}")
    print(f"Passed: {summary.passed}")
    print(f"Failed: {summary.failed}")
    print(f"Skipped: {summary.skipped}")
    print(f"Internal errors: {summary.internal_errors}")
    print(f"Publish-blocking errors: {summary.errors}")
    print(f"Warnings: {summary.warnings}")


def print_batch_report(batch):
    print()
    print("USDvalidator Batch Validation")
    print("=" * 60)
    print(f"Files: {batch.total_files}")
    print(f"Passed: {batch.passed_files}")
    print(f"Failed: {batch.failed_files}")
    print()

    for report in batch.reports:
        status = "PASS" if report.publish_passed else "FAIL"
        print(f"[{status}] {report.source_path}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Validate OpenUSD files for publishing."
    )

    parser.add_argument(
        "source_path",
        nargs="?",
        help="Path to a .usd, .usda, .usdc, or .usdz file.",
    )

    parser.add_argument(
        "--batch",
        metavar="DIRECTORY",
        help="Validate all supported USD files in a directory.",
    )

    parser.add_argument(
        "--report",
        help="Write the validation report to a JSON file.",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    if bool(args.source_path) == bool(args.batch):
        raise SystemExit(
            "Provide either a source file or --batch DIRECTORY."
        )

    profile_loader = ProfileLoader("validation/profiles.json")
    profile = profile_loader.get_profile(DEFAULT_PROFILE)

    checker = PublishChecker(profile=profile)

    if args.batch:
        batch_dir = Path(args.batch)

        if not batch_dir.is_dir():
            raise SystemExit(
                f"Batch directory does not exist: {batch_dir}"
            )

        source_paths = sorted(
            path
            for path in batch_dir.iterdir()
            if path.is_file()
            and path.suffix.lower() in USD_EXTENSIONS
        )

        if not source_paths:
            raise SystemExit(
                f"No supported USD files found in: {batch_dir}"
            )

        batch = BatchValidator(checker=checker).validate(source_paths)

        if args.report:
            batch.write_json(args.report)

        print_batch_report(batch)
        return

    report = checker.check(args.source_path)

    if args.report:
        report.write_json(args.report)

    print_report(report)


if __name__ == "__main__":
    main()

"""
single file CLI PowerShell command:
python main.py tests/fixtures/valid_stage.usda --report report.json

Batch file CLI PowerShell command:
python main.py --batch tests/fixtures --report batch_report.json

Without a JSON report PowerShell command:
python main.py --batch tests/fixtures

--batch DIRECTORY means “validate the supported USD files directly inside this directory.”
"""