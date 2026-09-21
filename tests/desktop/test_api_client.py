import httpx
import pytest

from s_usd_desktop.client.api_client import SUsdvApiClient
from s_usd_desktop.client.configuration import ApiClientConfiguration
from s_usd_desktop.client.errors import (
    RequestTimeoutError,
    ResourceConflictError,
    ResourceNotFoundError,
    ServiceUnavailableError,
    UnexpectedServiceError,
    ValidationResponseError
)


def make_client(handler):
    transport = httpx.MockTransport(handler)
    return SUsdvApiClient(ApiClientConfiguration(), transport=transport)


def test_normalizes_base_url():
    config = ApiClientConfiguration(base_url="http://127.0.0.1:8000/")
    assert config.base_url == "http://127.0.0.1:8000"


@pytest.mark.parametrize("url", ["", "127.0.0.1:8000", "ftp://example.com"])
def test_rejects_invalid_base_url(url):
    with pytest.raises(ValueError):
        ApiClientConfiguration(base_url=url)


def test_maps_not_found():
    with make_client(lambda _: httpx.Response(404, json={"detail": "Missing"})) as client:
        with pytest.raises(ResourceNotFoundError, match="Missing"):
            client.get("/api/v1/projects/unknown")


def test_maps_conflict():
    with make_client(lambda _: httpx.Response(409, json={"detail": "Duplicate"})) as client:
        with pytest.raises(ResourceConflictError, match="Duplicate"):
            client.post("/api/v1/projects", json={})


def test_maps_validation_details():
    detail = [{"loc": ["body", "name"], "msg": "Field required", "type": "missing"}]
    with make_client(lambda _: httpx.Response(422, json={"detail": detail})) as client:
        with pytest.raises(ValidationResponseError, match="Field required") as error:
            client.post("/api/v1/projects", json={})
        assert error.value.details == detail


def test_maps_connection_failure():
    def handler(request):
        raise httpx.ConnectError("Connection refused", request=request)

    with make_client(handler) as client:
        with pytest.raises(ServiceUnavailableError):
            client.get("/api/v1/health")


def test_maps_timeout():
    def handler(request):
        raise httpx.ReadTimeout("Timed out", request=request)

    with make_client(handler) as client:
        with pytest.raises(RequestTimeoutError):
            client.get("/api/v1/health")


def test_rejects_malformed_json():
    with make_client(lambda _: httpx.Response(200, text="not-json")) as client:
        with pytest.raises(UnexpectedServiceError, match="malformed JSON"):
            client.get("/api/v1/health")
