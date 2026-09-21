from hashlib import sha256
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest

from s_usd_desktop.cache import (
    CacheConfiguration,
    CacheEntryStatus,
    CacheLocation,
    CacheManager,
    ChecksumMismatchError,
    DownloadCancellationToken,
    DownloadCancelledError,
    SizeMismatchError,
    VerifiedDownloader
)
from s_usd_desktop.client import ApiClientConfiguration, FileClient, SUsdvApiClient


def stored_file(payload, expected_payload=None):
    expected_payload = payload if expected_payload is None else expected_payload
    return SimpleNamespace(
        id=uuid4(),
        version_id=uuid4(),
        relative_path="root/scene.usda",
        size_bytes=len(expected_payload),
        sha256=sha256(expected_payload).hexdigest()
    )


def make_downloader(tmp_path, payload, status=200, headers=None, chunk_size=4):
    def handler(_request):
        return httpx.Response(status, content=payload, headers=headers or {})

    api = SUsdvApiClient(
        ApiClientConfiguration(),
        transport=httpx.MockTransport(handler)
    )
    manager = CacheManager(CacheConfiguration(root=tmp_path))
    downloader = VerifiedDownloader(FileClient(api), manager, chunk_size=chunk_size)
    return api, manager, downloader


def location():
    return CacheLocation("ORB", "rover", "model", 1)


def test_download_verifies_and_records_file(tmp_path):
    payload = b"#usda 1.0\nabcdef"
    remote = stored_file(payload)
    api, manager, downloader = make_downloader(tmp_path, payload)
    progress = []

    with api:
        entry = downloader.download(remote, location(), progress=lambda sent, total: progress.append((sent, total)))

    assert entry.status == CacheEntryStatus.AVAILABLE
    assert entry.local_path.read_bytes() == payload
    assert entry.sha256 == sha256(payload).hexdigest()
    assert progress[-1] == (len(payload), len(payload))
    assert not entry.local_path.with_name("scene.usda.part").exists()
    assert manager.inspect("ORB", "rover", "model", 1, remote).status == CacheEntryStatus.AVAILABLE


def test_checksum_mismatch_removes_part_file(tmp_path):
    actual = b"different bytes"
    remote = stored_file(actual)
    remote.sha256 = sha256(b"x" * len(actual)).hexdigest()
    api, manager, downloader = make_downloader(tmp_path, actual)
    final_path = manager.inspect("ORB", "rover", "model", 1, remote).local_path

    with api, pytest.raises(ChecksumMismatchError):
        downloader.download(remote, location())

    assert not final_path.exists()
    assert not final_path.with_name("scene.usda.part").exists()


def test_size_mismatch_removes_part_file(tmp_path):
    payload = b"short"
    remote = stored_file(payload)
    remote.size_bytes += 1
    api, manager, downloader = make_downloader(tmp_path, payload)
    final_path = manager.inspect("ORB", "rover", "model", 1, remote).local_path

    with api, pytest.raises(SizeMismatchError):
        downloader.download(remote, location())

    assert not final_path.exists()
    assert not final_path.with_name("scene.usda.part").exists()


def test_cancellation_removes_part_and_preserves_existing_file(tmp_path):
    old = b"old verified copy"
    incoming = b"new replacement bytes"
    remote = stored_file(incoming)
    api, manager, downloader = make_downloader(tmp_path, incoming, chunk_size=4)
    final_path = manager.inspect("ORB", "rover", "model", 1, remote).local_path
    final_path.parent.mkdir(parents=True, exist_ok=True)
    final_path.write_bytes(old)
    token = DownloadCancellationToken()

    def cancel_after_first_chunk(sent, _total):
        if sent >= 4:
            token.cancel()

    with api, pytest.raises(DownloadCancelledError):
        downloader.download(remote, location(), progress=cancel_after_first_chunk, token=token)

    assert final_path.read_bytes() == old
    assert not final_path.with_name("scene.usda.part").exists()


def test_failed_update_preserves_existing_file(tmp_path):
    old = b"old verified copy"
    actual = b"corrupt replacement"
    remote = stored_file(actual)
    remote.sha256 = sha256(b"x" * len(actual)).hexdigest()
    api, manager, downloader = make_downloader(tmp_path, actual)
    final_path = manager.inspect("ORB", "rover", "model", 1, remote).local_path
    final_path.parent.mkdir(parents=True, exist_ok=True)
    final_path.write_bytes(old)

    with api, pytest.raises(ChecksumMismatchError):
        downloader.download(remote, location())

    assert final_path.read_bytes() == old
