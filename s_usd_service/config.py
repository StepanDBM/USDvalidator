from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="S_USDV_", env_file=".env", extra="ignore")

    service_name: str = "S-USDv Service"
    service_version: str = "0.3.0"
    api_prefix: str = "/api/v1"
    data_root: Path = Path(".s_usdv_data")
    database_url: str = "sqlite:///./.s_usdv_data/s_usdv.db"
    storage_provider: str = "local"
    storage_root: Path = Path(".s_usdv_data/storage")
    temporary_root: Path = Path(".s_usdv_data/temp")
    storage_chunk_size: int = 1024 * 1024
    maximum_upload_bytes: int = 2 * 1024 * 1024 * 1024
    allowed_usd_extensions: tuple[str, ...] = (".usd", ".usda", ".usdc", ".usdz")
    token_signing_key: str = ""
    token_algorithm: str = "HS256"
    token_issuer: str = "s-usdv"
    token_audience: str = "s-usdv-service"
    access_token_minutes: int = 15
    refresh_session_days: int = 30
    token_clock_skew_seconds: int = 30
    allow_registration: bool = True
    maximum_active_sessions: int = 10
    validation_worker_enabled: bool = True
    validation_worker_poll_seconds: float = 1.0
    validation_job_maximum_attempts: int = 3
    validation_job_retry_delay_seconds: int = 5
    allowed_file_roles: tuple[str, ...] = (
        "root_layer",
        "dependency",
        "texture",
        "preview",
        "manifest",
        "report",
        "other",
    )

    def prepare_directories(self):
        self.data_root.mkdir(parents=True, exist_ok=True)
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self.temporary_root.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings():
    settings = ServiceSettings()
    settings.prepare_directories()
    return settings
