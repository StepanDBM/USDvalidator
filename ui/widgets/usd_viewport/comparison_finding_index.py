from collections import Counter, defaultdict
from dataclasses import dataclass, field

from pxr import Sdf


IMPACT_RANK = {"INFORMATIONAL": 1, "LOW": 2, "MEDIUM": 3, "HIGH": 4, "CRITICAL": 5}


@dataclass
class ComparisonSummary:
    direct_changes: list = field(default_factory=list)
    descendant_changes: list = field(default_factory=list)

    @property
    def all_changes(self):
        return self.direct_changes + self.descendant_changes

    @property
    def direct_count(self):
        return len(self.direct_changes)

    @property
    def descendant_count(self):
        return len(self.descendant_changes)

    @property
    def total_count(self):
        return len(self.all_changes)

    @property
    def impact_counts(self):
        return Counter(change.impact.value for change in self.all_changes)

    @property
    def kind_counts(self):
        return Counter(change.kind.value for change in self.all_changes)

    @property
    def highest_impact(self):
        return max((change.impact.value for change in self.all_changes), key=lambda value: IMPACT_RANK.get(value, 0), default="INFORMATIONAL")

    @property
    def tooltip(self):
        lines = [f"Semantic changes: {self.total_count}", f"Direct: {self.direct_count}", f"Descendants: {self.descendant_count}", f"Highest impact: {self.highest_impact}", ""]
        lines.extend(f"{name.title()}: {self.impact_counts.get(name, 0)}" for name in IMPACT_RANK)
        lines.append("")
        lines.extend(f"{name.title()}: {count}" for name, count in sorted(self.kind_counts.items()))
        return "\n".join(lines)


class ComparisonFindingIndex:
    def __init__(self, stage=None, changes=()):
        self.stage = stage
        self.changes = tuple(changes or ())
        self.direct_changes = defaultdict(list)
        self.stage_changes = []
        self._summaries = {}
        if stage:
            self._build()

    def summary(self, prim_path):
        prim_path = str(prim_path or "")
        if prim_path not in self._summaries:
            prefix = prim_path.rstrip("/") + "/"
            descendants = [change for path, changes in self.direct_changes.items() if path.startswith(prefix) for change in changes]
            self._summaries[prim_path] = ComparisonSummary(list(self.direct_changes.get(prim_path, ())), descendants)
        return self._summaries[prim_path]

    def _build(self):
        for change in self.changes:
            path = self._owning_prim_path(change.property_path or change.path)
            if path:
                self.direct_changes[path].append(change)
            else:
                self.stage_changes.append(change)

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
