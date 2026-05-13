from __future__ import annotations

import logging
import typing

from PyQt6.QtCore import QAbstractListModel
from PyQt6.QtCore import QModelIndex
from PyQt6.QtCore import QObject
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtProperty
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtDBus import QDBusMessage
from PyQt6.QtQml import qmlRegisterType
from systemd import journal

from wneud.services import SystemDService

from .units import Unit

if typing.TYPE_CHECKING:
    from PyQt6.QtCore import QByteArray
    from PyQt6.QtCore import QObject
    from PyQt6.QtCore import QPersistentModelIndex

    from .sd_types import JournalRecord

    ModelIndex = QModelIndex | QPersistentModelIndex

ItemDataRole = Qt.ItemDataRole

QML_IMPORT_NAME = "WneudModels"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@typing.final
class JournalLogModel(QAbstractListModel):
    """A list model for querying and displaying log messages."""

    MessageRole = ItemDataRole.UserRole + 1
    TimestampRole = ItemDataRole.UserRole + 2

    forUnitChanged = pyqtSignal()

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.messages: list[JournalRecord] = []

        self.reader = journal.Reader()
        self._for_unit: str = ""

    @typing.override
    def data(self, index: ModelIndex, /, role: int):
        if not index.isValid():
            self.logger.debug(".data() called with invalid index: %s", index)
            return None

        if (row := index.row()) > len(self.messages):
            self.logger.debug(
                "row %d is greater than unit list length (%d)", row, len(self.messages)
            )
            return None

        item = self.messages[row]
        # self.logger.debug("selected row: %s", item)

        if role in {ItemDataRole.DisplayRole, self.MessageRole}:
            return item["MESSAGE"]

        if role == self.TimestampRole:
            return f"{item['__REALTIME_TIMESTAMP']:%Y-%m-%d %H:%M:%S}"

        self.logger.debug(".data() returning none")
        return None

    @typing.override
    def rowCount(self, parent: ModelIndex = QModelIndex()):
        # self.logger.debug("rowCount called")
        return len(self.messages)

    @typing.override
    def roleNames(self):
        self.logger.debug("roleNames called")
        roles: dict[int, QByteArray] = {
            **super().roleNames(),
            self.MessageRole: b"message",
            self.TimestampRole: b"timestamp",
        }
        return roles

    def get_for_unit(self):
        return self._for_unit

    def set_for_unit(self, unit_name: str):
        self._for_unit = unit_name
        self.logger.debug("Unit Name: %r", unit_name)
        self.forUnitChanged.emit()
        self.reload_log()

    forUnit = pyqtProperty(
        str, fget=get_for_unit, fset=set_for_unit, notify=forUnitChanged
    )

    def reload_log(self):
        self.beginResetModel()
        self.logger.debug("reloading logs")
        self.messages.clear()

        # We want the equivalent of `journalctl --user -u unit.name -I`
        # where -I limits results to the latest invocation id.
        #
        # As far as I can tell, the only way to get this is to look at the latest message
        # to discover the invocation id to set as the filter.
        reader = journal.Reader()
        unit_filter = f"USER_UNIT={self._for_unit}"

        self.logger.debug("Unit filter: %r", unit_filter)
        reader.add_match(unit_filter)
        reader.seek_tail()

        entry = reader.get_previous()

        invocation_filter = f"_SYSTEMD_INVOCATION_ID={entry['USER_INVOCATION_ID']}"
        self.logger.debug("invocation filter: %r", invocation_filter)

        self.reader = journal.Reader()
        self.reader.add_match(invocation_filter)

        for entry in self.reader:
            # self.logger.debug("%s", entry)
            self.messages.append(entry)

        self.endResetModel()


@typing.final
class SDUnitListModel(QAbstractListModel):
    """A list model for systemd units."""

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.systemd = SystemDService(parent)
        self.system_units: list[Unit] = []
        self.user_units: list[Unit] = []
        self.unit_index: dict[str, Unit] = {}

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
            return item

        self.logger.debug(".data() returning none")
        return None

    @typing.override
    def rowCount(self, parent: ModelIndex = QModelIndex()):
        # self.logger.debug("rowCount called")
        return len(self.units)

    @typing.override
    def roleNames(self):
        # self.logger.debug("roleNames called")
        roles: dict[int, QByteArray] = {
            **super().roleNames(),
            ItemDataRole.UserRole + 1: b"item",
        }
        return roles

    def reload_units(self):
        """Reload list of units."""
        self.unit_index.clear()
        self.user_units.clear()
        self.system_units.clear()

        unit_files = self.systemd.list_unit_files()
        for path, status in unit_files:
            # self.logger.debug("UnitFile %s (%s)", path, status)
            unit = Unit.from_filepath(path, status, systemd=self.systemd)
            self.unit_index[unit.id] = unit

            # It might seem strange to talk about 'system' units since we're connected
            # to the user systemd instance however, there are many system services
            # running in the user instance that we probably should leave well alone.
            #
            # So for our purposes a 'user' unit is one that lives in .config/systemd/user
            # as it's most likely been set up by us or the user independently
            if ".config/systemd" in unit.fragmentPath:
                self.user_units.append(unit)
            else:
                self.system_units.append(unit)

        loaded_units = self.systemd.list_units()
        for item in loaded_units:
            self.logger.debug("UnitState: %s", item)

            (
                name,
                desc,
                load_state,
                active_state,
                state,
                _,
                obj_path,
                job_id,
                job_type,
                job_obj_path,
            ) = item

            if (unit := self.unit_index.get(name, None)) is None:
                # TODO: Handle transient units, e.g. those created via systemd-run
                self.logger.warning("Unknown unit: %s", name)
                continue

            unit.description = desc
            unit.objectPath = obj_path


qmlRegisterType(
    JournalLogModel,
    QML_IMPORT_NAME,
    QML_IMPORT_MAJOR_VERSION,
    QML_IMPORT_MINOR_VERSION,
    "JournalLogModel",
)
qmlRegisterType(
    SDUnitListModel,
    QML_IMPORT_NAME,
    QML_IMPORT_MAJOR_VERSION,
    QML_IMPORT_MINOR_VERSION,
    "SDUnitListModel",
)
