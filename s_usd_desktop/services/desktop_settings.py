from dataclasses import dataclass

from PySide6.QtCore import QSettings

from s_usd_desktop.client.configuration import ApiClientConfiguration


@dataclass(frozen=True, slots=True)
class ConnectionPreferences:
    base_url: str = "http://127.0.0.1:8000"
    connect_timeout: float = 3.0
    request_timeout: float = 30.0
    auto_connect: bool = True

    def to_api_configuration(self):
        return ApiClientConfiguration(
            base_url=self.base_url,
            connect_timeout=self.connect_timeout,
            read_timeout=self.request_timeout,
            write_timeout=self.request_timeout,
            pool_timeout=self.connect_timeout
        )


class DesktopSettings:
    ORGANIZATION = "Styopa"
    APPLICATION = "S-USDv"

    def __init__(self, settings=None):
        self.settings = settings or QSettings(self.ORGANIZATION, self.APPLICATION)

    def connection_preferences(self):
        return ConnectionPreferences(
            base_url=self.settings.value("service/base_url", "http://127.0.0.1:8000", str),
            connect_timeout=self.settings.value("service/connect_timeout", 3.0, float),
            request_timeout=self.settings.value("service/request_timeout", 30.0, float),
            auto_connect=self.settings.value("service/auto_connect", True, bool)
        )

    def set_connection_preferences(self, preferences):
        self.settings.setValue("service/base_url", preferences.base_url)
        self.settings.setValue("service/connect_timeout", preferences.connect_timeout)
        self.settings.setValue("service/request_timeout", preferences.request_timeout)
        self.settings.setValue("service/auto_connect", preferences.auto_connect)
        self.settings.sync()
