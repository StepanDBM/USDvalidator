from .models import CheckDefinition
from .phases import phase_order


class ValidationRegistry:
    def __init__(self):
        self._definitions = {}

    def register(self, definition: CheckDefinition):
        if definition.check_id in self._definitions:
            raise ValueError(
                f"Duplicate check ID: {definition.check_id}"
            )

        phase_order(definition.phase)
        self._definitions[definition.check_id] = definition

    def get(self, check_id):
        return self._definitions[check_id]

    def all(self):
        return tuple(self._definitions.values())

    def resolve_profile(self, profile):
        return self.resolve(
            enabled_ids=profile.enabled_check_ids,
            disabled_ids=profile.disabled_check_ids,
        )

    def resolve(self, enabled_ids=None, disabled_ids=None):
        enabled_ids = set(enabled_ids or ())
        disabled_ids = set(disabled_ids or ())
        definitions = []

        for definition in self._definitions.values():
            if (
                not definition.enabled
                or definition.check_id in disabled_ids
            ):
                continue

            if (
                enabled_ids
                and definition.check_id not in enabled_ids
            ):
                continue

            definitions.append(definition)

        return sorted(
            definitions,
            key=lambda item: (
                phase_order(item.phase),
                item.category,
                item.check_id,
            ),
        )

    def __len__(self):
        return len(self._definitions)