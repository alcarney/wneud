from __future__ import annotations

import pathlib
import typing

from .path import PathUnit
from .unit import Unit

if typing.TYPE_CHECKING:
    from wneud.services import SystemDService

__all__ = (
    "PathUnit",
    "Unit",
    "unit_from_filepath",
)


def unit_from_filepath(path: str, status: str, systemd: SystemDService | None = None):
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
            return Unit(data, systemd=systemd)
