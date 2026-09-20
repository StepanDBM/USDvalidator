from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="S_USD_", env_file=".env", extra="ignore")

    service_name: str = "S-USD Service"
    service_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    data_root: Path = Path(".s_usd_data")
    database_url: str = "sqlite:///./.s_usd_data/s_usd.db"

    def prepare_directories(self):
        self.data_root.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings():
    settings = ServiceSettings()
    settings.prepare_directories()
    return settings
