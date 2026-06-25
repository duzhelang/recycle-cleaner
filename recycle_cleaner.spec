# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

block_cipher = None
base_dir = Path('.').resolve()
assets = base_dir / 'assets'
version_file = base_dir / 'version_info.txt'

datas = []
if assets.exists():
    datas.append((str(assets), 'assets'))

a = Analysis(
    ['recycle_cleaner.py'],
    pathex=[str(base_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='RecycleCleaner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(assets / 'logo.ico') if (assets / 'logo.ico').exists() else None,
    uac_admin=True,
    version=str(version_file) if version_file.exists() else None,
)
