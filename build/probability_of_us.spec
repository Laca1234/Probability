# PyInstaller one-folder specification. Build from the repository root.
from pathlib import Path
import sys
import PySide6
from PyInstaller.building.datastruct import TOC

ROOT = Path(SPECPATH).parent.resolve()
PYSIDE = Path(PySide6.__file__).resolve().parent
datas = [
    (str(ROOT / "src" / "probability_of_us" / "ui" / "qml" / "Main.qml"), "probability_of_us/ui/qml"),
    (str(ROOT / "src" / "probability_of_us" / "assets" / "app_icon.svg"), "probability_of_us/assets"),
    (str(ROOT / "src" / "probability_of_us" / "data" / "births_teaching_sample.csv"), "probability_of_us/data"),
    (str(ROOT / "docs" / "distribution_readme.md"), "."),
    (str(ROOT / "docs" / "user_guide.md"), "docs"),
    (str(ROOT / "docs" / "mathematical_model.md"), "docs"),
    (str(ROOT / "docs" / "data_sources.md"), "docs"),
    (str(ROOT / "docs" / "data_dictionary.md"), "docs"),
    (str(ROOT / "docs" / "privacy.md"), "docs"),
    (str(ROOT / "docs" / "limitations.md"), "docs"),
    (str(ROOT / "data" / "README.md"), "data"),
    (str(ROOT / "LICENSE"), "licenses"),
    (str(ROOT / "THIRD-PARTY-NOTICES.md"), "licenses"),
]
site_packages = PYSIDE.parent
license_files = [
    (site_packages / "numpy-2.3.4.dist-info" / "LICENSE.txt", "licenses/NumPy-LICENSE.txt"),
    (site_packages / "pyinstaller-6.20.0.dist-info" / "licenses" / "COPYING.txt", "licenses/PyInstaller-COPYING.txt"),
    (Path(sys.base_prefix) / "LICENSE.txt", "licenses/Python-LICENSE.txt"),
]
datas.extend((str(source), destination) for source, destination in license_files if source.is_file())

hiddenimports = [
    "PySide6.QtQml",
    "PySide6.QtQuick",
    "PySide6.QtQuickControls2",
    "PySide6.QtWidgets",
]

a = Analysis(
    [str(ROOT / "run_app.py")],
    pathex=[str(ROOT / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[str(ROOT / "build" / "hooks")],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "scipy", "pandas"],
    noarchive=False,
    optimize=1,
)
# Qt 6.11 uses the Windows ICU implementation. A build host may have an
# unrelated ICU DLL earlier on PATH (for example, the one shipped with
# Poppler); bundling that library can shadow Windows ICU and prevent QtCore
# from loading. Keep ICU-family DLLs out of the application bundle.
a.binaries = TOC(
    [
        entry
        for entry in a.binaries
        if not Path(entry[0]).name.lower().startswith("icu")
    ]
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ProbabilityOfUs",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon=str(ROOT / "build" / "probability_of_us.ico"),
    version=str(ROOT / "build" / "version_info.txt"),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="ProbabilityOfUs",
)
