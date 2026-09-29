from enum import Enum

from PySide6.QtCore import QObject, Signal

from s_usd_desktop.client import AuthenticationClient, SUsdvApiClient
from s_usd_desktop.client.errors import AuthenticationError, SUsdvClientError
from s_usd_desktop.client.session import SessionRegistry
from s_usd_desktop.services.credential_store import SecureCredentialStore


class SessionState(Enum):
    SIGNED_OUT = "signed_out"
    AUTHENTICATING = "authenticating"
    AUTHENTICATED = "authenticated"
    EXPIRED = "expired"
    ERROR = "error"


class SessionService(QObject):
    state_changed = Signal(object)
    authenticated = Signal(object)
    signed_out = Signal()
    authentication_failed = Signal(str)
    workspaces_changed = Signal(object)
    workspace_changed = Signal(object)

    def __init__(self, connection_service, credential_store=None, parent=None):
        super().__init__(parent)
        self.connection_service = connection_service
        self.credential_store = credential_store or SecureCredentialStore()
        self.state = SessionState.SIGNED_OUT
        self.user = None
        self.workspaces = ()
        self.current_workspace = None
        self.last_error = ""
        SessionRegistry.set_persister(
            self.base_url, lambda credentials: self._persist_rotated_token(credentials.refresh_token)
        )

    @property
    def base_url(self):
        return self.connection_service.preferences.base_url.rstrip("/")

    @property
    def authenticated_session(self):
        return SessionRegistry.get(self.base_url)

    def sign_in(self, email, password, remember=True):
        self._set_state(SessionState.AUTHENTICATING)
        try:
            with SUsdvApiClient(self.connection_service.preferences.to_api_configuration()) as api:
                credentials = AuthenticationClient(api).login(email.strip(), password)
            self._accept_credentials(credentials, remember)
            self.load_workspaces()
            self.authenticated.emit(credentials.user)
            return True
        except SUsdvClientError as error:
            self.last_error = error.message
            self._set_state(SessionState.ERROR)
            self.authentication_failed.emit(error.message)
            return False

    def restore(self):
        refresh_token = self.credential_store.load_refresh_token(self.base_url)
        if not refresh_token:
            return False
        self._set_state(SessionState.AUTHENTICATING)
        try:
            with SUsdvApiClient(self.connection_service.preferences.to_api_configuration()) as api:
                credentials = AuthenticationClient(api).refresh(refresh_token)
            self._accept_credentials(credentials, remember=True)
            self.load_workspaces()
            self.authenticated.emit(credentials.user)
            return True
        except (AuthenticationError, SUsdvClientError):
            self.credential_store.delete_refresh_token(self.base_url)
            SessionRegistry.clear(self.base_url)
            self._set_state(SessionState.EXPIRED)
            self.authentication_failed.emit("The saved service session has expired. Sign in again.")
            return False

    def sign_out(self):
        session = self.authenticated_session
        try:
            if session:
                with SUsdvApiClient(self.connection_service.preferences.to_api_configuration()) as api:
                    AuthenticationClient(api).logout(session.refresh_token)
        except Exception:
            pass
        finally:
            self.credential_store.delete_refresh_token(self.base_url)
            SessionRegistry.clear(self.base_url)
            self.user = None
            self.workspaces = ()
            self.current_workspace = None
            self._set_state(SessionState.SIGNED_OUT)
            self.workspaces_changed.emit(())
            self.workspace_changed.emit(None)
            self.signed_out.emit()

    def load_workspaces(self, preferred_workspace_id=None):
        with SUsdvApiClient(self.connection_service.preferences.to_api_configuration()) as api:
            self.workspaces = AuthenticationClient(api).list_workspaces()
        current_ids = {workspace.id for workspace in self.workspaces}
        selected_id = preferred_workspace_id
        if selected_id is None and self.current_workspace and self.current_workspace.id in current_ids:
            selected_id = self.current_workspace.id
        if selected_id is None:
            stored_id = self.connection_service.settings.current_workspace_id()
            selected_id = stored_id if stored_id in current_ids else None
        self.select_workspace(selected_id or (self.workspaces[0].id if self.workspaces else None))
        self.workspaces_changed.emit(self.workspaces)
        return self.workspaces

    def create_workspace(self, code, name, description=""):
        with SUsdvApiClient(self.connection_service.preferences.to_api_configuration()) as api:
            workspace = AuthenticationClient(api).create_workspace(code, name, description)
        self.load_workspaces(preferred_workspace_id=workspace.id)
        return workspace

    def list_members(self, workspace_id):
        with SUsdvApiClient(self.connection_service.preferences.to_api_configuration()) as api:
            return AuthenticationClient(api).list_members(workspace_id)

    def add_member(self, workspace_id, email, role):
        with SUsdvApiClient(self.connection_service.preferences.to_api_configuration()) as api:
            return AuthenticationClient(api).add_member(workspace_id, email, role)

    def select_workspace(self, workspace_id):
        self.current_workspace = next(
            (workspace for workspace in self.workspaces if workspace.id == workspace_id), None
        )
        self.connection_service.settings.set_current_workspace_id(
            self.current_workspace.id if self.current_workspace else ""
        )
        self.workspace_changed.emit(self.current_workspace)

    def _persist_rotated_token(self, refresh_token):
        if self.credential_store.load_refresh_token(self.base_url):
            self.credential_store.save_refresh_token(self.base_url, refresh_token)

    def _accept_credentials(self, credentials, remember):
        SessionRegistry.set(self.base_url, credentials)
        self.user = credentials.user
        self.last_error = ""
        if remember:
            self.credential_store.save_refresh_token(self.base_url, credentials.refresh_token)
        else:
            self.credential_store.delete_refresh_token(self.base_url)
        self._set_state(SessionState.AUTHENTICATED)

    def _set_state(self, state):
        self.state = state
        self.state_changed.emit(state)
