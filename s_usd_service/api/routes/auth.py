from fastapi import APIRouter, HTTPException, status

from s_usd_service.api.dependencies import CurrentUser, DatabaseSession
from s_usd_service.api.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
    UserRead,
)
from s_usd_service.config import get_settings
from s_usd_service.database.repositories.errors import ConflictError
from s_usd_service.database.repositories.identity import IdentityRepository
from s_usd_service.security.tokens import InvalidRefreshToken, create_access_token, utc_now

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _token_pair(user, session, refresh_token, settings) -> TokenPair:
    access_token, access_expires_at = create_access_token(user.id, session.id, settings)
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        access_expires_at=access_expires_at,
        refresh_expires_at=session.expires_at,
        user=user,
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, database: DatabaseSession):
    settings = get_settings()
    if not settings.allow_registration:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Registration is disabled.")
    try:
        return IdentityRepository(database).create_user(payload.email, payload.display_name, payload.password)
    except ConflictError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, database: DatabaseSession):
    settings = get_settings()
    repository = IdentityRepository(database)
    user = repository.authenticate(payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user.last_login_at = utc_now()
    session, refresh_token = repository.create_refresh_session(
        user,
        settings.refresh_session_days,
        payload.client_name,
        payload.client_fingerprint,
        settings.maximum_active_sessions,
    )
    return _token_pair(user, session, refresh_token, settings)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, database: DatabaseSession):
    settings = get_settings()
    try:
        session, user, refresh_token = IdentityRepository(database).rotate_refresh_session(
            payload.refresh_token, settings.refresh_session_days
        )
    except InvalidRefreshToken as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh session.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
    return _token_pair(user, session, refresh_token, settings)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: LogoutRequest, database: DatabaseSession):
    try:
        IdentityRepository(database).revoke_session(payload.refresh_token)
    except InvalidRefreshToken:
        pass


@router.get("/me", response_model=UserRead)
def me(current_user: CurrentUser):
    return current_user
