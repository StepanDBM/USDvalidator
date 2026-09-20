from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field

from pxr import Sdf
from s_usd_core.validation.enums import CheckStatus, Severity


STATUS_RANK = {CheckStatus.ERROR: 4, CheckStatus.FAILED: 3, CheckStatus.SKIPPED: 1, CheckStatus.PASSED: 0}
SEVERITY_RANK = {Severity.ERROR: 3, Severity.WARNING: 2, Severity.INFO: 1}


@dataclass(frozen=True)
class FindingEvidence:
    result: object
    status: CheckStatus
    severity: Severity
    prim_path: str
    property_path: str = ""


@dataclass
class FindingSummary:
    direct_evidence: list[FindingEvidence] = field(default_factory=list)
    descendant_evidence: list[FindingEvidence] = field(default_factory=list)

    @property
    def all_evidence(self):
        return self.direct_evidence + self.descendant_evidence

    @property
    def direct_results(self):
        return _unique_results(item.result for item in self.direct_evidence)

    @property
    def descendant_results(self):
        return _unique_results(item.result for item in self.descendant_evidence)

    @property
    def all_results(self):
        return _unique_results(item.result for item in self.all_evidence)

    @property
    def direct(self):
        return self.direct_results

    @property
    def descendants(self):
        return self.descendant_results

    @property
    def direct_count(self):
        return len(self.direct_evidence)

    @property
    def descendant_count(self):
        return len(self.descendant_evidence)

    @property
    def total_count(self):
        return len(self.all_evidence)

    @property
    def status_counts(self):
        return Counter(item.status.value for item in self.all_evidence)

    @property
    def severity_counts(self):
        return Counter(item.severity.value for item in self.all_evidence if item.status in {CheckStatus.FAILED, CheckStatus.ERROR})

    @property
    def passed_count(self):
        return self.status_counts.get(CheckStatus.PASSED.value, 0)

    @property
    def failed_count(self):
        return self.status_counts.get(CheckStatus.FAILED.value, 0) + self.error_count

    @property
    def error_count(self):
        return self.status_counts.get(CheckStatus.ERROR.value, 0)

    @property
    def warning_count(self):
        return sum(item.status is CheckStatus.FAILED and item.severity is Severity.WARNING for item in self.all_evidence)

    @property
    def information_count(self):
        return sum(item.severity is Severity.INFO for item in self.all_evidence)

    @property
    def skipped_count(self):
        return self.status_counts.get(CheckStatus.SKIPPED.value, 0)

    @property
    def highest_status_rank(self):
        return max((STATUS_RANK.get(item.status, 0) for item in self.all_evidence), default=0)

    @property
    def highest_severity_rank(self):
        return max((SEVERITY_RANK.get(item.severity, 0) for item in self.all_evidence if item.status in {CheckStatus.FAILED, CheckStatus.ERROR}), default=0)

    @property
    def is_aggregate(self):
        return bool(self.descendant_evidence)

    @property
    def tooltip(self):
        if not self.total_count:
            return "No validation target outcomes affect this prim."
        status = self.status_counts
        return "\n".join([
            f"Total target outcomes: {self.total_count}",
            f"Direct: {self.direct_count}",
            f"Descendants: {self.descendant_count}",
            "",
            f"Passed: {self.passed_count}",
            f"Failed: {status.get('FAILED', 0)}",
            f"Errors: {self.error_count}",
            f"Warnings: {self.warning_count}",
            f"Information: {self.information_count}",
            f"Skipped: {self.skipped_count}",
        ])


class PrimFindingIndex:
    def __init__(self, stage=None, results=()):
        self.stage = stage
        self.results = tuple(results or ())
        self.direct_evidence = defaultdict(list)
        self.direct_results = defaultdict(list)
        self.stage_results = []
        self._summaries = {}
        self._build()

    def summary(self, prim_path):
        prim_path = str(prim_path or "")
        if prim_path not in self._summaries:
            direct = list(self.direct_evidence.get(prim_path, ()))
            prefix = prim_path.rstrip("/") + "/"
            descendants = [item for path, values in self.direct_evidence.items() if path.startswith(prefix) for item in values]
            self._summaries[prim_path] = FindingSummary(direct, descendants)
        return self._summaries[prim_path]

    def direct_for_prim(self, prim_path):
        return list(self.direct_results.get(str(prim_path), ()))

    def results_for_paths(self, prim_paths, include_descendants=False):
        results = []
        for prim_path in prim_paths:
            summary = self.summary(prim_path)
            results.extend(summary.all_results if include_descendants else summary.direct_results)
        return _unique_results(results)

    def _build(self):
        if not self.stage:
            return
        for result in self.results:
            explicit = tuple(getattr(result, "targets", ()) or ())
            evidence = self._explicit_evidence(result, explicit) if explicit else self._legacy_evidence(result)
            if not evidence:
                self.stage_results.append(result)
                continue
            for item in evidence:
                self.direct_evidence[item.prim_path].append(item)
                bucket = self.direct_results[item.prim_path]
                if result not in bucket:
                    bucket.append(result)

    def _explicit_evidence(self, result, targets):
        evidence = []
        for target in targets:
            candidate = target.property_path or target.prim_path
            prim_path = self._owning_prim_path(candidate)
            if prim_path:
                evidence.append(FindingEvidence(result, target.status, result.severity, prim_path, target.property_path))
        return evidence

    def _legacy_evidence(self, result):
        evidence = []
        seen = set()
        for candidate in self._result_candidates(result):
            prim_path = self._owning_prim_path(candidate)
            if prim_path and prim_path not in seen:
                seen.add(prim_path)
                evidence.append(FindingEvidence(result, result.status, result.severity, prim_path))
        return evidence

    def _result_candidates(self, result):
        if result.location:
            yield result.location
        details = result.details or {}
        priority_keys = ("property_path", "prim_path", "paths", "invalid_meshes", "primvars", "variant_sets", "instancers", "meshes", "shaders", "cameras", "lights", "materials", "prims", "affected_paths")
        for key in priority_keys:
            if key in details:
                yield from _flatten(details[key])
        for key, value in details.items():
            if key not in priority_keys:
                yield from _flatten(value)

    def _owning_prim_path(self, value):
        text = str(value or "").strip()
        if not text.startswith("/"):
            return ""
        try:
            path = Sdf.Path(text)
        except Exception:
            return ""
        if path.IsPropertyPath():
            path = path.GetPrimPath()
        if not path.IsPrimPath():
            return ""
        prim = self.stage.GetPrimAtPath(path)
        return path.pathString if prim and prim.IsValid() else ""


def _flatten(value):
    if isinstance(value, dict):
        for nested in value.values():
            yield from _flatten(nested)
    elif isinstance(value, (list, tuple, set)):
        for nested in value:
            yield from _flatten(nested)
    else:
        yield value


def _unique_results(results):
    unique = []
    for result in results:
        if result not in unique:
            unique.append(result)
    return unique
