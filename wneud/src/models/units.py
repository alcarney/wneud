from __future__ import annotations

import pathlib
import typing

from PyQt6.QtCore import QObject
from PyQt6.QtCore import pyqtProperty
from PyQt6.QtCore import pyqtSignal

if typing.TYPE_CHECKING:
    from typing import Any


class Unit(QObject):
    """Base unit class."""

    descriptionChanged = pyqtSignal()

    def __init__(
        self,
        unit: dict[str, str],
        parent=None,
    ):
        super().__init__(parent)
        self._unit = unit

    @pyqtProperty(str, constant=True)
    def id(self):
        return self._unit["ID"]

    @pyqtProperty(str, constant=True)
    def name(self):
        return self._unit["ID"].split(".")[0]

    @pyqtProperty(str, notify=descriptionChanged)
    def description(self):
        return self._unit.get("Description", "")

    @description.setter
    def description(self, value):
        if self._unit.get("Description", "") != value:
            self._unit["Description"] = value
            self.descriptionChanged.emit()

    @pyqtProperty(str, constant=True)
    def unitType(self):
        return self._unit["Type"]

    @pyqtProperty(bool, constant=True)
    def canStart(self):
        return self._unit.get("CanStart", False)

    @pyqtProperty(bool, constant=True)
    def canReload(self):
        return self._unit.get("CanReload", False)

    @pyqtProperty(bool, constant=True)
    def canStop(self):
        return self._unit.get("CanStop", False)

    @pyqtProperty(str, constant=True)
    def fragmentPath(self):
        return self._unit.get("FragmentPath", "")

    @classmethod
    def from_filepath(cls, path: str, status: str):
        """Return a unit instance from its filepath"""
        unit_path = pathlib.Path(path)
        data = {
            "ID": unit_path.name,
            "Type": unit_path.suffix[1:],
            "FragmentPath": str(unit_path),
        }

        match data["Type"]:
            case "path":
                return PathUnit(data)
            case _:
                return cls(data)


class PathUnit(Unit):
    """Path unit class."""

    def __init__(
        self,
        unit: dict[str, str],
        parent=None,
    ):
        super().__init__(unit, parent)

    @pyqtProperty(str, constant=True)
    def unit(self):
        return self._unit.get("Unit", "")

    @pyqtProperty(str, constant=True)
    def makeDirectory(self):
        return self._unit.get("MakeDirectory", "")

    @pyqtProperty(str, constant=True)
    def directoryMode(self):
        return self._unit.get("DirectoryMode", "")

    @pyqtProperty(str, constant=True)
    def pathExists(self):
        return self._unit.get("PathExists", "")

    @pyqtProperty(str, constant=True)
    def pathExistsGlob(self):
        return self._unit.get("PathExistsGlob", "")

    @pyqtProperty(str, constant=True)
    def pathChanged(self):
        return self._unit.get("PathChanged", "")

    @pyqtProperty(str, constant=True)
    def pathModified(self):
        return self._unit.get("PathModified", "")

    @pyqtProperty(str, constant=True)
    def directoryNotEmpty(self):
        return self._unit.get("DirectoryNotEmpty", "")
