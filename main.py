# USDvalidator main.py

import argparse

from validation import PublishChecker
from validation.profile_loader import ProfileLoader
from validation.profiles import DEFAULT_PROFILE


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


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Validate an OpenUSD file for publishing."
    )
    parser.add_argument(
        "source_path",
        help="Path to a .usd, .usda, .usdc, or .usdz file."
    )
    return parser.parse_args()

def main():
    args = parse_arguments()

    profile_loader = ProfileLoader("validation/profiles.json")
    profile = profile_loader.get_profile(DEFAULT_PROFILE)

    checker = PublishChecker(profile=profile)
    report = checker.check(args.source_path)

    print_report(report)


if __name__ == "__main__":
    main()