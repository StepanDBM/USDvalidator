from pathlib import Path
from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from s_usd_service.api.dependencies import DatabaseSession, ObjectStorageDependency
from s_usd_service.api.schemas.files import StoredFileList, StoredFileRead
from s_usd_service.api.schemas.storage import FileDeletionResponse
from s_usd_service.services.file_lifecycle import FileLifecycleService
from s_usd_service.services.file_transfer import FileTransferService, InvalidRelativePathError

router = APIRouter(tags=["Files"])

def iter_file(storage, storage_key, chunk_size=1024 * 1024):
    with storage.open(storage_key) as source:
        while chunk := source.read(chunk_size):
            yield chunk

def serialize_file(stored_file):
    return StoredFileRead.model_validate({
        **stored_file.__dict__,
        "content_url": f"/api/v1/files/{stored_file.id}/content"
    })


@router.post(
    "/versions/{version_id}/files",
    response_model=StoredFileRead,
    status_code=status.HTTP_201_CREATED
)
def upload_file(
    version_id: UUID,
    database: DatabaseSession,
    storage: ObjectStorageDependency,
    file: UploadFile = File(...),
    role: str = Form(default="other"),
    relative_path: str | None = Form(default=None)
):
    try:
        stored_file = FileTransferService(database, storage).upload(
            version_id=version_id,
            source=file.file,
            original_name=file.filename or "unnamed",
            relative_path=relative_path,
            role=role,
            content_type=file.content_type or "application/octet-stream"
        )
    except InvalidRelativePathError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return serialize_file(stored_file)


@router.get("/versions/{version_id}/files", response_model=StoredFileList)
def list_version_files(version_id: UUID, database: DatabaseSession, storage: ObjectStorageDependency):
    files = FileTransferService(database, storage).list_for_version(version_id)
    return StoredFileList(items=[serialize_file(item) for item in files], count=len(files))


@router.get("/files/{file_id}", response_model=StoredFileRead)
def get_file_metadata(file_id: UUID, database: DatabaseSession, storage: ObjectStorageDependency):
    stored_file = FileTransferService(database, storage).get(file_id)
    return serialize_file(stored_file)


@router.get("/files/{file_id}/content")
def download_file(
    file_id: UUID,
    database: DatabaseSession,
    storage: ObjectStorageDependency
):
    stored_file = FileTransferService(database, storage).get(file_id)

    if not storage.exists(stored_file.storage_key):
        stored_file.status = "missing"
        database.commit()
        raise HTTPException(
            status_code=404,
            detail="Stored file content is missing"
        )

    ascii_name = (
        Path(stored_file.original_name)
        .name
        .encode("ascii", "ignore")
        .decode()
        or "download"
    )
    encoded_name = quote(stored_file.original_name)

    headers = {
        "Content-Length": str(stored_file.size_bytes),
        "Content-Disposition": (
            f'attachment; filename="{ascii_name}"; '
            f"filename*=UTF-8''{encoded_name}"
        ),"ETag": f'"{stored_file.sha256}"'
    }

    return StreamingResponse(
        iter_file(storage, stored_file.storage_key),
        media_type=stored_file.content_type,
        headers=headers
    )


@router.delete("/files/{file_id}", response_model=FileDeletionResponse)
def delete_file(file_id: UUID, database: DatabaseSession, storage: ObjectStorageDependency):
    return FileLifecycleService(database, storage).delete(file_id)
