# tests/test_registry.py

import pytest

from validation import CheckDefinition, Severity, ValidationRegistry


def dummy_check(context, runtime_context):
    return []


def definition(check_id="USD_TEST", phase="open"):
    return CheckDefinition(
        check_id=check_id,
        label="Test",
        func=dummy_check,
        target_type=object,
        category="Tests",
        phase=phase,
        default_severity=Severity.ERROR
    )


def test_registry_rejects_duplicate_ids():
    registry = ValidationRegistry()
    registry.register(definition())
    with pytest.raises(ValueError, match="Duplicate check ID"):
        registry.register(definition())


def test_registry_sorts_by_execution_phase():
    registry = ValidationRegistry()
    registry.register(definition("USD_GEOMETRY", "geometry"))
    registry.register(definition("USD_OPEN", "open"))
    assert [item.check_id for item in registry.resolve()] == ["USD_OPEN", "USD_GEOMETRY"]
