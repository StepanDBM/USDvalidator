import json
from dataclasses import dataclass
from pathlib import Path

from validation.version import (
    MANIFEST_SCHEMA_NAME,
    MANIFEST_SCHEMA_VERSION,
    TOOL_NAME,
    TOOL_VERSION,
)


@dataclass(frozen=True)
class PublishManifest:
    report: object
    report_path: str = ""

    def to_dict(self):
        report = self.report
        health = report.stage_health
        stage = health.stage if health else None
        scene = health.scene if health else None
        types = health.types if health else None
        composition = health.composition if health else None
        return {
            "schema": {
                "name": MANIFEST_SCHEMA_NAME,
                "version": MANIFEST_SCHEMA_VERSION,
            },
            "generator": {"name": TOOL_NAME, "version": TOOL_VERSION},
            "publish": {
                "created_utc": report.validation_timestamp_utc,
                "source_path": self._path(report.source_path),
                "root_layer": self._path(report.root_layer),
                "default_prim": stage.default_prim if stage else "",
                "profile": report.profile_name,
                "validation_passed": report.publish_passed,
                "report_path": self._path(self.report_path),
            },
            "stage": {
                "up_axis": stage.up_axis if stage else None,
                "meters_per_unit": stage.meters_per_unit if stage else None,
                "start_time_code": stage.start_time_code if stage else None,
                "end_time_code": stage.end_time_code if stage else None,
                "frames_per_second": stage.frames_per_second if stage else None,
            },
            "contents": {
                "total_prims": scene.total_prims if scene else 0,
                "meshes": types.meshes if types else 0,
                "materials": types.materials if types else 0,
                "cameras": types.cameras if types else 0,
                "lights": types.lights if types else 0,
            },
            "dependencies": {
                "used_layers": composition.used_layers if composition else 0,
                "sublayers": composition.sublayers if composition else 0,
                "references": composition.references if composition else 0,
                "payloads": composition.payloads if composition else 0,
                "unresolved_references": (
                    composition.unresolved_references if composition else 0
                ),
                "unresolved_payloads": (
                    composition.unresolved_payloads if composition else 0
                ),
            },
            "validation": {
                "report_schema_version": report.to_dict()["schema"]["version"],
                "configuration_fingerprint": report.configuration_fingerprint,
                "check_catalog_version": report.check_catalog_version,
                "check_catalog_fingerprint": report.check_catalog_fingerprint,
                "summary": report.to_dict()["summary"],
            },
        }

    def to_json(self, *, indent=2):
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def write_json(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")

    @staticmethod
    def _path(value):
        return str(value).replace("\\", "/") if value else ""
