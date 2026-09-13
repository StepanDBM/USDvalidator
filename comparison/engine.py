from dataclasses import replace

from validation import PublishChecker

from .advanced_comparators import (
    BlendShapeComparator,
    LightComparator,
    RenderProductComparator,
    RenderSettingsComparator,
    RenderVarComparator,
    SkeletonComparator,
    SkinningComparator,
    TimeConfigurationComparator,
    ValueClipComparator,
)
from .models import CorrelationConfidence, ChangeKind, ComparisonResult, SemanticChange
from .composition_comparators import (
    CollectionComparator,
    CompositionArcComparator,
    GeomSubsetComparator,
    PrimvarComparator,
    RelationshipComparator,
    SublayerComparator,
)
from .lookdev_comparators import MaterialBindingComparator, MaterialComparator, ShaderComparator
from .publish_domain_comparators import (
    CameraComparator,
    DependencyComparator,
    InstancingComparator,
    LayerComparator,
    SurfaceComparator,
)
from .snapshot import StageComparisonSnapshotBuilder
from .variant_comparator import VariantComparator
from .transform_comparator import TransformComparator


class SemanticComparisonEngine:
    def __init__(self, profile=None):
        self.profile = profile
        self.snapshot_builder = StageComparisonSnapshotBuilder()
        self.domain_comparators = (
            TransformComparator(),
            VariantComparator(),
            MaterialComparator(),
            ShaderComparator(),
            MaterialBindingComparator(),
            DependencyComparator(),
            LayerComparator(),
            SurfaceComparator(),
            CameraComparator(),
            InstancingComparator(),
            SublayerComparator(),
            CompositionArcComparator(),
            RelationshipComparator(),
            CollectionComparator(),
            GeomSubsetComparator(),
            PrimvarComparator(),
            LightComparator(),
            RenderSettingsComparator(),
            RenderProductComparator(),
            RenderVarComparator(),
            SkeletonComparator(),
            SkinningComparator(),
            BlendShapeComparator(),
            ValueClipComparator(),
            TimeConfigurationComparator(),
        )

    def compare(self, previous_path, current_path):
        previous = self.snapshot_builder.build(previous_path)
        current = self.snapshot_builder.build(current_path)
        previous_report = PublishChecker(profile=self.profile).check(previous_path)
        current_report = PublishChecker(profile=self.profile).check(current_path)
        result = ComparisonResult(previous.source_path, current.source_path)
        self._compare_mapping(result, "Metadata", "stage", previous.metadata, current.metadata)
        self._compare_prims(result, previous.prims, current.prims)
        self._compare_meshes(result, previous.meshes, current.meshes)
        self._compare_dependencies(result, previous.dependencies, current.dependencies)
        self._compare_animation(result, previous.animation, current.animation)
        for comparator in self.domain_comparators:
            result.changes.extend(comparator.compare(previous, current))
        self._compare_validation(result, previous_report, current_report)
        self._correlate_validation(result, previous_report, current_report)
        self._summarize_validation_by_domain(result)
        self._compatibility_warnings(result, previous_report, current_report)
        result.changes.sort(key=lambda item: (item.category, item.path, item.label))
        return result

    @staticmethod
    def _compare_mapping(result, category, root, previous, current):
        for key in sorted(set(previous) | set(current)):
            SemanticComparisonEngine._append_value(
                result, category, f"{root}.{key}", key.replace("_", " ").title(),
                previous.get(key), current.get(key),
            )

    @staticmethod
    def _compare_prims(result, previous, current):
        for path in sorted(set(previous) | set(current)):
            old = previous.get(path)
            new = current.get(path)

            if old is None:
                result.changes.append(SemanticChange(
                    "Hierarchy", path, f"Prim added ({new.type_name})",
                    ChangeKind.ADDED, None, new.type_name,
                ))
                continue
            if new is None:
                result.changes.append(SemanticChange(
                    "Hierarchy", path, f"Prim removed ({old.type_name})",
                    ChangeKind.REMOVED, old.type_name, None,
                ))
                continue

            for field, label in (
                ("type_name", "Prim type"),
                ("active", "Active state"),
                ("defined", "Defined state"),
                ("abstract", "Abstract state"),
                ("instance", "Instance state"),
                ("properties", "Property names"),
            ):
                SemanticComparisonEngine._append_value(
                    result, "Hierarchy", f"{path}.{field}", label,
                    getattr(old, field), getattr(new, field),
                )

    @staticmethod
    def _compare_meshes(result, previous, current):
        for path in sorted(set(previous) | set(current)):
            old = previous.get(path)
            new = current.get(path)

            if old is None or new is None:
                continue

            for field, label in (
                ("points_count", "Point count"),
                ("face_count", "Face count"),
                ("topology_hash", "Topology"),
                ("points_hash", "Point positions"),
                ("extent", "Extent"),
                ("subdivision_scheme", "Subdivision scheme"),
                ("orientation", "Orientation"),
            ):
                SemanticComparisonEngine._append_value(
                    result, "Geometry", f"{path}.{field}", label,
                    getattr(old, field), getattr(new, field),
                )

    @staticmethod
    def _compare_dependencies(result, previous, current):
        old = {(item.prim_path, item.arc_type, item.asset_path, item.prim_path_in_asset): item for item in previous}
        new = {(item.prim_path, item.arc_type, item.asset_path, item.prim_path_in_asset): item for item in current}

        for key in sorted(set(old) | set(new)):
            item = old.get(key) or new[key]
            path = f"{item.prim_path}.{item.arc_type}:{item.asset_path}"

            if key not in old:
                result.changes.append(SemanticChange(
                    "Composition", path, f"{item.arc_type.title()} added",
                    ChangeKind.ADDED, None, item.asset_path,
                ))
            elif key not in new:
                result.changes.append(SemanticChange(
                    "Composition", path, f"{item.arc_type.title()} removed",
                    ChangeKind.REMOVED, item.asset_path, None,
                ))
            else:
                SemanticComparisonEngine._append_value(
                    result, "Composition", f"{path}.resolved", "Resolution state",
                    old[key].resolved, new[key].resolved,
                )

    @staticmethod
    def _compare_animation(result, previous, current):
        for path in sorted(set(previous) | set(current)):
            old = previous.get(path)
            new = current.get(path)

            if old is None:
                result.changes.append(SemanticChange(
                    "Animation", path, "Animated attribute added",
                    ChangeKind.ADDED, None, new.sample_count,
                ))
                continue
            if new is None:
                result.changes.append(SemanticChange(
                    "Animation", path, "Animated attribute removed",
                    ChangeKind.REMOVED, old.sample_count, None,
                ))
                continue

            for field, label in (
                ("sample_count", "Sample count"),
                ("first_sample", "First sample"),
                ("last_sample", "Last sample"),
                ("sample_times_hash", "Sample times"),
                ("values_hash", "Sample values"),
            ):
                SemanticComparisonEngine._append_value(
                    result, "Animation", f"{path}.{field}", label,
                    getattr(old, field), getattr(new, field),
                )

    @staticmethod
    def _compare_validation(result, previous, current):
        old = {item.check_id: item for item in previous.results}
        new = {item.check_id: item for item in current.results}
        good = {"PASSED", "SKIPPED"}
        bad = {"FAILED", "ERROR"}

        for check_id in sorted(set(old) | set(new)):
            old_result = old.get(check_id)
            new_result = new.get(check_id)
            old_status = old_result.status.value if old_result else None
            new_status = new_result.status.value if new_result else None

            if old_status in good and new_status in bad:
                kind = ChangeKind.REGRESSION
            elif old_status in bad and new_status in good:
                kind = ChangeKind.RESOLVED
            elif old_result is None:
                kind = ChangeKind.ADDED
            elif new_result is None:
                kind = ChangeKind.REMOVED
            elif old_status == new_status:
                kind = ChangeKind.UNCHANGED
            else:
                kind = ChangeKind.CHANGED

            result.changes.append(SemanticChange(
                "Validation", check_id,
                new_result.label if new_result else old_result.label,
                kind, old_status, new_status,
                {
                    "previous_message": old_result.message if old_result else "",
                    "current_message": new_result.message if new_result else "",
                    "previous_version": old_result.check_version if old_result else None,
                    "current_version": new_result.check_version if new_result else None,
                },
            ))

    @staticmethod
    def _append_value(result, category, path, label, previous, current):
        if previous == current:
            kind = ChangeKind.UNCHANGED
        elif previous is None:
            kind = ChangeKind.ADDED
        elif current is None:
            kind = ChangeKind.REMOVED
        elif isinstance(previous, (int, float)) and isinstance(current, (int, float)):
            kind = ChangeKind.INCREASED if current > previous else ChangeKind.DECREASED
        else:
            kind = ChangeKind.CHANGED

        result.changes.append(SemanticChange(
            category, path, label, kind, previous, current,
        ))

    @staticmethod
    def _correlate_validation(result, previous, current):
        previous_results = _results_by_check_id(previous.results)
        current_results = _results_by_check_id(current.results)
        correlated = []
        for change in result.changes:
            correlations = []
            for check_id in change.related_check_ids:
                old_items = previous_results.get(check_id, ())
                new_items = current_results.get(check_id, ())
                count = max(len(old_items), len(new_items), 1)
                for index in range(count):
                    old = old_items[index] if index < len(old_items) else None
                    new = new_items[index] if index < len(new_items) else None
                    old_status = old.status.value if old else "NOT_RUN"
                    new_status = new.status.value if new else "NOT_RUN"
                    consequence = _consequence(old_status, new_status)
                    confidence = _correlation_confidence(change, old, new)
                    old_location = getattr(old, "location", "") if old else ""
                    new_location = getattr(new, "location", "") if new else ""

                    correlations.append({
                        "check_id": check_id,
                        "previous_status": old_status,
                        "current_status": new_status,
                        "previous_location": old_location,
                        "current_location": new_location,
                        "confidence": confidence.value,
                        "consequence": consequence,
                    })
            meaningful = [item for item in correlations if item["consequence"]]
            meaningful.sort(key=lambda item: _confidence_rank(item["confidence"]), reverse=True)
            consequence = "; ".join(
                f'{item["check_id"]} {item["consequence"]} ({item["confidence"]})'
                for item in meaningful
            )
            if correlations:
                correlated.append(replace(
                    change,
                    validation_consequence=consequence,
                    details={**change.details, "validation_correlation": correlations},
                ))
            else:
                correlated.append(change)
        result.changes[:] = correlated

    @staticmethod
    def _summarize_validation_by_domain(result):
        summary = {}
        for change in result.changes:
            if change.category == "Validation":
                continue
            domain = change.domain or change.category
            bucket = summary.setdefault(domain, {"regressions": 0, "resolutions": 0})
            for item in change.details.get("validation_correlation", ()):
                if item["consequence"] == "regressed":
                    bucket["regressions"] += 1
                elif item["consequence"] == "resolved":
                    bucket["resolutions"] += 1
        result.validation_summary_by_domain = {
            domain: counts for domain, counts in sorted(summary.items())
            if counts["regressions"] or counts["resolutions"]
        }

    @staticmethod
    def _compatibility_warnings(result, previous, current):
        if previous.configuration_fingerprint != current.configuration_fingerprint:
            result.warnings.append("The effective validation configurations differ.")
        if previous.check_catalog_fingerprint != current.check_catalog_fingerprint:
            result.warnings.append("The validation check catalogs differ.")


