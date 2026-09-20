import hashlib
import json
from dataclasses import asdict, is_dataclass


def canonical_data(value):
    if is_dataclass(value):
        return canonical_data(asdict(value))
    if isinstance(value, dict):
        return {key: canonical_data(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [canonical_data(item) for item in value]
    if hasattr(value, "value"):
        return value.value
    return value


def configuration_fingerprint(config):
    payload = json.dumps(
        canonical_data(config),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def check_catalog_fingerprint(definitions):
    payload = [
        {
            "check_id": item.check_id,
            "check_version": getattr(item, "check_version", "1"),
            "category": item.category,
            "phase": item.phase,
            "target_type": item.target_type.__name__,
        }
        for item in sorted(definitions, key=lambda value: value.check_id)
    ]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
