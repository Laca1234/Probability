# Third-party notices

The Windows build bundles Python and native runtime components. Exact versions are pinned in `requirements-lock.txt`; the checked build uses Python 3.13.9, PySide6/Qt 6.11.1, NumPy 2.3.4, and PyInstaller 6.20.0.

- **Qt for Python / Qt / Shiboken**: PySide6, the selected Qt libraries and QML plugins, and Shiboken are offered under LGPLv3, GPLv2/GPLv3, or commercial terms depending on the component. Review the [Qt for Python license information](https://doc.qt.io/qtforpython-6/licenses.html) and [Qt licensing overview](https://doc.qt.io/qt-6/licensing.html) for the exact modules in the bundle.
- **NumPy**: BSD 3-Clause license. The bundled license text is in `licenses/NumPy-LICENSE.txt`.
- **PyInstaller bootloader**: GPLv2-or-later with the PyInstaller bootloader exception. The bundled license text is in `licenses/PyInstaller-COPYING.txt`.
- **Python runtime**: Python Software Foundation license. The build includes Python's license text when supplied with the selected Python installation.
- **Microsoft Visual C++ runtime**: redistributed runtime DLLs remain subject to Microsoft's applicable redistribution terms.
- **Teaching dataset**: the arbitrary sample values are CC0-1.0, as documented in `data/README.md`.
- **Application source**: MIT, in `licenses/LICENSE`.

The build uses dynamic Qt libraries. This notice is a component summary, not a substitute for the license texts, corresponding-source obligations, notices, or installation information required for redistribution. Verify the current terms for every bundled component before redistributing the application. The executable is not code-signed.
