from types import SimpleNamespace

from s_usd_desktop.runtime import CapabilityProbe, RuntimeCapabilities, detect_runtime_capabilities


def fake_importer(name):
    modules = {
        "pxr.Usd": SimpleNamespace(__file__="/usd/Usd.py", GetVersion=lambda: (25, 8, 0)),
        "pxr.Usdviewq.stageView": SimpleNamespace(__file__="/usd/Usdviewq/stageView.py"),
        "pxr.UsdImagingGL": SimpleNamespace(__file__="/usd/UsdImagingGL.py"),
        "PySide6": SimpleNamespace(__file__="/qt/__init__.py", __version__="6.8.0")
    }

    if name == "PySide6.QtGui":
        class Format:
            def majorVersion(self): return 4
            def minorVersion(self): return 6

        class Context:
            def create(self): return True
            def isValid(self): return True
            def format(self): return Format()

        return SimpleNamespace(
            QGuiApplication=SimpleNamespace(instance=lambda: object()),
            QOpenGLContext=Context
        )

    if name not in modules:
        raise ModuleNotFoundError(name)
    return modules[name]


def test_detects_complete_viewport_runtime():
    capabilities = detect_runtime_capabilities(fake_importer)

    assert capabilities.viewport_available is True
    assert capabilities.openusd_core.version == "25.8.0"
    assert capabilities.pyside6.version == "6.8.0"
    assert capabilities.opengl_context.version == "4.6"


def test_missing_usdviewq_disables_only_viewport():
    def importer(name):
        if name == "pxr.Usdviewq.stageView":
            raise ModuleNotFoundError("No module named 'pxr.Usdviewq'")
        return fake_importer(name)

    capabilities = detect_runtime_capabilities(importer)

    assert capabilities.openusd_core.available is True
    assert capabilities.usdviewq.available is False
    assert capabilities.viewport_available is False
    assert "Usdviewq" in capabilities.unavailable_reasons[0]


def test_capability_report_is_serializable():
    missing = CapabilityProbe("Usdviewq", False, "pxr.Usdviewq", error="missing")
    available = CapabilityProbe("Available", True, "module", location="module.py")
    capabilities = RuntimeCapabilities(
        "3.12", "python.exe", "Windows", available, missing, available,
        available, available, "C:/OpenUSD/plugin"
    )

    data = capabilities.to_dict()

    assert data["viewport_available"] is False
    assert data["capabilities"]["Usdviewq"]["error"] == "missing"
    assert "Embedded viewport: UNAVAILABLE" in capabilities.diagnostic_text()
