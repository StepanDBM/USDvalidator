from datetime import datetime

from s_usd_desktop.client.session import DesktopUser, SessionCredentials, WorkspaceSummary


def _datetime(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _credentials(data):
    user = data["user"]
    return SessionCredentials(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        access_expires_at=_datetime(data["access_expires_at"]),
        refresh_expires_at=_datetime(data["refresh_expires_at"]),
        user=DesktopUser(
            id=user["id"],
            email=user["email"],
            display_name=user["display_name"],
            is_platform_admin=user["is_platform_admin"],
        ),
    )


class AuthenticationClient:
    def __init__(self, api):
        self.api = api

    def login(self, email, password, client_name="S-USDv Desktop", client_fingerprint=""):
        return _credentials(
            self.api.post(
                "/api/v1/auth/login",
                json={
                    "email": email,
                    "password": password,
                    "client_name": client_name,
                    "client_fingerprint": client_fingerprint,
                },
                authenticated=False,
            )
        )

    def refresh(self, refresh_token):
        return _credentials(
            self.api.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token}, authenticated=False)
        )

    def logout(self, refresh_token):
        return self.api.post("/api/v1/auth/logout", json={"refresh_token": refresh_token}, authenticated=False)

    def list_workspaces(self):
        return tuple(
            WorkspaceSummary(
                id=item["id"],
                code=item["code"],
                name=item["name"],
                description=item.get("description", ""),
                status=item.get("status", "active"),
            )
            for item in self.api.get("/api/v1/workspaces")
        )

    def create_workspace(self, code, name, description=""):
        item = self.api.post(
            "/api/v1/workspaces",
            json={"code": code, "name": name, "description": description},
        )
        return WorkspaceSummary(
            id=item["id"],
            code=item["code"],
            name=item["name"],
            description=item.get("description", ""),
            status=item.get("status", "active"),
        )

    def list_members(self, workspace_id):
        return tuple(self.api.get(f"/api/v1/workspaces/{workspace_id}/members"))

    def add_member(self, workspace_id, email, role):
        return self.api.post(
            f"/api/v1/workspaces/{workspace_id}/members",
            json={"email": email, "role": role},
        )
