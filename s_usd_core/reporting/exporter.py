from dataclasses import dataclass
from pathlib import Path

from .manifest import PublishManifest


@dataclass(frozen=True)
class ExportOptions:
    output_directory: Path
    write_batch_report: bool = True
    write_per_file_reports: bool = False
    write_manifests: bool = True


def export_batch(batch, options):
    output = Path(options.output_directory)
    output.mkdir(parents=True, exist_ok=True)
    written = []

    if options.write_batch_report:
        path = output / "batch_report.json"
        batch.write_json(path)
        written.append(path)

    for report in batch.reports:
        stem = Path(report.source_path).stem
        report_path = output / f"{stem}.report.json"

        if options.write_per_file_reports:
            report.write_json(report_path)
            written.append(report_path)

        if options.write_manifests:
            manifest_path = output / f"{stem}.manifest.json"
            PublishManifest(
                report=report,
                report_path=str(report_path) if options.write_per_file_reports else "",
            ).write_json(manifest_path)
            written.append(manifest_path)

    return tuple(written)
