from __future__ import annotations

import logging
import pathlib
import typing

from PyQt6.QtCore import QObject
from PyQt6.QtCore import pyqtProperty
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import pyqtSlot

if typing.TYPE_CHECKING:
    from wneud.services import SystemDService


class Unit(QObject):
    """Base unit class."""

    DBUS_IFACES = [
        "org.freedesktop.systemd1.Unit",
    ]

    propsChanged = pyqtSignal()

    def __init__(
        self,
        unit: dict[str, str],
        parent=None,
        systemd: SystemDService | None = None,
    ):
        super().__init__(parent)
        self._unit = unit
        self._systemd = systemd
        self.logger = logging.getLogger(self.__class__.__name__)

    @pyqtProperty(str, constant=True)
    def id(self):
        return self._unit["ID"]

    @pyqtProperty(str, constant=True)
    def name(self):
        return self._unit["ID"].split(".")[0]

    @pyqtProperty(str, notify=propsChanged)
    def description(self):
        return self._unit.get("Description", "")

    @description.setter
    def description(self, value):
        if self._unit.get("Description", "") != value:
            self._unit["Description"] = value
            self.propsChanged.emit()

    @pyqtProperty(str, constant=True)
    def unitType(self):
        return self._unit["Type"]

    @pyqtProperty(str, notify=propsChanged)
    def activeState(self):
        return self._unit.get("ActiveState", "")

    @activeState.setter
    def activeState(self, value):
        if self._unit.get("ActiveState", "") != value:
            self._unit["ActiveState"] = value
            self.propsChanged.emit()

    @pyqtProperty(bool, notify=propsChanged)
    def canStart(self):
        return self._unit.get("CanStart", False)

    @pyqtProperty(bool, notify=propsChanged)
    def canReload(self):
        return self._unit.get("CanReload", False)

    @pyqtProperty(bool, notify=propsChanged)
    def canStop(self):
        return self._unit.get("CanStop", False)

    @pyqtProperty(str, notify=propsChanged)
    def objectPath(self):
        return self._unit.get("ObjectPath", "")

    @objectPath.setter
    def objectPath(self, value):
        if self._unit.get("ObjectPath", "") != value:
            self._unit["ObjectPath"] = value
            self.propsChanged.emit()

    @pyqtProperty(str, constant=True)
    def fragmentPath(self):
        return self._unit.get("FragmentPath", "")

    @pyqtSlot()
    def start(self):
        """Start the unit."""
        self._systemd.start_unit(self.id)
        self.refresh()

    @pyqtSlot()
    def stop(self):
        """Start the unit."""
        self._systemd.stop_unit(self.id)
        self.refresh()

    @pyqtSlot()
    def refresh(self):
        if self.objectPath == "" and self.fragmentPath != "":
            if (object_path := self._systemd.load_unit(self.id)) is not None:
                self.objectPath = object_path
            else:
                self.logger.warning(
                    "Unable to refresh unit %r, missing object path", self.id
                )
                return

        for iface in self.DBUS_IFACES:
            properties = self._systemd.get_iface_properties(self.objectPath, iface)
            for prop, value in (properties or {}).items():
                # self.logger.debug("%s: %s", prop, value)
                self._unit[prop] = value

        self.propsChanged.emit()

    @classmethod
    def from_filepath(
        cls, path: str, status: str, systemd: SystemDService | None = None
    ):
        """Return a unit instance from its filepath"""
        unit_path = pathlib.Path(path)
        data = {
            "ID": unit_path.name,
            "Type": unit_path.suffix[1:],
            "FragmentPath": str(unit_path),
        }

        match data["Type"]:
            case "path":
                return PathUnit(data, systemd=systemd)
            case _:
                return cls(data, systemd=systemd)


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
