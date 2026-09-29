from datetime import datetime, timedelta, timezone

import httpx

from s_usd_desktop.client.api_client import SUsdvApiClient
from s_usd_desktop.client.configuration import ApiClientConfiguration
from s_usd_desktop.client.session import DesktopUser, SessionCredentials, SessionRegistry
from s_usd_desktop.services.credential_store import MemoryCredentialStore
from s_usd_desktop.services.session_service import SessionService, SessionState


class Settings:
    def __init__(self):
        self.workspace_id = ""

    def connection_preferences(self):
        from s_usd_desktop.services.desktop_settings import ConnectionPreferences

        return ConnectionPreferences(auto_connect=False)

    def current_workspace_id(self):
        return self.workspace_id

    def set_current_workspace_id(self, value):
        self.workspace_id = value


class Connection:
    def __init__(self):
        self.settings = Settings()

    @property
    def preferences(self):
        return self.settings.connection_preferences()


def credentials(access="access", refresh="refresh"):
    now = datetime.now(timezone.utc)
    return SessionCredentials(
        access,
        refresh,
        now + timedelta(minutes=15),
        now + timedelta(days=30),
        DesktopUser("user-id", "artist@example.com", "Artist"),
    )


def test_api_attaches_access_token():
    SessionRegistry.set("http://127.0.0.1:8000", credentials())

    def handler(request):
        assert request.headers["Authorization"] == "Bearer access"
        return httpx.Response(200, json={"ok": True})

    api = SUsdvApiClient(ApiClientConfiguration(), transport=httpx.MockTransport(handler))
    assert api.get("/protected") == {"ok": True}
    api.close()
    SessionRegistry.clear("http://127.0.0.1:8000")


def test_401_refreshes_and_retries_once():
    SessionRegistry.set("http://127.0.0.1:8000", credentials("expired", "old-refresh"))
    calls = []

    def handler(request):
        calls.append(request.url.path)
        if request.url.path == "/api/v1/auth/refresh":
            now = datetime.now(timezone.utc)
            return httpx.Response(
                200,
                json={
                    "access_token": "new-access",
                    "refresh_token": "new-refresh",
                    "token_type": "bearer",
                    "access_expires_at": (now + timedelta(minutes=15)).isoformat(),
                    "refresh_expires_at": (now + timedelta(days=30)).isoformat(),
                    "user": {
                        "id": "user-id",
                        "email": "artist@example.com",
                        "display_name": "Artist",
                        "is_active": True,
                        "is_platform_admin": False,
                        "created_at": now.isoformat(),
                        "updated_at": now.isoformat(),
                        "last_login_at": now.isoformat(),
                    },
                },
            )
        if request.headers.get("Authorization") == "Bearer new-access":
            return httpx.Response(200, json={"ok": True})
        return httpx.Response(401, json={"detail": "expired"})

    api = SUsdvApiClient(ApiClientConfiguration(), transport=httpx.MockTransport(handler))
    assert api.get("/protected") == {"ok": True}
    assert calls == ["/protected", "/api/v1/auth/refresh", "/protected"]
    api.close()
    SessionRegistry.clear("http://127.0.0.1:8000")


def test_sign_out_clears_local_session_even_when_server_is_unavailable(monkeypatch):
    store = MemoryCredentialStore()
    service = SessionService(Connection(), store)
    SessionRegistry.set(service.base_url, credentials())
    store.save_refresh_token(service.base_url, "refresh")

    monkeypatch.setattr(SUsdvApiClient, "post", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError()))
    try:
        service.sign_out()
    except RuntimeError:
        pass

    assert SessionRegistry.get(service.base_url) is None
    assert store.load_refresh_token(service.base_url) is None


def test_workspace_selection_is_persisted():
    from s_usd_desktop.client.session import WorkspaceSummary

    connection = Connection()
    service = SessionService(connection, MemoryCredentialStore())
    service.workspaces = (
        WorkspaceSummary("one", "ONE", "One"),
        WorkspaceSummary("two", "TWO", "Two"),
    )
    service.select_workspace("two")
    assert service.current_workspace.id == "two"
    assert connection.settings.workspace_id == "two"


def test_local_mode_starts_signed_out_without_service_session():
    SessionRegistry.clear("http://127.0.0.1:8000")
    service = SessionService(Connection(), MemoryCredentialStore())
    assert service.state is SessionState.SIGNED_OUT
    assert service.authenticated_session is None