def _results_by_check_id(results):
    grouped = {}
    for item in results:
        grouped.setdefault(item.check_id, []).append(item)
    return grouped


def _consequence(previous, current):
    bad = {"FAILED", "ERROR"}
    if previous not in bad and current in bad:
        return "regressed"
    if previous in bad and current not in bad:
        return "resolved"
    return ""


def _correlation_confidence(change, previous, current):
    locations = [
        getattr(item, "location", "")
        for item in (previous, current)
        if item and getattr(item, "location", "")
    ]
    if not locations:
        return CorrelationConfidence.CHECK_ONLY
    subjects = [change.path, change.property_path, change.source_hint.split(" :: ")[0]]
    subjects = [_normalize_path(item) for item in subjects if item]
    locations = [_normalize_path(item) for item in locations]
    if any(location == subject for location in locations for subject in subjects):
        return CorrelationConfidence.EXACT
    if any(_paths_related(location, subject) for location in locations for subject in subjects):
        return CorrelationConfidence.RELATED_PATH
    return CorrelationConfidence.CHECK_ONLY


def _normalize_path(value):
    return str(value).strip().replace("\\", "/").rstrip("/")


def _paths_related(left, right):
    return left.startswith(right + "/") or right.startswith(left + "/") or left.startswith(right + ".") or right.startswith(left + ".")


def _confidence_rank(value):
    return {"NONE": 0, "CHECK_ONLY": 1, "RELATED_PATH": 2, "EXACT": 3}[value]
