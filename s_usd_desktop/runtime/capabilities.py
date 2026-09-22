from dataclasses import dataclass
from importlib import import_module
import os
import platform
import sys


@dataclass(frozen=True, slots=True)
class CapabilityProbe:
    name: str
    available: bool
    module: str
    location: str = ""
    version: str = ""
    error: str = ""


@dataclass(frozen=True, slots=True)
class RuntimeCapabilities:
    python_version: str
    python_executable: str
    platform: str
    openusd_core: CapabilityProbe
    usdviewq: CapabilityProbe
    usd_imaging_gl: CapabilityProbe
    pyside6: CapabilityProbe
    opengl_context: CapabilityProbe
    plugin_path: str

    @property
    def viewport_available(self):
        return all((
            self.openusd_core.available,
            self.usdviewq.available,
            self.usd_imaging_gl.available,
            self.pyside6.available,
            self.opengl_context.available
        ))

    @property
    def unavailable_reasons(self):
        probes = (
            self.openusd_core,
            self.usdviewq,
            self.usd_imaging_gl,
            self.pyside6,
            self.opengl_context
        )
        return tuple(
            f"{probe.name}: {probe.error or 'unavailable'}"
            for probe in probes
            if not probe.available
        )

    def to_dict(self):
        return {
            "python": {
                "version": self.python_version,
                "executable": self.python_executable,
                "platform": self.platform
            },
            "environment": {"PXR_PLUGINPATH_NAME": self.plugin_path},
            "viewport_available": self.viewport_available,
            "capabilities": {
                probe.name: {
                    "available": probe.available,
                    "module": probe.module,
                    "location": probe.location,
                    "version": probe.version,
                    "error": probe.error
                }
                for probe in (
                    self.openusd_core,
                    self.usdviewq,
                    self.usd_imaging_gl,
                    self.pyside6,
                    self.opengl_context
                )
            }
        }

    def diagnostic_text(self):
        state = "AVAILABLE" if self.viewport_available else "UNAVAILABLE"
        lines = [
            f"Embedded viewport: {state}",
            f"Python: {self.python_version}",
            f"Executable: {self.python_executable}",
            f"Platform: {self.platform}",
            f"PXR_PLUGINPATH_NAME: {self.plugin_path or '<not set>'}",
            ""
        ]

        for probe in (
            self.openusd_core,
            self.usdviewq,
            self.usd_imaging_gl,
            self.pyside6,
            self.opengl_context
        ):
            status = "available" if probe.available else "missing"
            lines.append(f"{probe.name}: {status}")
            if probe.version:
                lines.append(f"  Version: {probe.version}")
            if probe.location:
                lines.append(f"  Location: {probe.location}")
            if probe.error:
                lines.append(f"  Error: {probe.error}")

        return "\n".join(lines)


def detect_runtime_capabilities(importer=import_module):
    core = _probe_module("OpenUSD Core", "pxr.Usd", importer, _usd_version)
    usdviewq = _probe_module("Usdviewq", "pxr.Usdviewq.stageView", importer)
    imaging = _probe_module("Hydra Imaging", "pxr.UsdImagingGL", importer)
    pyside = _probe_module("PySide6", "PySide6", importer, _module_version)
    opengl = _probe_opengl(importer)
    return RuntimeCapabilities(
        python_version=platform.python_version(),
        python_executable=sys.executable,
        platform=platform.platform(),
        openusd_core=core,
        usdviewq=usdviewq,
        usd_imaging_gl=imaging,
        pyside6=pyside,
        opengl_context=opengl,
        plugin_path=os.environ.get("PXR_PLUGINPATH_NAME", "")
    )


def _probe_module(name, module_name, importer, version_getter=None):
    try:
        module = importer(module_name)
        version = version_getter(module) if version_getter else ""
        return CapabilityProbe(
            name=name,
            available=True,
            module=module_name,
            location=getattr(module, "__file__", "") or "",
            version=version
        )
    except Exception as error:
        return CapabilityProbe(
            name=name,
            available=False,
            module=module_name,
            error=f"{type(error).__name__}: {error}"
        )


def _probe_opengl(importer):
    try:
        gui = importer("PySide6.QtGui")
        application = gui.QGuiApplication.instance()

        if application is None:
            return CapabilityProbe(
                "OpenGL Context",
                False,
                "PySide6.QtGui.QOpenGLContext",
                error="QGuiApplication is not running"
            )

        context = gui.QOpenGLContext()
        if not context.create() or not context.isValid():
            return CapabilityProbe(
                "OpenGL Context",
                False,
                "PySide6.QtGui.QOpenGLContext",
                error="Qt could not create a valid OpenGL context"
            )

        surface_format = context.format()
        version = f"{surface_format.majorVersion()}.{surface_format.minorVersion()}"
        return CapabilityProbe(
            "OpenGL Context",
            True,
            "PySide6.QtGui.QOpenGLContext",
            version=version
        )
    except Exception as error:
        return CapabilityProbe(
            "OpenGL Context",
            False,
            "PySide6.QtGui.QOpenGLContext",
            error=f"{type(error).__name__}: {error}"
        )


def _usd_version(module):
    getter = getattr(module, "GetVersion", None)
    if not getter:
        return ""
    value = getter()
    return ".".join(str(part) for part in value) if isinstance(value, tuple) else str(value)


def _module_version(module):
    return str(getattr(module, "__version__", ""))
