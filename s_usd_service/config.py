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
    storage_root: Path = Path(".s_usdv_data/storage")
    temporary_root: Path = Path(".s_usdv_data/temp")
    storage_chunk_size: int = 1024 * 1024
    maximum_upload_bytes: int = 2 * 1024 * 1024 * 1024
    allowed_usd_extensions: tuple[str, ...] = (".usd", ".usda", ".usdc", ".usdz")
    allowed_file_roles: tuple[str, ...] = (
        "root_layer",
        "dependency",
        "texture",
        "preview",
        "manifest",
        "report",
        "other"
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
