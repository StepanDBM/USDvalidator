from dataclasses import dataclass
import os
from pathlib import Path
import sys


_DLL_HANDLES = []


class OpenUsdBootstrapError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class OpenUsdRuntimeLayout:
    root: Path
    python_root: Path
    library_root: Path
    binary_root: Path
    plugin_root: Path

    @classmethod
    def from_root(cls, root):
        root = Path(root).expanduser().resolve()
        return cls(
            root=root,
            python_root=root / "lib" / "python",
            library_root=root / "lib",
            binary_root=root / "bin",
            plugin_root=root / "plugin" / "usd"
        )

    @property
    def valid(self):
        required = (
            self.python_root / "pxr" / "Usd" / "__init__.py",
            self.python_root / "pxr" / "Usdviewq" / "stageView.py",
            self.python_root / "pxr" / "UsdImagingGL" / "__init__.py",
            self.library_root / "usd_usdImagingGL.dll",
            self.plugin_root
        )
        return all(path.exists() for path in required)


@dataclass(frozen=True, slots=True)
class OpenUsdBootstrapResult:
    applied: bool
    layout: OpenUsdRuntimeLayout | None
    message: str


def bootstrap_openusd_runtime(project_root=None, runtime_root=None, strict=False):
    if any(name == "pxr" or name.startswith("pxr.") for name in sys.modules):
        message = "OpenUSD runtime bootstrap must run before importing any pxr module"
        if strict:
            raise OpenUsdBootstrapError(message)
        return OpenUsdBootstrapResult(False, None, message)

    layout = discover_openusd_runtime(project_root=project_root, runtime_root=runtime_root)

    if layout is None:
        message = "No complete OpenUSD runtime containing Usdviewq and UsdImagingGL was found"
        if strict:
            raise OpenUsdBootstrapError(message)
        return OpenUsdBootstrapResult(False, None, message)

    _prepend_sys_path(layout.python_root)
    _prepend_environment_path("PATH", layout.binary_root)
    _prepend_environment_path("PATH", layout.library_root)
    _prepend_environment_path("PXR_PLUGINPATH_NAME", layout.plugin_root)
    _register_dll_directory(layout.binary_root)
    _register_dll_directory(layout.library_root)
    os.environ["S_USDV_OPENUSD_ROOT"] = str(layout.root)
    return OpenUsdBootstrapResult(True, layout, f"OpenUSD runtime bootstrapped from {layout.root}")


def discover_openusd_runtime(project_root=None, runtime_root=None):
    candidates = []

    if runtime_root:
        candidates.append(Path(runtime_root))

    configured = os.environ.get("S_USDV_OPENUSD_ROOT")
    if configured:
        candidates.append(Path(configured))

    project_root = Path(project_root or Path.cwd()).expanduser().resolve()
    candidates.extend(_ancestor_candidates(project_root))
    candidates.extend(_ancestor_candidates(Path(__file__).resolve()))

    seen = set()

    for candidate in candidates:
        candidate = candidate.expanduser().resolve()
        if candidate in seen:
            continue
        seen.add(candidate)
        layout = OpenUsdRuntimeLayout.from_root(candidate)
        if layout.valid:
            return layout

    return None


def _ancestor_candidates(path):
    current = path if path.is_dir() else path.parent

    for parent in (current, *current.parents):
        yield parent / "Setup"
        if parent.name.lower() == "usds":
            yield parent / "Setup"


def _prepend_sys_path(path):
    value = str(path)
    sys.path[:] = [entry for entry in sys.path if _normalized(entry) != _normalized(value)]
    sys.path.insert(0, value)


def _prepend_environment_path(name, path):
    value = str(path)
    existing = [item for item in os.environ.get(name, "").split(os.pathsep) if item]
    existing = [item for item in existing if _normalized(item) != _normalized(value)]
    os.environ[name] = os.pathsep.join([value, *existing])


def _register_dll_directory(path):
    if os.name != "nt" or not hasattr(os, "add_dll_directory") or not path.is_dir():
        return
    _DLL_HANDLES.append(os.add_dll_directory(str(path)))


def _normalized(value):
    return os.path.normcase(os.path.abspath(value or "."))
