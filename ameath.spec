# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gifs', 'gifs'),
        ('fonts', 'fonts'),
        ('sound', 'sound'),
        ('version.txt', '.'),
    ],
    hiddenimports=[
        'pystray',
        'win32gui',
        'win32con',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'screeninfo',
        'numpy',
        'sounddevice',
        'soundfile',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ameath',
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
    icon='gifs/ameath.ico',
)
