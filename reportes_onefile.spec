# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File ONEFILE para Sistema de Reportes
Empaqueta TODO en un solo ejecutable autocontenido sin dependencias externas
"""

import os

block_cipher = None
base_dir = os.path.abspath(os.getcwd())

# Solo incluir el frontend compilado
datas = [
    ('dist', 'dist'),
]

a = Analysis(
    ['main.py'],
    pathex=[base_dir],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # Flask y extensiones
        'flask',
        'flask_cors',
        'flask_sqlalchemy',
        'werkzeug',
        'jinja2',
        'click',
        'itsdangerous',
        'markupsafe',

        # SQLAlchemy y MySQL
        'sqlalchemy',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.dialects.mysql',
        'mysql.connector',
        'greenlet',

        # Procesamiento de datos
        'pandas',
        'pandas.io.formats.style',
        'numpy',
        'numpy.core',
        'numpy.core.multiarray',

        # Excel (openpyxl)
        'openpyxl',
        'openpyxl.styles',
        'openpyxl.utils',
        'openpyxl.cell',
        'openpyxl.worksheet',
        'openpyxl.workbook',

        # PDF (reportlab)
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.pdfgen.canvas',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'reportlab.lib.colors',
        'reportlab.lib.units',
        'reportlab.lib.styles',
        'reportlab.lib.enums',
        'reportlab.platypus',
        'reportlab.pdfbase',
        'reportlab.pdfbase._fontdata',
        'reportlab.pdfbase.pdfmetrics',
        'reportlab.pdfbase.ttfonts',

        # Servidor waitress
        'waitress',
        'waitress.server',

        # Utilidades
        'dotenv',
        'python_dotenv',

        # pkg_resources y dependencias
        'pkg_resources',
        'pkg_resources.extern',
        'pkg_resources._vendor',
        'jaraco',
        'jaraco.text',
        'jaraco.functools',
        'jaraco.context',
        'jaraco.classes',
        'more_itertools',
        'zipp',
        'importlib_metadata',
        'importlib_resources',
        'platformdirs',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        '_tkinter',
        'matplotlib',
        'IPython',
        'notebook',
        'jupyter',
        'scipy',
        'pytest',
        'test',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SistemaReportes',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin consola - modo headless
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
