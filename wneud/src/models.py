from __future__ import annotations

import dataclasses
import logging
import typing

import varlink
from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt
from PySide6.QtQml import QmlElement

if typing.TYPE_CHECKING:
    from PySide6.QtCore import QByteArray, QObject, QPersistentModelIndex

    from .sd_types import VarlinkUnit

    ModelIndex = QModelIndex | QPersistentModelIndex

ItemDataRole = Qt.ItemDataRole

QML_IMPORT_NAME = "WneudModels"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class SDUnitListModel(QAbstractListModel):
    """A list model for systemd units."""

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.system_units: list[SDUnit] = []
        self.user_units: list[SDUnit] = []

        self.reload_units()

    @property
    def units(self):
        # TODO: Filters for selecting other unit types?
        return self.user_units

    @typing.override
    def data(self, index: ModelIndex, /, role: int):
        if not index.isValid():
            self.logger.debug(".data() called with invalid index: %s", index)
            return None

        if (row := index.row()) > len(self.units):
            self.logger.debug(
                "row %d is greater than unit list length (%d)", row, len(self.units)
            )
            return None

        item = self.units[row]
        # self.logger.debug("selected row: %s", item)

        if role in {ItemDataRole.DisplayRole, ItemDataRole.UserRole + 1}:
            return item.name

        if role == ItemDataRole.UserRole + 2:
            return item.description

        if role == ItemDataRole.UserRole + 3:
            return item.unitType

        self.logger.debug(".data() returning none")
        return None

    @typing.override
    def rowCount(self, parent: ModelIndex = QModelIndex()):
        # self.logger.debug("rowCount called")
        return len(self.units)

    @typing.override
    def roleNames(self):
        # TODO: do some dataclass introspection!
        # self.logger.debug("roleNames called")
        roles: dict[int, QByteArray] = {
            **super().roleNames(),
            ItemDataRole.UserRole + 1: b"name",
            ItemDataRole.UserRole + 2: b"description",
            ItemDataRole.UserRole + 3: b"unitType",
        }
        return roles

    def reload_units(self):
        """Reload list of units."""
        self.user_units.clear()
        self.system_units.clear()

        with varlink.Client("unix:/run/user/1000/systemd/io.systemd.Manager") as client:
            with client.open("io.systemd.Unit") as connection:
                for item in connection.List(_more=True):
                    unit = SDUnit.from_varlink(item["context"])

                    # It might seem strange to talk about 'system' units since we're connected
                    # to the user systemd instance however, there are many system services
                    # running in the user instance that we probably should leave well alone.
                    #
                    # So for our purposes a 'user' unit is one that lives in .config/systemd/user
                    # as it's most likely been set up by us or the user independently.
                    source = unit.sourcePath or unit.fragmentPath
                    if source is not None and ".config/systemd" in source:
                        self.user_units.append(unit)

                    else:
                        self.system_units.append(unit)


@dataclasses.dataclass
class SDUnit:
    """Represents a systemd unit"""

    name: str
    description: str | None
    unitType: str

    sourcePath: str | None
    fragmentPath: str | None

    @classmethod
    def from_varlink(cls, item: VarlinkUnit):
        """Create an instance from the varlink representation"""

        return cls(
            name=item["ID"],
            description=item.get("Description"),
            unitType=item["Type"],
            sourcePath=item.get("SourcePath"),
            fragmentPath=item.get("FragmentPath"),
        )
