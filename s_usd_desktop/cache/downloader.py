import hashlib
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from s_usd_desktop.cache.entry import CacheEntry, CacheEntryStatus
from s_usd_desktop.cache.errors import (
    CacheWriteError,
    ChecksumMismatchError,
    DownloadCancelledError,
    SizeMismatchError,
    StoredContentMissingError
)
from s_usd_desktop.client.errors import ResourceNotFoundError


@dataclass(frozen=True, slots=True)
class CacheLocation:
    project_code: str
    asset_code: str
    stream_name: str
    version_number: int


class DownloadCancellationToken:
    def __init__(self):
        from threading import Event
        self._event = Event()

    @property
    def cancelled(self):
        return self._event.is_set()

    def cancel(self):
        self._event.set()

    def raise_if_cancelled(self):
        if self.cancelled:
            raise DownloadCancelledError("Download cancelled")


class VerifiedDownloader:
    def __init__(self, file_client, cache_manager, chunk_size=1024 * 1024):
        self.file_client = file_client
        self.cache_manager = cache_manager
        self.chunk_size = int(chunk_size)

        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

    def download(self, stored_file, location, progress=None, token=None):
        token = token or DownloadCancellationToken()
        inspection = self.cache_manager.inspect(
            location.project_code,
            location.asset_code,
            location.stream_name,
            location.version_number,
            stored_file
        )
        final_path = inspection.local_path
        part_path = final_path.with_name(f"{final_path.name}.part")
        replacement_path = final_path.with_name(f"{final_path.name}.replacement")
        final_path.parent.mkdir(parents=True, exist_ok=True)
        part_path.unlink(missing_ok=True)
        replacement_path.unlink(missing_ok=True)
        digest = hashlib.sha256()
        received = 0

        try:
            token.raise_if_cancelled()

            with self.file_client.stream_content(stored_file.id) as response:
                expected_header = response.headers.get("content-length")
                expected_length = int(expected_header) if expected_header else int(stored_file.size_bytes)

                with part_path.open("xb") as output:
                    for chunk in response.iter_bytes(self.chunk_size):
                        token.raise_if_cancelled()

                        if not chunk:
                            continue

                        output.write(chunk)
                        digest.update(chunk)
                        received += len(chunk)

                        if progress:
                            progress(received, expected_length)

                    output.flush()
                    os.fsync(output.fileno())

            token.raise_if_cancelled()
            self._verify(stored_file, received, digest.hexdigest())
            os.replace(part_path, replacement_path)
            os.replace(replacement_path, final_path)
            now = datetime.now(timezone.utc)
            entry = CacheEntry(
                file_id=stored_file.id,
                version_id=stored_file.version_id,
                relative_path=stored_file.relative_path,
                local_path=final_path,
                size_bytes=received,
                sha256=digest.hexdigest(),
                downloaded_at=now,
                last_accessed_at=now,
                status=CacheEntryStatus.AVAILABLE
            )
            self.cache_manager.record(
                location.project_code,
                location.asset_code,
                location.stream_name,
                location.version_number,
                entry
            )
            return entry
        except ResourceNotFoundError as error:
            raise StoredContentMissingError(
                f"Stored content is missing for file {stored_file.id}"
            ) from error
        except (DownloadCancelledError, ChecksumMismatchError, SizeMismatchError):
            raise
        except OSError as error:
            raise CacheWriteError(f"Could not write cache file: {final_path}") from error
        finally:
            part_path.unlink(missing_ok=True)
            replacement_path.unlink(missing_ok=True)

    @staticmethod
    def _verify(stored_file, received, digest):
        expected_size = int(stored_file.size_bytes)

        if received != expected_size:
            raise SizeMismatchError(
                f"Downloaded {received} bytes, expected {expected_size} bytes"
            )

        if digest.lower() != stored_file.sha256.lower():
            raise ChecksumMismatchError(
                f"Downloaded SHA-256 {digest} does not match {stored_file.sha256}"
            )
