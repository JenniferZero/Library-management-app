# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['library_manager.py'],
    pathex=[],
    binaries=[],
    datas=[('data', 'data'), ('en_core_web_sm-3.5.0', 'en_core_web_sm-3.5.0')],
    hiddenimports=['aiohttp', 'bs4', 'tkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=True,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [('v', None, 'OPTION')],
    name='LibraryManager',
    debug=True,
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
)
