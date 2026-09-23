from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field, model_validator

from s_usd_service.api.schemas.common import ApiModel


class ValidationSummary(ApiModel):
    total: int = Field(ge=0)
    passed: int = Field(ge=0)
    failed: int = Field(ge=0)
    skipped: int = Field(default=0, ge=0)
    errors: int = Field(default=0, ge=0)
    warnings: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_counts(self):
        if self.passed + self.failed + self.skipped > self.total:
            raise ValueError("Validation summary counts cannot exceed total")
        return self


class ValidationRunCreate(ApiModel):
    stored_file_id: UUID | None = None
    profile_name: str = Field(min_length=1, max_length=128)
    report_schema_version: str = Field(min_length=1, max_length=32)
    tool_name: str = Field(min_length=1, max_length=128)
    tool_version: str = Field(min_length=1, max_length=64)
    configuration_fingerprint: str = Field(default="", max_length=64)
    check_catalog_fingerprint: str = Field(default="", max_length=64)
    started_at: datetime
    completed_at: datetime
    duration_seconds: float = Field(default=0.0, ge=0)
    publish_passed: bool
    summary: ValidationSummary
    report: dict[str, Any]

    @model_validator(mode="after")
    def validate_times(self):
        if self.completed_at < self.started_at:
            raise ValueError("completed_at cannot be earlier than started_at")
        return self


class ValidationRunRead(ApiModel):
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


class ValidationRunDetail(ValidationRunRead):
    report: dict[str, Any]
