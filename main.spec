# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for packaging the Flask backend
This creates a single executable that includes all dependencies
"""

import sys
import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect all dependencies
datas = [('.env', '.')]  # Include .env file
binaries = []
hiddenimports = [
    'waitress',
    'flask',
    'flask_cors',
    'sqlalchemy',
    'mysql.connector',
    'pymysql',
    'dotenv',
    'openpyxl',
    'pandas',
    'numpy'
]

# Collect data files from packages
tmp_ret = collect_all('flask')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('flask_cors')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('sqlalchemy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'test', 'unittest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed app (no console), True for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='electron/build/icon.ico' if os.path.exists('electron/build/icon.ico') else None
)
