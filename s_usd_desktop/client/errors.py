class SUsdvClientError(Exception):
    def __init__(self, message, status_code=None, details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class ServiceUnavailableError(SUsdvClientError):
    pass


class RequestTimeoutError(SUsdvClientError):
    pass


class AuthenticationError(SUsdvClientError):
    pass


class ResourceNotFoundError(SUsdvClientError):
    pass


class ResourceConflictError(SUsdvClientError):
    pass


class ValidationResponseError(SUsdvClientError):
    pass


class UnexpectedServiceError(SUsdvClientError):
    pass
