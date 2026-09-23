from sqlalchemy import select

from s_usd_service.database.models import StoredFile, ValidationRun, Version
from s_usd_service.database.repositories.errors import ConflictError, NotFoundError
from s_usd_service.domain.version_lifecycle import VersionStatus
from s_usd_service.services.content_fingerprint import VersionContentFingerprint


SUPPORTED_REPORT_SCHEMA_VERSIONS = frozenset({"1.0.0"})


class VersionLifecycleService:
    def __init__(self, database):
        self.database = database

    def ensure_content_mutable(self, version):
        if version.status in {VersionStatus.PUBLISHED, VersionStatus.DEPRECATED}:
            raise ConflictError(
                "Published and deprecated versions are immutable. Create a new version instead."
            )

    def mark_after_upload(self, version, stored_file):
        self.ensure_content_mutable(version)
        if stored_file.role == "root_layer" and stored_file.status == "available":
            version.status = VersionStatus.UPLOADED
        elif version.status in {
            VersionStatus.VALIDATED,
            VersionStatus.VALIDATION_FAILED
        }:
            version.status = VersionStatus.UPLOADED

    def mark_after_delete(self, version, deleted_file):
        self.ensure_content_mutable(version)
        remaining = [item for item in version.files if item.id != deleted_file.id]
        has_root = any(
            item.role == "root_layer" and item.status == "available"
            for item in remaining
        )
        version.status = VersionStatus.UPLOADED if has_root else VersionStatus.DRAFT

    def mark_after_validation(self, version, validation_run):
        if version.status in {VersionStatus.PUBLISHED, VersionStatus.DEPRECATED}:
            return
        if not validation_run.stored_file_id:
            return
        stored_file = self.database.get(StoredFile, validation_run.stored_file_id)
        if not stored_file or stored_file.role != "root_layer":
            return
        version.status = (
            VersionStatus.VALIDATED
            if validation_run.publish_passed
            else VersionStatus.VALIDATION_FAILED
        )

    def publish(self, version_id):
        version = self._version(version_id)
        if version.status == VersionStatus.PUBLISHED:
            if not version.published_content_fingerprint:
                version.published_content_fingerprint = VersionContentFingerprint.calculate(
                    self._files(version_id)
                )
                self.database.commit()
                self.database.refresh(version)
            return version
        if version.status == VersionStatus.DEPRECATED:
            raise ConflictError("Deprecated versions cannot be published again")

        files = self._files(version_id)
        roots = [item for item in files if item.role == "root_layer"]
        if len(roots) != 1:
            raise ConflictError("Publishing requires exactly one root layer")
        if not files or any(item.status != "available" for item in files):
            raise ConflictError("Every registered file must be available before publishing")

        validation = self.database.scalar(
            select(ValidationRun)
            .where(
                ValidationRun.version_id == version_id,
                ValidationRun.stored_file_id == roots[0].id
            )
            .order_by(ValidationRun.created_at.desc())
        )
        if not validation:
            raise ConflictError("Publishing requires a validation run for the current root layer")
        if not validation.publish_passed:
            raise ConflictError("The latest root-layer validation did not pass")
        if validation.report_schema_version not in SUPPORTED_REPORT_SCHEMA_VERSIONS:
            raise ConflictError(
                f"Unsupported validation report schema: {validation.report_schema_version}"
            )
        report_validation = validation.report.get("validation", {})
        if report_validation.get("cancelled", False):
            raise ConflictError("Cancelled validation runs cannot authorize publishing")

        content_fingerprint = VersionContentFingerprint.calculate(files)
        if not validation.content_fingerprint:
            raise ConflictError(
                "The latest validation predates content fingerprints; validate the version again"
            )
        if validation.content_fingerprint != content_fingerprint:
            raise ConflictError(
                "The latest validation does not match the current version contents"
            )

        version.status = VersionStatus.PUBLISHED
        version.published_content_fingerprint = content_fingerprint
        self.database.commit()
        self.database.refresh(version)
        return version

    def deprecate(self, version_id):
        version = self._version(version_id)
        if version.status == VersionStatus.DEPRECATED:
            return version
        if version.status != VersionStatus.PUBLISHED:
            raise ConflictError("Only published versions can be deprecated")
        version.status = VersionStatus.DEPRECATED
        self.database.commit()
        self.database.refresh(version)
        return version

    def _version(self, version_id):
        version = self.database.get(Version, version_id)
        if not version:
            raise NotFoundError("Version not found")
        return version

    def _files(self, version_id):
        statement = select(StoredFile).where(StoredFile.version_id == version_id)
        return list(self.database.scalars(statement).all())
