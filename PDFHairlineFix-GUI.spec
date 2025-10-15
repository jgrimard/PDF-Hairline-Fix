# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Resolve tkdnd_path dynamically (relative/import-based)
import os
try:
    import tkinterdnd2
    # Derive the tkdnd runtime folder from the installed package location
    tkdnd_path = os.path.join(os.path.dirname(tkinterdnd2.__file__), "tkdnd", "win-x64")
    if not os.path.isdir(tkdnd_path):
        tkdnd_path = ""
except ImportError:
    tkdnd_path = ""  # tkinterdnd2 not installed; proceed without it

datas = []
if tkdnd_path:
    datas.append((tkdnd_path, "tkdnd2.9"))

from PyInstaller.utils.hooks import collect_submodules
hiddenimports = []
# hiddenimports += collect_submodules("tkinterdnd2")  # uncomment if needed

a = Analysis(
    ["PDF-hairline-fix-GUI.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
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
    name="PDFHairlineFix",
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon="app.ico",
)
