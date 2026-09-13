# validation/config_solver.py

from copy import deepcopy

from .rule_config import ValidationRuleConfig


def resolve_override_target(root, path):
    parts = path.split(".")

    if len(parts) < 2:
        raise ValueError(
            f"Override path must include a section and attribute: {path}"
        )

    target = root

    for part in parts[:-1]:
        if not hasattr(target, part):
            raise AttributeError(
                f"Unknown component '{part}' in override path '{path}'."
            )

        target = getattr(target, part)

    attribute_name = parts[-1]

    if not hasattr(target, attribute_name):
        raise AttributeError(
            f"Unknown attribute '{attribute_name}' "
            f"in override path '{path}'."
        )

    return target, attribute_name


def validate_override_value(current_value, value, path):
    expected_type = type(current_value)

    if expected_type is int and type(value) is not int:
        raise TypeError(f"Override '{path}' expects an integer.")

    if expected_type is float:
        if type(value) not in (int, float):
            raise TypeError(f"Override '{path}' expects a number.")

        return float(value)

    if expected_type is bool and type(value) is not bool:
        raise TypeError(f"Override '{path}' expects a boolean.")

    if expected_type not in (int, float, bool) and not isinstance(
        value,
        expected_type,
    ):
        raise TypeError(
            f"Override '{path}' expects {expected_type.__name__}."
        )

    return value


def apply_overrides(config, overrides):
    for override in overrides:
        if not override.enabled:
            continue

        target, attribute_name = resolve_override_target(
            config,
            override.path,
        )

        current_value = getattr(target, attribute_name)
        value = validate_override_value(
            current_value,
            override.value,
            override.path,
        )

        setattr(target, attribute_name, value)

    return config


def build_effective_config(profile=None, base_config=None):
    config = deepcopy(base_config if base_config is not None else ValidationRuleConfig())

    if profile is not None:
        apply_overrides(config, profile.overrides)

    return config