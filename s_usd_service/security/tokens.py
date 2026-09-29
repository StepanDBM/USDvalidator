from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from secrets import token_urlsafe
from uuid import UUID, uuid4

import jwt

from s_usd_service.config import ServiceSettings


class InvalidAccessToken(ValueError):
    pass


class InvalidRefreshToken(ValueError):
    pass


@dataclass(frozen=True)
class AccessTokenClaims:
    user_id: UUID
    session_id: UUID


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _validate_signing_key(settings: ServiceSettings) -> None:
    if len(settings.token_signing_key.encode("utf-8")) < 32:
        raise RuntimeError("S_USDV_TOKEN_SIGNING_KEY must contain at least 32 bytes.")


def create_access_token(user_id: UUID, session_id: UUID, settings: ServiceSettings) -> tuple[str, datetime]:
    _validate_signing_key(settings)
    issued_at = utc_now()
    expires_at = issued_at + timedelta(minutes=settings.access_token_minutes)
    payload = {
        "sub": str(user_id),
        "sid": str(session_id),
        "jti": str(uuid4()),
        "type": "access",
        "iat": issued_at,
        "exp": expires_at,
        "iss": settings.token_issuer,
        "aud": settings.token_audience,
    }
    token = jwt.encode(payload, settings.token_signing_key, algorithm=settings.token_algorithm)
    return token, expires_at


def decode_access_token(token: str, settings: ServiceSettings) -> AccessTokenClaims:
    _validate_signing_key(settings)
    try:
        payload = jwt.decode(
            token,
            settings.token_signing_key,
            algorithms=[settings.token_algorithm],
            audience=settings.token_audience,
            issuer=settings.token_issuer,
            leeway=settings.token_clock_skew_seconds,
            options={"require": ["sub", "sid", "jti", "type", "iat", "exp", "iss", "aud"]},
        )
        if payload["type"] != "access":
            raise InvalidAccessToken("Unexpected token type.")
        return AccessTokenClaims(user_id=UUID(payload["sub"]), session_id=UUID(payload["sid"]))
    except (jwt.PyJWTError, KeyError, TypeError, ValueError) as error:
        raise InvalidAccessToken("Invalid or expired access token.") from error


def create_refresh_token(session_id: UUID) -> tuple[str, str]:
    token = f"{session_id}.{token_urlsafe(48)}"
    return token, hash_refresh_token(token)


def parse_refresh_session_id(token: str) -> UUID:
    try:
        session_id, secret = token.split(".", maxsplit=1)
        if not secret:
            raise ValueError
        return UUID(session_id)
    except (AttributeError, ValueError) as error:
        raise InvalidRefreshToken("Invalid refresh token.") from error


def hash_refresh_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()
