from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from s_usd_service.config import get_settings
from s_usd_service.database.session import get_db
from s_usd_service.storage.local import LocalObjectStorage

DatabaseSession = Annotated[Session, Depends(get_db)]


@lru_cache
def get_object_storage():
    settings = get_settings()
    return LocalObjectStorage(
        root=settings.storage_root,
        temporary_root=settings.temporary_root,
        chunk_size=settings.storage_chunk_size
    )


ObjectStorageDependency = Annotated[LocalObjectStorage, Depends(get_object_storage)]
