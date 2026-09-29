import keyring
from keyring.errors import KeyringError


class CredentialStoreError(RuntimeError):
    pass


class SecureCredentialStore:
    SERVICE = "S-USDv Desktop"

    def __init__(self, backend=None):
        self.backend = backend or keyring

    def save_refresh_token(self, base_url, refresh_token):
        try:
            self.backend.set_password(self.SERVICE, base_url.rstrip("/"), refresh_token)
        except KeyringError as error:
            raise CredentialStoreError("The operating-system credential store is unavailable.") from error

    def load_refresh_token(self, base_url):
        try:
            return self.backend.get_password(self.SERVICE, base_url.rstrip("/"))
        except KeyringError as error:
            raise CredentialStoreError("The operating-system credential store is unavailable.") from error

    def delete_refresh_token(self, base_url):
        try:
            self.backend.delete_password(self.SERVICE, base_url.rstrip("/"))
        except self.backend.errors.PasswordDeleteError:
            pass
        except KeyringError as error:
            raise CredentialStoreError("The operating-system credential store is unavailable.") from error


class MemoryCredentialStore:
    def __init__(self):
        self.values = {}

    def save_refresh_token(self, base_url, refresh_token):
        self.values[base_url.rstrip("/")] = refresh_token

    def load_refresh_token(self, base_url):
        return self.values.get(base_url.rstrip("/"))

    def delete_refresh_token(self, base_url):
        self.values.pop(base_url.rstrip("/"), None)
