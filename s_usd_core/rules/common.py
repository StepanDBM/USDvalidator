from s_usd_core.validation.enums import CheckStatus
from s_usd_core.validation.models import CheckResult, CheckTargetResult


def result(check_id, label, category, runtime_context, passed, message, location="", details=None, suggestion="", targets=()):
    return [CheckResult(
        check_id=check_id, label=label, category=category,
        status=CheckStatus.PASSED if passed else CheckStatus.FAILED,
        severity=runtime_context.default_severity, message=message, location=location,
        details=details or {}, suggestion=suggestion, targets=tuple(targets),
    )]


def target_results(evaluated, path, failed, property_name="", observed=None, expected=None, message=None):
    targets = []
    for item in evaluated:
        prim_path = str(path(item))
        property_path = _property_path(prim_path, property_name(item) if callable(property_name) else property_name)
        is_failed = bool(failed(item))
        targets.append(CheckTargetResult(
            prim_path=prim_path, property_path=property_path,
            status=CheckStatus.FAILED if is_failed else CheckStatus.PASSED,
            observed=_value(observed, item), expected=_value(expected, item),
            message=_value(message, item) or "",
        ))
    return tuple(targets)


def prim_target_results(evaluated, path, failed, **kwargs):
    return target_results(evaluated, path, failed, **kwargs)


def property_target_results(evaluated, path, property_name, failed, **kwargs):
    return target_results(evaluated, path, failed, property_name=property_name, **kwargs)


def _property_path(prim_path, name):
    name = str(name or "")
    return f"{prim_path}.{name}" if name else ""


def _value(value, item):
    return value(item) if callable(value) else value


def csv_values(value):
    return tuple(item.strip() for item in value.split(",") if item.strip())
