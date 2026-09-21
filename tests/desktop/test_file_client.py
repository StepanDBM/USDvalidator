from pathlib import Path

import httpx

from s_usd_desktop.client import ApiClientConfiguration, FileClient, SUsdvApiClient

VERSION_ID = "44444444-4444-4444-8444-444444444444"
FILE_ID = "55555555-5555-4555-8555-555555555555"
DATE = "2026-09-21T10:00:00+00:00"


def file_response():
    return {
        "id": FILE_ID,
        "version_id": VERSION_ID,
        "role": "root_layer",
        "original_name": "rover.usda",
        "relative_path": "root/rover.usda",
        "storage_key": "projects/ORB/rover.usda",
        "content_type": "application/octet-stream",
        "size_bytes": 11,
        "sha256": "abc123",
        "status": "available",
        "created_at": DATE,
        "updated_at": DATE,
        "content_url": f"/api/v1/files/{FILE_ID}/content"
    }


def test_upload_builds_multipart_request(tmp_path):
    source_path = tmp_path / "rover.usda"
    source_path.write_bytes(b"#usda 1.0\n")
    captured = {}

    def handler(request):
        captured["content_type"] = request.headers["content-type"]
        captured["body"] = request.content
        return httpx.Response(201, json=file_response())

    with SUsdvApiClient(ApiClientConfiguration(), transport=httpx.MockTransport(handler)) as api:
        result = FileClient(api).upload_file(
            VERSION_ID,
            source_path,
            role="root_layer",
            relative_path="root/rover.usda"
        )

    assert captured["content_type"].startswith("multipart/form-data;")
    assert b'filename="rover.usda"' in captured["body"]
    assert b"root_layer" in captured["body"]
    assert b"root/rover.usda" in captured["body"]
    assert result.original_name == "rover.usda"


def test_list_files_parses_collection():
    def handler(_):
        return httpx.Response(200, json={"items": [file_response()], "count": 1})

    with SUsdvApiClient(transport=httpx.MockTransport(handler)) as api:
        collection = FileClient(api).list_files(VERSION_ID)

    assert collection.count == 1
    assert collection.items[0].role == "root_layer"
