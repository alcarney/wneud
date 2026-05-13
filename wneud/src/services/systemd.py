from __future__ import annotations

import logging
import typing

from PyQt6.QtCore import QObject
from PyQt6.QtDBus import QDBusConnection
from PyQt6.QtDBus import QDBusInterface
from PyQt6.QtDBus import QDBusMessage

if typing.TYPE_CHECKING:
    LoadedUnit = tuple[str, str, ...]  # TODO: complete this.
    UnitFile = tuple[str, str]


class SystemDService(QObject):
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)

        self._bus = QDBusConnection.sessionBus()
        if not self._bus.isConnected():
            raise RuntimeError("Unable to connection to dbus.")

        self._manager_iface = QDBusInterface(
            "org.freedesktop.systemd1",
            "/org/freedesktop/systemd1",
            interface="org.freedesktop.systemd1.Manager",
            connection=self._bus,
        )
        if not self._manager_iface.isValid():
            message = self._manager_iface.lastError().message()
            raise RuntimeError(f"Unable to connect to systemd: {message!r}")

    def _call_debus_method(
        self, service: str, object_path: str, iface_name: str, method: str, *args
    ):
        """Make a dbus call."""
        iface = QDBusInterface(service, object_path, iface_name, connection=self._bus)
        if not iface.isValid():
            self.logger.error(
                "dbus: %s %s %s: interface is not valid",
                service,
                object_path,
                iface_name,
            )
            return None

        self.logger.debug(
            "call: %s %s %s %s %r", service, object_path, iface_name, method, args
        )
        message = iface.call(method, *args)
        match message.type():
            case QDBusMessage.MessageType.ReplyMessage:
                result = message.arguments()
                self.logger.debug("reply: %s", result)
                return message.arguments()

            case QDBusMessage.MessageType.ErrorMessage:
                self.logger.error(
                    "error %s: %s", message.errorName(), message.errorMessage()
                )
                return None

            case _:
                self.logger.warning("Unknown message type: %s", message.type())
                return None

    def start_unit(self, unit_name: str, mode: str = "fail"):
        """Start the given unit name."""
        result = self._call_debus_method(
            "org.freedesktop.systemd1",
            "/org/freedesktop/systemd1",
            "org.freedesktop.systemd1.Manager",
            "StartUnit",
            unit_name,
            mode,
        )
        if result is not None:
            return result[0]

    def stop_unit(self, unit_name: str, mode: str = "fail"):
        """Stop the given unit name."""
        result = self._call_debus_method(
            "org.freedesktop.systemd1",
            "/org/freedesktop/systemd1",
            "org.freedesktop.systemd1.Manager",
            "StopUnit",
            unit_name,
            mode,
        )
        if result is not None:
            return result[0]

    def load_unit(self, unit_name: str):
        """Load the given unit name."""
        result = self._call_debus_method(
            "org.freedesktop.systemd1",
            "/org/freedesktop/systemd1",
            "org.freedesktop.systemd1.Manager",
            "LoadUnit",
            unit_name,
        )
        if result is not None:
            return result[0]

    def list_units(self) -> list[LoadedUnit]:
        """List loaded units."""
        message = self._manager_iface.call("ListUnits")
        if message.type() == QDBusMessage.MessageType.ReplyMessage:
            return message.arguments()[0]

        return []

    def list_unit_files(self) -> list[UnitFile]:
        """List unit files."""
        message = self._manager_iface.call("ListUnitFiles")
        if message.type() == QDBusMessage.MessageType.ReplyMessage:
            return message.arguments()[0]

        # TODO: error handling!
        return []

    def get_unit_properties(self, unit_path: str):
        """Get the set of generic unit properties."""
        props = self._call_debus_method(
            "org.freedesktop.systemd1",
            unit_path,
            "org.freedesktop.DBus.Properties",
            "GetAll",
            "org.freedesktop.systemd1.Unit",
        )
        if props is not None:
            return props[0]
