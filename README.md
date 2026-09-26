# USDvalidator

USDvalidator is a registry-driven OpenUSD publish validation application designed for pipeline engineering workflows and is based off my own ValiW tool for cross-DCC pipeline validation.

It inspects USD stages, extracts stage-health information, executes configurable/overridable validation checks, and produces structured reports for individual files or complete directories.

The application includes:

- A PySide6 desktop interface
- Single-file and batch validation
- Registry-driven check discovery
- Editable validation profiles
- Profile-specific configuration overrides
- Typed runtime check configuration
- Stage-health inspection
- JSON report generation
- Publish manifest generation
- Automated tests and USD fixtures

USDvalidator separates extracted USD facts from validation policy. The same USD stage can therefore pass under one validation profile and fail under another without modifying the stage, the check implementations, or the global defaults.

---

## Project Status

USDvalidator currently provides a functional validation architecture and desktop interface.

The current system supports:

- Opening and inspecting `.usd`, `.usda`, `.usdc`, and `.usdz` files
- Selecting either a USD file or a directory
- Automatically choosing single-file or batch validation
- Extracting stage, hierarchy, metadata, geometry, animation, composition, and dependency information
- Discovering checks from the Python validation registry
- Creating and editing validation profiles
- Adding registered checks to profiles
- Removing checks from profiles
- Creating typed configuration overrides
- Editing, enabling, disabling, and removing overrides
- Applying profile overrides to isolated runtime configuration
- Displaying validation results in the UI
- Exporting stable JSON reports
- Generating publish-oriented manifests
- Testing valid and intentionally invalid USD stages

The project is actively evolving toward a complete pipeline-oriented USD publishing tool.

---

# Core Architecture

USDvalidator is organized around several intentionally separate concepts.

```text
CheckDefinition
    What check exists?
    Where does it run?
    What does it target?
    What is its category, phase, severity, and identity?

ValidationProfile
    Which registered checks belong to this profile?
    Which checks should execute during validation?

AttributeOverride
    What configuration value does this profile replace?
    What is the replacement value?
    Is the replacement enabled?

ValidationRuleConfig
    What are the default validation rules and limits?

CheckRuntimeContext
    Which check is currently executing?
    What is its default severity?
    What effective configuration should it use?

StageContext / StageHealthContext
    What facts were extracted from the USD stage?

CheckResult
    What happened when one check evaluated the extracted facts?
---

## Reproducible Development and CI Environment

S-USDv separates service, desktop and hosted-CI dependencies:

```powershell
python -m pip install -r requirements-service.txt
python -m pip install -r requirements-desktop.txt
python -m pip install -r requirements-ci.txt
```

Use `requirements-desktop.txt` on a workstation that already provides the full OpenUSD runtime. Set `S_USDV_OPENUSD_ROOT` when the runtime is not discoverable automatically.

Use `requirements-ci.txt` in a clean hosted environment. It installs portable OpenUSD core bindings for validation and comparison tests; the embedded viewport remains an optional capability because `pxr.Usdviewq` is not part of that package.

Verify a clean environment with:

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
python scripts/ci/check_environment.py
python -m compileall -q s_usd_core s_usd_service s_usd_desktop
python -m pytest tests/service tests/desktop -v
```

See `docs/ci_environment.md` for the environment contract, isolated test-state variables and the boundary between portable CI tests and full workstation viewport tests.

---

## Continuous Integration

The GitHub Actions workflow in `.github/workflows/ci.yml` runs on every pushed branch, pull requests targeting `main`, and manual dispatches.

The hosted job uses Ubuntu and Python 3.12, installs the portable `usd-core` bindings, configures Qt for offscreen execution, verifies the environment, compiles the source packages, and runs the complete test suite:

```bash
python scripts/ci/run_tests.py tests -v
```

The hosted `usd-core` package provides the core OpenUSD APIs used by validation and comparison tests. `UsdImagingGL` and `Usdviewq` remain optional because the hosted job does not reproduce the complete workstation viewport runtime.
