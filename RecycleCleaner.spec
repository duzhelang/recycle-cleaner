# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\SOLO\\回收站清理工具\\recycle_cleaner.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\SOLO\\回收站清理工具\\assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

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
    version='D:\\SOLO\\回收站清理工具\\version_info.txt',
    uac_admin=True,
)
