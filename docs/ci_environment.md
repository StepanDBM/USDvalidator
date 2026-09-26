# CI Environment Contract

This document defines the clean environment that S-USDv CI must reproduce before the GitHub Actions workflow is added.

## Supported baseline

- Ubuntu (`ubuntu-latest`) for the hosted runner
- Python 3.12
- SQLite for the first CI pass
- Qt in offscreen mode for desktop tests
- OpenUSD core Python bindings for validation and comparison tests
- The embedded OpenUSD viewport is optional in hosted CI

## Dependency layers

Install the dependency set matching the task:

```powershell
# Backend service only
python -m pip install -r requirements-service.txt

# Local desktop development with an external OpenUSD runtime
python -m pip install -r requirements-desktop.txt

# Hosted CI, including portable OpenUSD core bindings
python -m pip install -r requirements-ci.txt
```

`requirements-ci.txt` uses the `usd-core` package for portable core bindings. It does not provide `pxr.Usdviewq`, so the hosted runner validates viewport capability fallback behavior rather than the embedded Hydra viewport itself.

A workstation with a full OpenUSD build can instead set:

```powershell
$env:S_USDV_OPENUSD_ROOT = "E:\path\to\OpenUSD\Setup"
```

The directory must follow the runtime layout already expected by `s_usd_desktop.runtime.bootstrap`.

## Isolated test state

CI must not use `.s_usdv_data` from a developer workstation. Each run should point the service at a temporary root:

```powershell
$root = Join-Path $env:TEMP "s-usdv-ci"
$env:S_USDV_DATA_ROOT = $root
$env:S_USDV_DATABASE_URL = "sqlite:///$($root.Replace('\', '/'))/s_usdv.db"
$env:S_USDV_STORAGE_ROOT = Join-Path $root "storage"
$env:S_USDV_TEMPORARY_ROOT = Join-Path $root "temp"
$env:QT_QPA_PLATFORM = "offscreen"
```

Tests already use temporary paths extensively. The environment variables above additionally isolate application imports, Alembic, and future smoke tests.

## Clean-environment verification

From the repository root:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements-ci.txt
python scripts/ci/check_environment.py
python -m compileall -q s_usd_core s_usd_service s_usd_desktop
python scripts/ci/run_tests.py tests -v
```

The hosted workflow uses Ubuntu because `usd-core` publishes Linux Python wheels. It installs `libgl1`, `libegl1`, and `libxkbcommon-x11-0` before importing Qt. Full `UsdImagingGL` and `Usdviewq` verification remains part of the clean Windows workstation check.

The environment probe treats these as required:

- FastAPI, HTTPX, SQLAlchemy, Alembic, pydantic-settings and python-multipart
- pytest and PySide6
- `pxr.Sdf`, `pxr.Usd`, `pxr.UsdGeom` and `pxr.UsdShade`

These remain optional in hosted CI:

- `pxr.UsdImagingGL`
- `pxr.Usdviewq`

## Deliberate exclusions from Chunk 1

Chunk 1 prepares reproducibility only. It does not yet add:

- GitHub Actions workflow files
- PostgreSQL
- security scanners
- release packaging
- authentication dependencies
- branch protection

Those belong to later CI/CD chunks after this environment contract passes locally.
