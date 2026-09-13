from validation import PublishChecker

from .models import ChangeKind, ComparisonResult, SemanticChange
from .snapshot import StageSnapshotBuilder
from .transform_comparator import TransformComparator


class SemanticComparisonEngine:
    def __init__(self, profile=None):
        self.profile = profile
        self.snapshot_builder = StageSnapshotBuilder()
        self.domain_comparators = (TransformComparator(),)

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
            result.changes.extend(comparator.compare(previous.transforms, current.transforms))
        self._compare_validation(result, previous_report, current_report)
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
    def _compatibility_warnings(result, previous, current):
        if previous.configuration_fingerprint != current.configuration_fingerprint:
            result.warnings.append("The effective validation configurations differ.")
        if previous.check_catalog_fingerprint != current.check_catalog_fingerprint:
            result.warnings.append("The validation check catalogs differ.")
