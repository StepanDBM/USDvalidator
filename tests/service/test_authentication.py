from datetime import timedelta

import jwt
from sqlalchemy import select

from s_usd_service.config import get_settings
from s_usd_service.database.models.refresh_session import RefreshSession
from s_usd_service.database.models.user import User
from s_usd_service.database.session import SessionLocal
from s_usd_service.security.tokens import utc_now

USER = {
    "email": "artist@example.com",
    "display_name": "Asset Artist",
    "password": "correct horse battery staple",
}


def register(anonymous_client, payload=None):
    return anonymous_client.post("/api/v1/auth/register", json=payload or USER)


def login(anonymous_client, password=USER["password"]):
    return anonymous_client.post(
        "/api/v1/auth/login",
        json={"email": USER["email"], "password": password, "client_name": "pytest"},
    )


def test_register_hashes_password_and_rejects_duplicate_email(anonymous_client):
    response = register(anonymous_client)
    assert response.status_code == 201
    assert response.json()["email"] == USER["email"]
    assert "password" not in response.json()

    with SessionLocal() as database:
        user = database.scalar(select(User))
        assert user.password_hash != USER["password"]
        assert user.password_hash.startswith("$argon2id$")

    duplicate = register(anonymous_client, {**USER, "email": "ARTIST@example.com"})
    assert duplicate.status_code == 409


def test_login_returns_access_and_hashed_refresh_session(anonymous_client):
    register(anonymous_client)
    response = login(anonymous_client)
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]

    with SessionLocal() as database:
        session = database.scalar(select(RefreshSession))
        assert session.token_hash not in data["refresh_token"]
        assert session.client_name == "pytest"


def test_invalid_credentials_use_one_non_revealing_response(anonymous_client):
    register(anonymous_client)
    wrong_password = login(anonymous_client, "definitely wrong")
    missing_user = anonymous_client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "definitely wrong"},
    )
    assert wrong_password.status_code == 401
    assert missing_user.status_code == 401
    assert wrong_password.json() == missing_user.json()


def test_me_requires_and_accepts_access_token(anonymous_client):
    register(anonymous_client)
    tokens = login(anonymous_client).json()
    assert anonymous_client.get("/api/v1/auth/me").status_code == 401
    response = anonymous_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert response.status_code == 200
    assert response.json()["email"] == USER["email"]


def test_refresh_rotates_token_and_reuse_revokes_family(anonymous_client):
    register(anonymous_client)
    first = login(anonymous_client).json()
    second_response = anonymous_client.post("/api/v1/auth/refresh", json={"refresh_token": first["refresh_token"]})
    assert second_response.status_code == 200
    second = second_response.json()
    assert second["refresh_token"] != first["refresh_token"]

    reuse = anonymous_client.post("/api/v1/auth/refresh", json={"refresh_token": first["refresh_token"]})
    assert reuse.status_code == 401
    revoked_replacement = anonymous_client.post("/api/v1/auth/refresh", json={"refresh_token": second["refresh_token"]})
    assert revoked_replacement.status_code == 401


def test_logout_revokes_refresh_session(anonymous_client):
    register(anonymous_client)
    tokens = login(anonymous_client).json()
    response = anonymous_client.post("/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 204
    assert (
        anonymous_client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code
        == 401
    )


def test_disabled_user_cannot_login_or_refresh(anonymous_client):
    register(anonymous_client)
    tokens = login(anonymous_client).json()
    with SessionLocal() as database:
        user = database.scalar(select(User))
        user.is_active = False
        database.commit()

    assert login(anonymous_client).status_code == 401
    assert (
        anonymous_client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code
        == 401
    )


def test_expired_and_wrong_audience_access_tokens_are_rejected(anonymous_client):
    register(anonymous_client)
    tokens = login(anonymous_client).json()
    settings = get_settings()
    claims = jwt.decode(
        tokens["access_token"],
        settings.token_signing_key,
        algorithms=[settings.token_algorithm],
        audience=settings.token_audience,
        issuer=settings.token_issuer,
    )
    claims["exp"] = utc_now() - timedelta(seconds=60)
    expired = jwt.encode(claims, settings.token_signing_key, algorithm=settings.token_algorithm)
    claims["exp"] = utc_now() + timedelta(minutes=5)
    claims["aud"] = "another-service"
    wrong_audience = jwt.encode(claims, settings.token_signing_key, algorithm=settings.token_algorithm)

    for token in (expired, wrong_audience):
        response = anonymous_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401


def test_registration_can_be_disabled(anonymous_client, monkeypatch):
    monkeypatch.setattr(get_settings(), "allow_registration", False)
    response = register(anonymous_client)
    assert response.status_code == 403
    assert response.json() == {"detail": "Registration is disabled."}


def test_maximum_active_sessions_revokes_oldest_session(anonymous_client, monkeypatch):
    monkeypatch.setattr(get_settings(), "maximum_active_sessions", 2)
    register(anonymous_client)
    sessions = [login(anonymous_client).json() for _ in range(3)]

    assert (
        anonymous_client.post("/api/v1/auth/refresh", json={"refresh_token": sessions[0]["refresh_token"]}).status_code
        == 401
    )
    assert (
        anonymous_client.post("/api/v1/auth/refresh", json={"refresh_token": sessions[-1]["refresh_token"]}).status_code
        == 200
    )
