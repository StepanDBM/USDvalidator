from dataclasses import dataclass, field

from validation.attribute_override import AttributeOverride
from validation.profiles import ValidationProfile


@dataclass
class ProfileDraft:
    name: str
    description: str
    enabled_check_ids: set[str] = field(default_factory=set)
    disabled_check_ids: set[str] = field(default_factory=set)
    overrides: list[AttributeOverride] = field(default_factory=list)
    include_all_checks: bool = False

    @classmethod
    def from_profile(cls, profile):
        return cls(
            name=profile.name,
            description=profile.description,
            enabled_check_ids=set(profile.enabled_check_ids),
            disabled_check_ids=set(profile.disabled_check_ids),
            overrides=list(profile.overrides),
            include_all_checks=profile.include_all_checks,
        )

    def to_profile(self):
        return ValidationProfile(
            name=self.name.strip(),
            description=self.description.strip(),
            enabled_check_ids=frozenset(self.enabled_check_ids),
            disabled_check_ids=frozenset(self.disabled_check_ids),
            overrides=tuple(self.overrides),
            include_all_checks=self.include_all_checks,
        )

    def add_checks(self, check_ids):
        self.enabled_check_ids.update(check_ids)
        self.disabled_check_ids.difference_update(check_ids)

    def remove_checks(self, check_ids):
        self.enabled_check_ids.difference_update(check_ids)
        self.disabled_check_ids.difference_update(check_ids)

    def has_check(self, check_id):
        if self.include_all_checks:
            return check_id not in self.disabled_check_ids

        return check_id in self.enabled_check_ids

    def get_override(self, path):
        return next(
            (override for override in self.overrides if override.path == path),
            None,
        )

    def set_override(self, path, value, enabled=True):
        override = AttributeOverride(path=path, value=value, enabled=enabled)

        for index, existing in enumerate(self.overrides):
            if existing.path == path:
                self.overrides[index] = override
                return

        self.overrides.append(override)

    def remove_override(self, path):
        self.overrides = [
            override for override in self.overrides if override.path != path
        ]

    def set_override_enabled(self, path, enabled):
        override = self.get_override(path)

        if override is not None:
            self.set_override(path, override.value, enabled)
