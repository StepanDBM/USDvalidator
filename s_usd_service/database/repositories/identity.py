from __future__ import annotations

import hmac
from datetime import timedelta, timezone
from secrets import token_urlsafe
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from s_usd_service.database.models.refresh_session import RefreshSession
from s_usd_service.database.models.user import User
from s_usd_service.database.repositories.errors import ConflictError, NotFoundError
from s_usd_service.security.passwords import hash_password, verify_password
from s_usd_service.security.tokens import (
    InvalidRefreshToken,
    create_refresh_token,
    hash_refresh_token,
    parse_refresh_session_id,
    utc_now,
)


def normalize_email(email: str) -> str:
    return email.strip().casefold()


_DUMMY_PASSWORD_HASH = hash_password(token_urlsafe(48))


class IdentityRepository:
    def __init__(self, database: Session):
        self.database = database

    def create_user(self, email: str, display_name: str, password: str) -> User:
        normalized_email = normalize_email(email)
        if self.database.scalar(select(User.id).where(User.normalized_email == normalized_email)):
            raise ConflictError("An account with this email already exists.")
        user = User(
            email=email.strip(),
            normalized_email=normalized_email,
            display_name=display_name.strip(),
            password_hash=hash_password(password),
        )
        self.database.add(user)
        self.database.commit()
        self.database.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> User | None:
        user = self.database.scalar(select(User).where(User.normalized_email == normalize_email(email)))
        password_hash = user.password_hash if user else _DUMMY_PASSWORD_HASH
        if not verify_password(password, password_hash) or not user:
            return None
        return user if user.is_active else None

    def get_user(self, user_id: UUID) -> User:
        user = self.database.get(User, user_id)
        if not user:
            raise NotFoundError("User not found.")
        return user

    def _build_refresh_session(
        self,
        user: User,
        lifetime_days: int,
        client_name: str = "",
        client_fingerprint: str = "",
        family_id: UUID | None = None,
    ) -> tuple[RefreshSession, str]:
        session = RefreshSession(
            user=user,
            family_id=family_id or UUID(int=0),
            token_hash=hash_refresh_token(token_urlsafe(48)),
            expires_at=utc_now() + timedelta(days=lifetime_days),
            client_name=client_name.strip(),
            client_fingerprint=client_fingerprint.strip(),
        )
        self.database.add(session)
        self.database.flush()
        if family_id is None:
            session.family_id = session.id
        token, session.token_hash = create_refresh_token(session.id)
        return session, token

    def create_refresh_session(
        self,
        user: User,
        lifetime_days: int,
        client_name: str = "",
        client_fingerprint: str = "",
        maximum_active_sessions: int = 10,
    ) -> tuple[RefreshSession, str]:
        now = utc_now()
        active_sessions = self.database.scalars(
            select(RefreshSession)
            .where(
                RefreshSession.user_id == user.id,
                RefreshSession.revoked_at.is_(None),
                RefreshSession.expires_at > now,
            )
            .order_by(RefreshSession.created_at.asc())
        ).all()
        overflow = max(0, len(active_sessions) - maximum_active_sessions + 1)
        for old_session in active_sessions[:overflow]:
            old_session.revoked_at = now

        session, token = self._build_refresh_session(user, lifetime_days, client_name, client_fingerprint)
        self.database.commit()
        self.database.refresh(session)
        return session, token

    def rotate_refresh_session(self, token: str, lifetime_days: int) -> tuple[RefreshSession, User, str]:
        session_id = parse_refresh_session_id(token)
        session = self.database.get(RefreshSession, session_id)
        if not session:
            raise InvalidRefreshToken("Invalid refresh token.")
        now = utc_now()
        if session.revoked_at is not None:
            if session.replaced_by_id is not None:
                self.revoke_family(session.family_id, now)
            raise InvalidRefreshToken("Refresh session is no longer active.")
        expires_at = session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at <= now or not hmac.compare_digest(session.token_hash, hash_refresh_token(token)):
            raise InvalidRefreshToken("Invalid or expired refresh token.")
        if not session.user.is_active:
            self.revoke_family(session.family_id, now)
            raise InvalidRefreshToken("Refresh session is no longer active.")

        replacement, replacement_token = self._build_refresh_session(
            session.user,
            lifetime_days,
            session.client_name,
            session.client_fingerprint,
            session.family_id,
        )
        session.last_used_at = now
        session.revoked_at = now
        session.replaced_by_id = replacement.id
        self.database.commit()
        return replacement, session.user, replacement_token

    def revoke_session(self, token: str) -> None:
        session_id = parse_refresh_session_id(token)
        session = self.database.get(RefreshSession, session_id)
        if not session or not hmac.compare_digest(session.token_hash, hash_refresh_token(token)):
            return
        if session.revoked_at is None:
            session.revoked_at = utc_now()
            self.database.commit()

    def revoke_family(self, family_id: UUID, revoked_at=None) -> None:
        self.database.execute(
            update(RefreshSession)
            .where(RefreshSession.family_id == family_id, RefreshSession.revoked_at.is_(None))
            .values(revoked_at=revoked_at or utc_now())
        )
        self.database.commit()
