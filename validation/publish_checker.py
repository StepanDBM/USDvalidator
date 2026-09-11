# validation/publish_checker.py

from contexts import StageContext, StageHealthContext
from extraction import UsdInspectionSession
from rules import build_registry

from .publish_report import PublishReport
from .runner import execute_checks


class PublishChecker:
    def __init__(self, registry=None, profile=None):
        self.registry = registry or build_registry()
        self.profile = profile

    def check(self, source_path):
        session = UsdInspectionSession(source_path)
        targets = session.extract()

        if self.profile is None:
            definitions = self.registry.resolve()
        else:
            definitions = self.registry.resolve_profile(self.profile)

        results = execute_checks(definitions, targets)
        stage_context = next(
            target
            for target in targets
            if isinstance(target, StageContext)
        )

        stage_health = next(
            (
                target
                for target in targets
                if isinstance(target, StageHealthContext)
            ),
            None,
        )

        return PublishReport(
            source_path=stage_context.source_path,
            stage_opened=stage_context.opened,
            root_layer=stage_context.root_layer,
            stage_health=stage_health,
            results=results,
        )