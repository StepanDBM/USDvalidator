from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from s_usd_service.config import get_settings
from s_usd_service.database.models.user import User
from s_usd_service.database.session import get_db
from s_usd_service.security.tokens import InvalidAccessToken, decode_access_token
from s_usd_service.storage import ObjectStorage, create_object_storage

DatabaseSession = Annotated[Session, Depends(get_db)]
_bearer = HTTPBearer(auto_error=False)


@lru_cache
def get_object_storage():
    return create_object_storage(get_settings())


ObjectStorageDependency = Annotated[ObjectStorage, Depends(get_object_storage)]


def get_current_user(
    database: DatabaseSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User:
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not credentials or credentials.scheme.casefold() != "bearer":
        raise error
    try:
        claims = decode_access_token(credentials.credentials, get_settings())
    except InvalidAccessToken as token_error:
        raise error from token_error
    user = database.get(User, claims.user_id)
    if not user or not user.is_active:
        raise error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
