import pytest

PySide6 = pytest.importorskip("PySide6")
from PySide6.QtCore import QSettings

from s_usd_desktop.services.desktop_settings import ConnectionPreferences, DesktopSettings


def test_connection_preferences_round_trip(tmp_path):
    path = tmp_path / "settings.ini"
    qsettings = QSettings(str(path), QSettings.IniFormat)
    settings = DesktopSettings(qsettings)
    expected = ConnectionPreferences(
        base_url="https://service.example.test/",
        connect_timeout=4.5,
        request_timeout=45.0,
        auto_connect=False
    )

    settings.set_connection_preferences(expected)
    actual = settings.connection_preferences()

    assert actual == expected
    assert actual.to_api_configuration().base_url == "https://service.example.test"
