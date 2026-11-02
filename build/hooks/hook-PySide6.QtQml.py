"""Collect only the QML modules used by this application's interface."""

from pathlib import Path, PurePath

from PyInstaller.utils.hooks.qt import add_qt6_dependencies, pyside6_library_info


hiddenimports, binaries, datas = add_qt6_dependencies(__file__)

qml_source = Path(pyside6_library_info.location["QmlImportsPath"]).resolve()
qml_destination = PurePath(pyside6_library_info.qt_rel_dir) / "qml"


def destination_for(source: Path) -> PurePath:
    relative = source.relative_to(qml_source)
    if source.is_file():
        relative = relative.parent
    return qml_destination / relative


# The UI imports QtQuick, QtQuick.Controls, and QtQuick.Layouts. Keep their
# QML resources and plugin binaries, without collecting unrelated modules
# such as WebEngine, Qt Location, or Qt 3D.
for module_name in ("QtQml", "QtQuick"):
    module_root = qml_source / module_name
    if not module_root.is_dir():
        continue
    for qmldir_file in sorted(module_root.rglob("qmldir")):
        plugin_binaries, plugin_datas = pyside6_library_info._process_qml_plugin(qmldir_file)
        binaries.extend((str(path), str(destination_for(path))) for path in plugin_binaries)
        datas.extend((str(path), str(destination_for(path))) for path in plugin_datas)
