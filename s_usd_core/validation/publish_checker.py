from datetime import datetime, timezone
from time import perf_counter

from s_usd_core.contexts import StageContext, StageHealthContext
from s_usd_core.extraction import UsdInspectionSession
from s_usd_core.reporting.fingerprint import (
    check_catalog_fingerprint,
    configuration_fingerprint,
)
from s_usd_core.rules import build_registry

from .config_resolver import build_effective_config
from .publish_report import PublishReport
from .rule_config import ValidationRuleConfig
from .runner import execute_checks


class PublishChecker:
    def __init__(self, profile=None, rule_config=None):
        self.profile = profile
        self.rule_config = (
            rule_config if rule_config is not None else ValidationRuleConfig()
        )
        self.registry = build_registry()

    def check(self, source_path):
        started = perf_counter()
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        session = UsdInspectionSession(source_path)
        targets = session.extract()
        definitions = (
            self.registry.resolve()
            if self.profile is None
            else self.registry.resolve_profile(self.profile)
        )
        effective_config = build_effective_config(self.profile, self.rule_config)
        results = execute_checks(definitions, targets, effective_config)
        stage_context = next(
            target for target in targets if isinstance(target, StageContext)
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
            validation_timestamp_utc=timestamp,
            validation_duration_seconds=round(perf_counter() - started, 6),
            profile_name=self.profile.name if self.profile else "default",
            configuration_fingerprint=configuration_fingerprint(effective_config),
            check_catalog_fingerprint=check_catalog_fingerprint(definitions),
        )
