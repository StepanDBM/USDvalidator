import httpx

from s_usd_desktop.client.configuration import ApiClientConfiguration
from s_usd_desktop.client.errors import (
    AuthenticationError,
    RequestTimeoutError,
    ResourceConflictError,
    ResourceNotFoundError,
    ServiceUnavailableError,
    UnexpectedServiceError,
    ValidationResponseError
)


class SUsdvApiClient:
    def __init__(self, configuration=None, transport=None):
        self.configuration = configuration or ApiClientConfiguration()
        self._client = httpx.Client(
            base_url=self.configuration.base_url,
            timeout=self.configuration.make_timeout(),
            transport=transport,
            headers={"Accept": "application/json"}
        )

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        self._client.close()

    def get(self, path, params=None):
        return self.request("GET", path, params=params)

    def post(self, path, json=None, data=None, files=None):
        return self.request("POST", path, json=json, data=data, files=files)

    def delete(self, path):
        return self.request("DELETE", path)

    def request(self, method, path, **kwargs):
        try:
            response = self._client.request(method, path, **kwargs)
        except httpx.TimeoutException as error:
            raise RequestTimeoutError(
                f"S-USDv Service request timed out: {method} {path}"
            ) from error
        except httpx.ConnectError as error:
            raise ServiceUnavailableError(
                f"Could not connect to S-USDv Service at {self.configuration.base_url}"
            ) from error
        except httpx.RequestError as error:
            raise ServiceUnavailableError(f"S-USDv Service request failed: {error}") from error

        if response.is_error:
            self._raise_service_error(response)

        if response.status_code == 204 or not response.content:
            return None

        try:
            return response.json()
        except ValueError as error:
            raise UnexpectedServiceError(
                "S-USDv Service returned malformed JSON",
                status_code=response.status_code
            ) from error

    @staticmethod
    def _raise_service_error(response):
        details = SUsdvApiClient._response_details(response)
        message = SUsdvApiClient._response_message(details, response.reason_phrase)
        error_type = {
            401: AuthenticationError,
            403: AuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceConflictError,
            422: ValidationResponseError
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
