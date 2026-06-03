from __future__ import annotations

import logging
import typing

from PyQt6.QtCore import QAbstractListModel
from PyQt6.QtCore import QModelIndex
from PyQt6.QtCore import QObject
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtProperty
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import pyqtSlot

from .unit import Unit

if typing.TYPE_CHECKING:
    from PyQt6.QtCore import QByteArray
    from PyQt6.QtCore import QPersistentModelIndex

    from wneud.services import SystemDService

    ModelIndex = QModelIndex | QPersistentModelIndex


@typing.final
class PathTriggerModel(QAbstractListModel):
    """A list model for systemd path unit triggers."""

    PathTriggerRole = Qt.ItemDataRole.UserRole + 1
    PathRole = Qt.ItemDataRole.UserRole + 2
    TriggerRole = Qt.ItemDataRole.UserRole + 3

    def __init__(
        self, path_triggers: list[tuple[str, str]], parent: QObject | None = None
    ):
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.path_triggers: list[tuple[str, str]] = path_triggers

    @typing.override
    def data(self, index: ModelIndex, /, role: int):
        if not index.isValid():
            self.logger.debug(".data() called with invalid index: %s", index)
            return None

        if (row := index.row()) > len(self.path_triggers):
            self.logger.debug(
                "row %d is greater than unit list length (%d)",
                row,
                len(self.path_triggers),
            )
            return None

        item = self.path_triggers[row]
        # self.logger.debug("selected row: %s", item)

        if role in {Qt.ItemDataRole.DisplayRole, self.PathTriggerRole}:
            return item

        if role == self.PathRole:
            return item[1]

        if role == self.TriggerRole:
            return item[0]

        self.logger.debug(".data() returning none")
        return None

    @typing.override
    def rowCount(self, parent: ModelIndex = QModelIndex()):
        # self.logger.debug("rowCount called")
        return len(self.path_triggers)

    @typing.override
    def roleNames(self):
        # self.logger.debug("roleNames called")
        roles: dict[int, QByteArray] = {
            **super().roleNames(),
            self.PathTriggerRole: b"item",
            self.PathRole: b"path",
            self.TriggerRole: b"trigger",
        }
        return roles


class PathUnit(Unit):
    """Path unit class."""

    DBUS_IFACES = [
        *Unit.DBUS_IFACES,
        "org.freedesktop.systemd1.Path",
    ]

    propsChanged = pyqtSignal()

    def __init__(
        self, unit: dict[str, str], parent=None, systemd: SystemDService | None = None
    ):
        super().__init__(unit, parent, systemd=systemd)
        self._path_trigger_model: PathTriggerModel | None = None

    @pyqtProperty(str, constant=True)
    def unit(self):
        return self._unit.get("Unit", "")

    @pyqtProperty(str, constant=True)
    def makeDirectory(self):
        return self._unit.get("MakeDirectory", "")

    @pyqtProperty(str, constant=True)
    def directoryMode(self):
        return self._unit.get("DirectoryMode", "")

    @pyqtProperty(object, notify=propsChanged)
    def paths(self):
        return self._unit.get("Paths", [])

    @pyqtProperty(str, constant=True)
    def directoryNotEmpty(self):
        return self._unit.get("DirectoryNotEmpty", "")

    @pyqtProperty(QObject, constant=True)
    def pathTriggerModel(self):
        """Return a ListView compatible model for viewing and editing the list of
        path triggers."""
        self.logger.debug("Getting path model.")
        if self._path_trigger_model is None:
            self._path_trigger_model = PathTriggerModel(self.paths)

        return self._path_trigger_model
