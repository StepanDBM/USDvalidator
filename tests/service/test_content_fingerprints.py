from types import SimpleNamespace

from s_usd_service.services.content_fingerprint import VersionContentFingerprint


def stored_file(role, path, size, sha256, status="available"):
    return SimpleNamespace(
        role=role,
        relative_path=path,
        size_bytes=size,
        sha256=sha256,
        status=status
    )


def test_fingerprint_is_order_independent_and_content_sensitive():
    root = stored_file("root_layer", "root/probe.usda", 20, "A" * 64)
    dependency = stored_file("dependency", "geo/body.usdc", 40, "B" * 64)

    first = VersionContentFingerprint.calculate([root, dependency])
    reordered = VersionContentFingerprint.calculate([dependency, root])
    changed = VersionContentFingerprint.calculate([
        root,
        stored_file("dependency", "geo/body.usdc", 40, "C" * 64)
    ])

    assert first == reordered
    assert first != changed
    assert len(first) == 64


def test_fingerprint_ignores_database_and_storage_identity():
    first = stored_file("root_layer", "root/probe.usda", 20, "A" * 64)
    first.id = "first"
    first.storage_key = "objects/first"
    second = stored_file("root_layer", "root/probe.usda", 20, "A" * 64)
    second.id = "second"
    second.storage_key = "objects/second"

    assert VersionContentFingerprint.calculate([first]) == VersionContentFingerprint.calculate([second])
