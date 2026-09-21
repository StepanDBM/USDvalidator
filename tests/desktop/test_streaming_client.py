import httpx

from s_usd_desktop.client import ApiClientConfiguration, FileClient, SUsdvApiClient


def test_stream_content_does_not_require_json():
    payload = b"binary-usd-content"
    transport = httpx.MockTransport(lambda _: httpx.Response(200, content=payload))

    with SUsdvApiClient(ApiClientConfiguration(), transport=transport) as api:
        with FileClient(api).stream_content("file-id") as response:
            assert b"".join(response.iter_bytes()) == payload
