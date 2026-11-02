# Windows build and release guide

## Supported build environment

Use Windows x64, Python 3.13, and the exact runtime pins in `requirements-lock.txt`. The checked development machine has PySide6 6.11.1 / Qt 6.11.1 and PyInstaller 6.20.0. Qt 6.11 supports Windows 10 version 1809 or later and Windows 11. The project spec includes the app QML file, the SVG icon, the synthetic CSV, and Qt Quick/QML module resources. PyInstaller's PySide6 hook collects Qt binaries and plugins; after building, verify those files in the output folder instead of assuming hook collection is complete.

The spec removes ICU-family DLLs from the collected binaries. Windows supplies the ICU C libraries used by this Qt build; a build host can expose an unrelated `icuuc.dll` on `PATH` (for example, from Poppler), and bundling it shadows the Windows library and breaks `QtCore` loading. Keep `icu*.dll` out of the package and verify that the output folder contains none. The Qt 6.11 Windows support floor is documented in the [Qt platform matrix](https://doc.qt.io/qt-6.11/windows.html); Microsoft documents the Windows ICU availability [here](https://learn.microsoft.com/en-us/windows/win32/intl/international-components-for-unicode--icu-).

## Build

From the repository root in a clean virtual environment:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --requirement requirements-lock.txt
py -m PyInstaller --noconfirm --clean build/probability_of_us.spec
```

The one-folder application should be at `dist\ProbabilityOfUs\ProbabilityOfUs.exe`. The app stores mutable data in LocalAppData, outside that folder. This project does not claim a successful build until the resulting artifact exists, starts, and passes the package checklist below.

After the packaged offscreen smoke check succeeds, stage user documentation, license notices, the build manifest, a ZIP archive, and SHA-256 sums:

```powershell
.\build\package_release.ps1 -SmokeTestPassed
```

The script expects `.venv\Scripts\python.exe` by default. Pass `-PythonExe` when the pinned environment is elsewhere. The ZIP contains the complete one-folder application plus user-facing documentation; do not distribute only the EXE.

## QML and Qt plugin checks

If startup reports a missing QML module, add only the relevant `PySide6/qml/<module>` directory to `datas` in the spec and rebuild. If the Qt platform plugin cannot load, inspect `dist\ProbabilityOfUs\_internal\PySide6\plugins\platforms` (or the corresponding directory emitted by the installed PyInstaller version). Do not copy Qt DLLs from an unrelated Qt installation into the package. Keep the build interpreter free of competing Qt bindings.

The source runtime uses `QQuickStyle.setStyle("Fusion")`. Verify the Fusion controls QML files, Qt Quick Controls templates, and Qt Quick Layouts at runtime. The PyInstaller hook behavior changes over time; review the hook output and the upstream [Qt for Python deployment guide](https://doc.qt.io/qtforpython-6/deployment/deployment-pyinstaller.html) after changing pinned Qt or PyInstaller versions.

## Release checklist

- [ ] Create the build from a clean virtual environment with pinned dependencies.
- [ ] Verify version resource, product name, icon, Qt plugins, QML, and teaching CSV.
- [ ] Launch the packaged executable under a clean Windows profile with no repository checkout available. The current artifact was smoke-tested on its build machine; clean-machine verification remains outstanding.
- [ ] Verify theme switching, analysis, recurrence, simulation cancel, scenario save/reload/delete, CSV import, and JSON/Markdown/CSV export.
- [ ] Verify offline startup and that no network requests occur.
- [ ] Check 100%, 150%, and 200% scaling, keyboard focus visibility, and a 1366×768 display.
- [ ] Run the mathematical tests and inspect the manifest hash and source fields.
- [ ] Generate a software bill of materials and scan dependencies for the release.
- [ ] Produce SHA-256 checksums for the built artifacts and retain the source revision/build environment manifest.
- [ ] Test install/uninstall and confirm LocalAppData is retained or removed according to the user's choice.
- [ ] Sign only if a legitimate signing certificate is available; otherwise state that the binary is unsigned.

## Qt and third-party licenses

PySide6/Qt has LGPLv3/GPLv3 and commercial licensing options, with some modules under different licenses. A compiled desktop distribution still must be reviewed for the obligations of the exact modules and package build. Read the official [Qt licensing overview](https://doc.qt.io/qt-6/licensing.html), [Qt for Python licensing information](https://doc.qt.io/qtforpython-6/licenses.html), and all bundled third-party notices. This guide is not legal advice. Do not redistribute a binary until the applicable licenses, notices, source/relinking obligations, and any commercial-use requirements have been reviewed.

The application source license is MIT. The synthetic teaching values are CC0-1.0. NumPy and PyInstaller have separate licenses and notices. A release should include a generated SBOM and the license texts for dependencies actually bundled in the build.

