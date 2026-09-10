# validation/publish_report.py

from dataclasses import dataclass, field

from contexts import StageHealthContext

from .models import CheckResult, ValidationSummary


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