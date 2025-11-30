# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['galaxy_classifier_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('final_galaxy_classifier.h5', '.'),
        ('background.jpg', '.'),
        ('favicon.ico', '.'),
    ],
    hiddenimports=[
        'tensorflow',
        'tensorflow.python',
        'tensorflow.python.ops',
        'tensorflow.python.framework',
        'tensorflow.python.eager',
        'tensorflow.python.keras',
        'tensorflow.python.keras.applications',
        'tensorflow.python.keras.applications.efficientnet',
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'h5py',
        'h5py.defs',
        'h5py.utils',
        'h5py._proxy',
        'h5py._conv',
        'numpy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'IPython',
        'jupyter',
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
    name='GalaxyClassifier',
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
    icon='favicon.ico',
)
