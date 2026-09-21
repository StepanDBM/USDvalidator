import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from s_usd_desktop.services.version_download_service import VersionDownloadService


class Preferences:
    def to_api_configuration(self):
        return object()


class Connection:
    preferences = Preferences()


class Cache:
    pass


def test_root_only_filters_version_files(monkeypatch):
    service = VersionDownloadService(Connection(), Cache())
    captured = {}

    class Pool:
        def start(self, worker):
            captured["files"] = worker.files

    service.thread_pool = Pool()
    root = type("File", (), {"role": "root_layer"})()
    dependency = type("File", (), {"role": "dependency"})()
    service.download([root, dependency], object(), root_only=True)

    assert captured["files"] == (root,)
