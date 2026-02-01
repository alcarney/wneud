from __future__ import annotations

import dataclasses
import logging
import typing

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt
from PySide6.QtQml import QmlElement

if typing.TYPE_CHECKING:
    from PySide6.QtCore import QByteArray, QObject, QPersistentModelIndex

    ModelIndex = QModelIndex | QPersistentModelIndex

ItemDataRole = Qt.ItemDataRole

QML_IMPORT_NAME = "WneudModels"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class SDUnitListModel(QAbstractListModel):
    """A list model for listing systemd units."""

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.units: list[SDUnit] = [
            SDUnit("Emacs", "Emacs server daemon", "service"),
            SDUnit("Another", "as said by Loki", "service"),
        ]
        self.logger.debug("Created model instance containing %s units", len(self.units))

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
        self.logger.debug("selected row: %s", item)

        if role in {ItemDataRole.DisplayRole, ItemDataRole.UserRole + 1}:
            return item.name

        if role == ItemDataRole.UserRole + 2:
            return item.description

        if role == ItemDataRole.UserRole + 3:
            return item.unitType

        self.logger.debug(".data() returning none")
        return None

    def headerData(self, section, orientation, role=ItemDataRole.DisplayRole):
        """Returns the appropriate header string depending on the orientation of
        the header and the section. If anything other than the display role is
        requested, we return an invalid variant."""
        self.logger.debug("headerData called")
        if role != ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return f"Column {section}"
        return f"Row {section}"

    @typing.override
    def rowCount(self, parent: ModelIndex = QModelIndex()):
        self.logger.debug("rowCount called")
        return len(self.units)

    @typing.override
    def roleNames(self):
        # TODO: do some dataclass introspection!
        self.logger.debug("roleNames called")
        roles: dict[int, QByteArray] = {
            **super().roleNames(),
            ItemDataRole.UserRole + 1: b"name",
            ItemDataRole.UserRole + 2: b"description",
            ItemDataRole.UserRole + 3: b"unitType",
        }
        return roles


@dataclasses.dataclass
class SDUnit:
    """Represents a systemd unit"""

    name: str
    description: str
    unitType: str
