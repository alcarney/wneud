from __future__ import annotations

import logging
import pathlib
import typing

from PyQt6.QtCore import QAbstractListModel
from PyQt6.QtCore import QModelIndex
from PyQt6.QtCore import QObject
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtProperty
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtDBus import QDBusConnection
from PyQt6.QtDBus import QDBusInterface
from PyQt6.QtDBus import QDBusMessage
from PyQt6.QtQml import qmlRegisterType
from systemd import journal

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


class SDUnitListModel(QAbstractListModel):
    """A list model for systemd units."""

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.system_units: list[SDUnit] = []
        self.user_units: list[SDUnit] = []

        bus = QDBusConnection.sessionBus()
        if not bus.isConnected():
            raise RuntimeError("Unable to connection to dbus.")

        self.systemd = QDBusInterface(
            "org.freedesktop.systemd1",
            "/org/freedesktop/systemd1",
            interface="org.freedesktop.systemd1.Manager",
            connection=bus,
        )
        if not self.systemd.isValid():
            message = self.systemd.lastError().message()
            raise RuntimeError(f"Unable to connect to systemd: {message!r}")

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
        self.user_units.clear()
        self.system_units.clear()

        loaded_units = self.systemd.call("ListUnits")
        if loaded_units.type() == QDBusMessage.MessageType.ReplyMessage:
            for item in loaded_units.arguments()[0]:
                unit = {
                    "context": {
                        "ID": item[0],
                        "Description": item[1],
                        "Type": "",
                        "SourcePath": "",
                        "FragmentPath": "",
                    },
                    "runtime": {
                        "CanStart": False,
                        "CanStop": False,
                        "CanReload": False,
                    },
                }
                # self.user_units.append(SDUnit(unit))

        unit_files = self.systemd.call("ListUnitFiles")
        if unit_files.type() == QDBusMessage.MessageType.ReplyMessage:
            for item in unit_files.arguments()[0]:
                unit = {
                    "context": {
                        "ID": pathlib.Path(item[0]).name,
                        "Description": "",
                        "Type": "",
                        "SourcePath": item[0],
                        "FragmentPath": "",
                    },
                    "runtime": {
                        "CanStart": False,
                        "CanStop": False,
                        "CanReload": False,
                    },
                }
                # It might seem strange to talk about 'system' units since we're connected
                # to the user systemd instance however, there are many system services
                # running in the user instance that we probably should leave well alone.
                #
                # So for our purposes a 'user' unit is one that lives in .config/systemd/user
                # as it's most likely been set up by us or the user independently.
                source = item[0]
                # self.logger.debug("%s (%s)", unit.name, source)
                if source is not None and ".config/systemd" in source:
                    self.user_units.append(SDUnit(unit))
                else:
                    self.system_units.append(SDUnit(unit))


@typing.final
class SDUnit(QObject):
    """Represents a systemd unit"""

    def __init__(
        self,
        item: VarlinkUnit,
        parent=None,
    ):
        super().__init__(parent)
        self._item = item

    @pyqtProperty(str, constant=True)
    def name(self):
        return self._item["context"]["ID"]

    @pyqtProperty(str, constant=True)
    def description(self):
        return self._item["context"].get("Description", "")

    @pyqtProperty(str, constant=True)
    def unitType(self):
        return self._item["context"]["Type"]

    @pyqtProperty(bool, constant=True)
    def canStart(self):
        return self._item["runtime"]["CanStart"]

    @pyqtProperty(bool, constant=True)
    def canStop(self):
        return self._item["runtime"]["CanStop"]

    @pyqtProperty(bool, constant=True)
    def canReload(self):
        return self._item["runtime"]["CanReload"]

    @property
    def sourcePath(self):
        return self._item["context"].get("SourcePath")

    @property
    def fragmentPath(self):
        return self._item["context"].get("FragmentPath")

    @pyqtSlot()
    def start(self):
        print(f"Start {self.name!r}")

    @pyqtSlot()
    def restart(self):
        print(f"Restarting {self.name!r}")

    @pyqtSlot()
    def stop(self):
        print(f"Stopping {self.name!r}")


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
