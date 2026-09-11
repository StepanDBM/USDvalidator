# validation/publish_report.py

import json
from dataclasses import dataclass, field
from pathlib import Path

from contexts import StageHealthContext

from .models import CheckResult, ValidationSummary


REPORT_SCHEMA_VERSION = "1.0"


@dataclass
class PublishReport:
    source_path: str
    stage_opened: bool
    root_layer: str
    stage_health: StageHealthContext | None = None
    results: list[CheckResult] = field(default_factory=list)

    @property
    def summary(self):
        return ValidationSummary.from_results(self.results)

    @property
    def publish_passed(self):
        return self.stage_opened and self.summary.errors == 0

    def to_dict(self):
        return {
            "schema_version": REPORT_SCHEMA_VERSION,
            "source": {
                "path": PublishReport._serialize_path(self.source_path),
                "stage_opened": self.stage_opened,
                "root_layer": PublishReport._serialize_path(self.root_layer),
            },
            "stage_health": (
                self._serialize_stage_health(self.stage_health)
                if self.stage_health is not None
                else None
            ),
            "summary": self._serialize_summary(self.summary),
            "results": [
                self._serialize_result(result)
                for result in self.results
            ],
        }

    def to_json(self, *, indent=2):
        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=False,
        )

    def write_json(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            self.to_json(),
            encoding="utf-8",
        )

    @staticmethod
    def _serialize_result(result):
        return {
            "check_id": result.check_id,
            "label": result.label,
            "category": result.category,
            "status": result.status.value,
            "severity": result.severity.value,
            "message": result.message,
            "location": PublishReport._serialize_path(result.location),
            "layer": PublishReport._serialize_path(result.layer),
            "suggestion": result.suggestion,
            "details": result.details,
            "check_version": result.check_version,
        }

    @staticmethod
    def _serialize_path(path):
        return str(path).replace("\\", "/")

    @staticmethod
    def _serialize_summary(summary):
        return {
            "total": summary.total,
            "passed": summary.passed,
            "failed": summary.failed,
            "skipped": summary.skipped,
            "internal_errors": summary.internal_errors,
            "errors": summary.errors,
            "warnings": summary.warnings,
            "info": summary.info,
        }

    @staticmethod
    def _serialize_stage_health(health):
        return {
            "file": {
                "filename": health.file.filename,
                "extension": health.file.extension,
                "size_bytes": health.file.size_bytes,
                "modification_time": health.file.modification_time,
            },
            "stage": {
                "open_duration_seconds": health.stage.open_duration_seconds,
                "root_layer": health.stage.root_layer,
                "default_prim": health.stage.default_prim,
                "default_prim_valid": health.stage.default_prim_valid,
                "up_axis": health.stage.up_axis,
                "meters_per_unit": health.stage.meters_per_unit,
                "frames_per_second": health.stage.frames_per_second,
                "time_codes_per_second": health.stage.time_codes_per_second,
                "start_time_code": health.stage.start_time_code,
                "end_time_code": health.stage.end_time_code,
            },
            "scene": {
                "total_prims": health.scene.total_prims,
                "root_prims": health.scene.root_prims,
                "active_prims": health.scene.active_prims,
                "inactive_prims": health.scene.inactive_prims,
                "defined_prims": health.scene.defined_prims,
                "abstract_prims": health.scene.abstract_prims,
                "instance_prims": health.scene.instance_prims,
            },
            "types": {
                "meshes": health.types.meshes,
                "xforms": health.types.xforms,
                "cameras": health.types.cameras,
                "lights": health.types.lights,
                "materials": health.types.materials,
                "curves": health.types.curves,
                "point_instancers": health.types.point_instancers,
            },
            "composition": {
                "used_layers": health.composition.used_layers,
                "sublayers": health.composition.sublayers,
                "references": health.composition.references,
                "payloads": health.composition.payloads,
                "variant_sets": health.composition.variant_sets,
                "unresolved_references": health.composition.unresolved_references,
                "unresolved_payloads": health.composition.unresolved_payloads,
                "invalid_layers": health.composition.invalid_layers,
                "unexpected_arcs": health.composition.unexpected_arcs,
            },
            "geometry": {
                "mesh_count": health.geometry.mesh_count,
                "total_points": health.geometry.total_points,
                "total_faces": health.geometry.total_faces,
                "total_polygons": health.geometry.total_polygons,
                "polygon_count_limit": health.geometry.polygon_count_limit,
                "meshes": [
                    {
                        "path": mesh.path,
                        "points_count": mesh.points_count,
                        "face_count": mesh.face_count,
                        "polygon_count": mesh.polygon_count,
                        "points_valid": mesh.points_valid,
                        "face_vertex_counts_valid": mesh.face_vertex_counts_valid,
                        "topology_valid": mesh.topology_valid,
                    }
                    for mesh in health.geometry.meshes
                ],
            },
            "animation": {
                "invalid_time_samples": (
                    health.animation.invalid_time_samples
                ),
            },
        }
