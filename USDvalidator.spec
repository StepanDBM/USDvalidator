# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


PROJECT_ROOT = Path(__name__).resolve().parent

PXR_ROOT = Path(
    r"E:\Work\3D\my_3D\KANEDA\Projects\Scripting\USDs\Setup"
    r"\\python-usd-venv\Lib\site-packages\pxr"
)


# ---------------------------------------------------------------------------
# OpenUSD native Python extensions + DLLs
# ---------------------------------------------------------------------------

pxr_binaries = []

for native_file in PXR_ROOT.rglob("*"):
    if native_file.suffix.lower() not in {".pyd", ".dll"}:
        continue

    destination = str(native_file.parent.relative_to(PXR_ROOT.parent))

    pxr_binaries.append(
        (
            destination + "/" + native_file.name,
            str(native_file),
            "BINARY",
        )
    )

print("PXR native binaries:", len(pxr_binaries))

for entry in pxr_binaries:
    if entry[0].endswith("pxr/Tf/_tf.pyd") or entry[0].endswith("pxr\\Tf/_tf.pyd"):
        print("FOUND _tf.pyd:", entry)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

a = Analysis(
    ["main.py"],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

print("ANALYSIS binaries BEFORE OpenUSD:", len(a.binaries))


# Explicitly append OpenUSD native binaries after Analysis.
for destination, source, typecode in pxr_binaries:
    a.binaries.append(
        (destination, source, typecode)
    )

print("ANALYSIS binaries AFTER OpenUSD:", len(a.binaries))

for entry in a.binaries:
    if "_tf.pyd" in entry[0]:
        print("EXPLICIT _tf.pyd ENTRY:", entry)


# ---------------------------------------------------------------------------
# PYZ
# ---------------------------------------------------------------------------

pyz = PYZ(a.pure)


# ---------------------------------------------------------------------------
# EXE
# ---------------------------------------------------------------------------

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="USDvalidator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)


# ---------------------------------------------------------------------------
# COLLECT
# ---------------------------------------------------------------------------

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="USDvalidator",
)