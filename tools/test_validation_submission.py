import argparse

from s_usd_core.validation import PublishReport
from s_usd_desktop.client import SUsdvApiClient, ValidationClient
from s_usd_desktop.validation import build_validation_run_payload


parser = argparse.ArgumentParser()
parser.add_argument("version_id")
parser.add_argument("report_path")
parser.add_argument("--stored-file-id")
arguments = parser.parse_args()

report = PublishReport.read_json(arguments.report_path)
payload = build_validation_run_payload(
    report,
    stored_file_id=arguments.stored_file_id
)

with SUsdvApiClient() as api:
    validation = ValidationClient(api)
    created = validation.create_run(arguments.version_id, payload)

print(f"Validation run: {created.id}")
print(f"Version: {created.version_id}")
print(f"Profile: {created.profile_name}")
print(f"Passed: {created.publish_passed}")
print(f"Results: {created.total_count}")
print(f"Report stored: {created.report is not None}")