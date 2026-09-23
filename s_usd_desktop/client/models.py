from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


def parse_datetime(value):
    return value if isinstance(value, datetime) else datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_uuid(value):
    return value if isinstance(value, UUID) else UUID(value)


@dataclass(frozen=True, slots=True)
class ServiceHealth:
    status: str
    service: str
    version: str

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass(frozen=True, slots=True)
class ProjectRecord:
    id: UUID
    code: str
    name: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=parse_uuid(data["id"]),
            code=data["code"],
            name=data["name"],
            description=data["description"],
            status=data["status"],
            created_at=parse_datetime(data["created_at"]),
            updated_at=parse_datetime(data["updated_at"])
        )


@dataclass(frozen=True, slots=True)
class AssetRecord:
    id: UUID
    project_id: UUID
    code: str
    name: str
    asset_type: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=parse_uuid(data["id"]),
            project_id=parse_uuid(data["project_id"]),
            code=data["code"],
            name=data["name"],
            asset_type=data["asset_type"],
            description=data["description"],
            status=data["status"],
            created_at=parse_datetime(data["created_at"]),
            updated_at=parse_datetime(data["updated_at"])
        )


@dataclass(frozen=True, slots=True)
class StreamRecord:
    id: UUID
    asset_id: UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=parse_uuid(data["id"]),
            asset_id=parse_uuid(data["asset_id"]),
            name=data["name"],
            description=data["description"],
            created_at=parse_datetime(data["created_at"]),
            updated_at=parse_datetime(data["updated_at"])
        )


@dataclass(frozen=True, slots=True)
class VersionRecord:
    id: UUID
    stream_id: UUID
    number: int
    status: str
    comment: str
    created_at: datetime
    updated_at: datetime
    published_content_fingerprint: str | None = None

    @property
    def display_name(self):
        return f"v{self.number:04d}"

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=parse_uuid(data["id"]),
            stream_id=parse_uuid(data["stream_id"]),
            number=data["number"],
            status=data["status"],
            comment=data["comment"],
            created_at=parse_datetime(data["created_at"]),
            updated_at=parse_datetime(data["updated_at"]),
            published_content_fingerprint=data.get("published_content_fingerprint")
        )


@dataclass(frozen=True, slots=True)
class StoredFileRecord:
    id: UUID
    version_id: UUID
    role: str
    original_name: str
    relative_path: str
    storage_key: str
    content_type: str
    size_bytes: int
    sha256: str
    status: str
    created_at: datetime
    updated_at: datetime
    content_url: str

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=parse_uuid(data["id"]),
            version_id=parse_uuid(data["version_id"]),
            role=data["role"],
            original_name=data["original_name"],
            relative_path=data["relative_path"],
            storage_key=data["storage_key"],
            content_type=data["content_type"],
            size_bytes=data["size_bytes"],
            sha256=data["sha256"],
            status=data["status"],
            created_at=parse_datetime(data["created_at"]),
            updated_at=parse_datetime(data["updated_at"]),
            content_url=data["content_url"]
        )


@dataclass(frozen=True, slots=True)
class StoredFileCollection:
    items: tuple[StoredFileRecord, ...]
    count: int

    @classmethod
    def from_dict(cls, data):
        return cls(
            items=tuple(StoredFileRecord.from_dict(item) for item in data["items"]),
            count=data["count"]
        )

@dataclass(frozen=True, slots=True)
class ValidationRunRecord:
    id: UUID
    version_id: UUID
    stored_file_id: UUID | None
    profile_name: str
    report_schema_version: str
    tool_name: str
    tool_version: str
    configuration_fingerprint: str
    check_catalog_fingerprint: str
    content_fingerprint: str
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    publish_passed: bool
    total_count: int
    passed_count: int
    failed_count: int
    skipped_count: int
    error_count: int
    warning_count: int
    created_at: datetime
    updated_at: datetime
    report: dict | None = None

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=parse_uuid(data["id"]),
            version_id=parse_uuid(data["version_id"]),
            stored_file_id=parse_uuid(data["stored_file_id"]) if data.get("stored_file_id") else None,
            profile_name=data["profile_name"],
            report_schema_version=data["report_schema_version"],
            tool_name=data["tool_name"],
            tool_version=data["tool_version"],
            configuration_fingerprint=data["configuration_fingerprint"],
            check_catalog_fingerprint=data["check_catalog_fingerprint"],
            content_fingerprint=data.get("content_fingerprint", ""),
            started_at=parse_datetime(data["started_at"]),
            completed_at=parse_datetime(data["completed_at"]),
            duration_seconds=float(data["duration_seconds"]),
            publish_passed=bool(data["publish_passed"]),
            total_count=int(data["total_count"]),
            passed_count=int(data["passed_count"]),
            failed_count=int(data["failed_count"]),
            skipped_count=int(data["skipped_count"]),
            error_count=int(data["error_count"]),
            warning_count=int(data["warning_count"]),
            created_at=parse_datetime(data["created_at"]),
            updated_at=parse_datetime(data["updated_at"]),
            report=data.get("report")
        )
