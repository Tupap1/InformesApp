# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File para Sistema de Reportes
Empaqueta Flask + React en un solo ejecutable portable
"""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Directorio base del proyecto
block_cipher = None
base_dir = os.path.abspath(os.getcwd())

# Recolectar datos adicionales
datas = [
    # Frontend compilado (dist/)
    ('dist', 'dist'),
]

# Recolectar módulos ocultos necesarios
hiddenimports = [
    'flask',
    'flask_cors',
    'flask_sqlalchemy',
    'sqlalchemy',
    'sqlalchemy.sql.default_comparator',
    'mysql.connector',
    'mysql.connector.locales',
    'mysql.connector.locales.eng',
    'mysql.connector.plugins',
    'mysql.connector.plugins.mysql_native_password',
    'mysql.connector.plugins.caching_sha2_password',
    'mysql.connector.plugins.sha256_password',
    'mysql.connector.cursor',
    'mysql.connector.pooling',
    'pandas',
    'openpyxl',
    'reportlab',
    'reportlab.pdfgen',
    'reportlab.lib',
    'reportlab.lib.pagesizes',
    'reportlab.lib.colors',
    'reportlab.platypus',
    'reportlab.lib.styles',
    'reportlab.lib.units',
    'dotenv',
    'waitress',
    'logging',
    'reports',
    'server',
]

# Agregar submódulos de reportlab, openpyxl y mysql.connector
hiddenimports += collect_submodules('reportlab')
hiddenimports += collect_submodules('openpyxl')
hiddenimports += collect_submodules('mysql.connector')

# Recolectar archivos de datos de reportlab, openpyxl y mysql.connector
datas += collect_data_files('reportlab')
datas += collect_data_files('openpyxl')
datas += collect_data_files('mysql.connector')

a = Analysis(
    ['main.py'],
    pathex=[base_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'tkinter.test',
        '_tkinter',
        'test',
        'unittest',
        'pydoc',
        'pkg_resources',
        'setuptools',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SistemaReportes',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Sin consola - modo headless completo
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Puedes agregar un .ico aquí
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SistemaReportes',
)
