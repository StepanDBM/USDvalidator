from contextlib import contextmanager

import httpx

from s_usd_desktop.client.configuration import ApiClientConfiguration
from s_usd_desktop.client.errors import (
    AuthenticationError,
    AuthorizationError,
    RequestTimeoutError,
    ResourceConflictError,
    ResourceNotFoundError,
    ServiceUnavailableError,
    UnexpectedServiceError,
    ValidationResponseError,
)
from s_usd_desktop.client.session import SessionRegistry


class SUsdvApiClient:
    def __init__(self, configuration=None, transport=None):
        self.configuration = configuration or ApiClientConfiguration()
        self._client = httpx.Client(
            base_url=self.configuration.base_url,
            timeout=self.configuration.make_timeout(),
            transport=transport,
            headers={"Accept": "application/json"},
        )

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        self._client.close()

    def get(self, path, params=None, authenticated=True):
        return self.request("GET", path, params=params, authenticated=authenticated)

    def post(self, path, json=None, data=None, files=None, authenticated=True):
        return self.request("POST", path, json=json, data=data, files=files, authenticated=authenticated)

    def delete(self, path):
        return self.request("DELETE", path)

    @contextmanager
    def stream(self, method, path, **kwargs):
        kwargs["headers"] = self._authorization_headers(kwargs.get("headers"))
        try:
            with self._client.stream(method, path, **kwargs) as response:
                if response.is_error:
                    response.read()
                    self._raise_service_error(response)
                yield response
        except httpx.TimeoutException as error:
            raise RequestTimeoutError(f"S-USDv Service request timed out: {method} {path}") from error
        except httpx.ConnectError as error:
            raise ServiceUnavailableError(
                f"Could not connect to S-USDv Service at {self.configuration.base_url}"
            ) from error
        except httpx.RequestError as error:
            raise ServiceUnavailableError(f"S-USDv Service request failed: {error}") from error

    def request(self, method, path, authenticated=True, **kwargs):
        if authenticated:
            kwargs["headers"] = self._authorization_headers(kwargs.get("headers"))
        try:
            response = self._client.request(method, path, **kwargs)
        except httpx.TimeoutException as error:
            raise RequestTimeoutError(f"S-USDv Service request timed out: {method} {path}") from error
        except httpx.ConnectError as error:
            raise ServiceUnavailableError(
                f"Could not connect to S-USDv Service at {self.configuration.base_url}"
            ) from error
        except httpx.RequestError as error:
            raise ServiceUnavailableError(f"S-USDv Service request failed: {error}") from error

        if response.status_code == 401 and authenticated and self._refresh_session():
            kwargs["headers"] = self._authorization_headers(kwargs.get("headers"))
            response = self._client.request(method, path, **kwargs)
        if response.is_error:
            self._raise_service_error(response)

        if response.status_code == 204 or not response.content:
            return None

        try:
            return response.json()
        except ValueError as error:
            raise UnexpectedServiceError(
                "S-USDv Service returned malformed JSON", status_code=response.status_code
            ) from error

    def _authorization_headers(self, headers=None):
        session = SessionRegistry.get(self.configuration.base_url)
        result = dict(headers or {})
        if session:
            result["Authorization"] = f"Bearer {session.access_token}"
        return result

    def _refresh_session(self):
        from s_usd_desktop.client.auth_client import AuthenticationClient

        with SessionRegistry.lock(self.configuration.base_url):
            session = SessionRegistry.get(self.configuration.base_url)
            if not session:
                return False
            try:
                refreshed = AuthenticationClient(self).refresh(session.refresh_token)
            except AuthenticationError:
                SessionRegistry.clear(self.configuration.base_url)
                return False
            SessionRegistry.set(self.configuration.base_url, refreshed)
            return True

    @staticmethod
    def _raise_service_error(response):
        details = SUsdvApiClient._response_details(response)
        message = SUsdvApiClient._response_message(details, response.reason_phrase)
        error_type = {
            401: AuthenticationError,
            403: AuthorizationError,
            404: ResourceNotFoundError,
            409: ResourceConflictError,
            422: ValidationResponseError,
        }.get(response.status_code, UnexpectedServiceError)
        raise error_type(message, status_code=response.status_code, details=details)

    @staticmethod
    def _response_details(response):
        try:
            return response.json().get("detail", response.json())
        except ValueError:
            return response.text or response.reason_phrase

    @staticmethod
    def _response_message(details, fallback):
        if isinstance(details, str):
            return details

        if isinstance(details, list):
            messages = [item.get("msg", str(item)) if isinstance(item, dict) else str(item) for item in details]
            return "; ".join(messages)

        return fallback
