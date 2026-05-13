from __future__ import annotations

import logging
import os
import pathlib
import signal
import sys
import typing

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine

from .models import register_models

if typing.TYPE_CHECKING:
    from collections.abc import Sequence


QML_IMPORT_NAME = "WneudModels"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


def main(args: Sequence[str] | None = None):
    logging.basicConfig(
        level=logging.DEBUG, format="[%(levelname)s][%(name)s]: %(message)s"
    )

    register_models(QML_IMPORT_NAME, QML_IMPORT_MAJOR_VERSION, QML_IMPORT_MINOR_VERSION)

    app = QGuiApplication(args or sys.argv)
    engine = QQmlApplicationEngine()

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    if not os.environ.get("QT_QUICK_CONTROLS_STYLE"):
        # requires: kf6-qqc2-desktop-style on fedora
        os.environ["QT_QUICK_CONTROLS_STYLE"] = "org.kde.desktop"

    if not (platform := os.environ.get("QT_QPA_PLATFORM")):
        os.environ["QT_QPA_PLATFORM"] = "wayland"
    else:
        print(f"Using plaform: {platform}")

    src = pathlib.Path(__file__).parent.resolve()
    main_qml = src / "qml/main.qml"

    engine.load(QUrl(main_qml.as_uri()))

    if len(engine.rootObjects()) == 0:
        sys.exit(1)

    sys.exit(app.exec())
