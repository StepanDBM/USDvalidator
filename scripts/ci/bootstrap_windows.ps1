param(
    [string]$BasePython = ""
)

$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$venv = Join-Path $root ".venv-ci"
$data = Join-Path $env:TEMP "s-usdv-ci"

if (-not $BasePython) {
    $projectPython = Join-Path $root ".venv\Scripts\python.exe"

    if (Test-Path $projectPython) {
        $BasePython = $projectPython
    } else {
        $BasePython = (Get-Command python -ErrorAction Stop).Source
    }
}

$BasePython = (Resolve-Path $BasePython).Path

Write-Host "Repository: $root"
Write-Host "Base Python: $BasePython"

$version = & $BasePython -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"

if ($LASTEXITCODE -ne 0) {
    throw "Could not execute the selected Python interpreter."
}

if ($version -ne "3.12") {
    throw (
        "S-USDv CI currently requires Python 3.12, but the selected " +
        "interpreter is Python $version. Pass -BasePython with the path " +
        "to a Python 3.12 executable."
    )
}

if (Test-Path $venv) {
    Remove-Item $venv -Recurse -Force
}

if (Test-Path $data) {
    Remove-Item $data -Recurse -Force
}

Set-Location $root

& $BasePython -m venv $venv

if ($LASTEXITCODE -ne 0) {
    throw "Failed to create the CI virtual environment."
}

$python = Join-Path $venv "Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "The CI Python executable was not created at $python."
}

& $python -m pip install --upgrade pip

if ($LASTEXITCODE -ne 0) {
    throw "Failed to upgrade pip."
}

& $python -m pip install -r requirements-desktop.txt

if ($LASTEXITCODE -ne 0) {
    throw "Failed to install desktop dependencies."
}

$env:QT_QPA_PLATFORM = "offscreen"
$env:S_USDV_DATA_ROOT = $data
$env:S_USDV_DATABASE_URL = "sqlite:///$($data.Replace('\', '/'))/s_usdv.db"
$env:S_USDV_STORAGE_ROOT = Join-Path $data "storage"
$env:S_USDV_TEMPORARY_ROOT = Join-Path $data "temp"

& $python scripts/ci/check_environment.py

if ($LASTEXITCODE -ne 0) {
    throw "Environment verification failed."
}

& $python -m compileall -q s_usd_core s_usd_service s_usd_desktop

if ($LASTEXITCODE -ne 0) {
    throw "Python compilation failed."
}

& $python scripts/ci/run_tests.py `
    tests/service `
    tests/desktop `
    -v

if ($LASTEXITCODE -ne 0) {
    throw "The test suite failed."
}

Write-Host ""
Write-Host "S-USDv clean Windows environment passed."