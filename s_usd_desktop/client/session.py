from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock


@dataclass(frozen=True, slots=True)
class DesktopUser:
    id: str
    email: str
    display_name: str
    is_platform_admin: bool = False


@dataclass(frozen=True, slots=True)
class WorkspaceSummary:
    id: str
    code: str
    name: str
    description: str = ""
    status: str = "active"


@dataclass(slots=True)
class SessionCredentials:
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime
    user: DesktopUser

    @property
    def access_expired(self):
        return self.access_expires_at <= datetime.now(timezone.utc)


class SessionRegistry:
    _sessions = {}
    _locks = {}
    _persisters = {}
    _guard = RLock()

    @classmethod
    def get(cls, base_url):
        with cls._guard:
            return cls._sessions.get(base_url.rstrip("/"))

    @classmethod
    def set(cls, base_url, credentials):
        with cls._guard:
            key = base_url.rstrip("/")
            cls._sessions[key] = credentials
            persister = cls._persisters.get(key)
            if persister:
                persister(credentials)

    @classmethod
    def clear(cls, base_url):
        with cls._guard:
            cls._sessions.pop(base_url.rstrip("/"), None)

    @classmethod
    def set_persister(cls, base_url, persister):
        with cls._guard:
            cls._persisters[base_url.rstrip("/")] = persister

    @classmethod
    def lock(cls, base_url):
        key = base_url.rstrip("/")
        with cls._guard:
            return cls._locks.setdefault(key, RLock())
