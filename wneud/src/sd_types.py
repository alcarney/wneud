from __future__ import annotations

import typing


class VarlinkUnit(typing.TypedDict, total=False):
    """Represents the varlink representation of a systemd unit.

    (Other fields may be present, this only represents the fields we currently use.)
    """

    ID: typing.Required[str]
    Type: typing.Required[str]

    Description: str
    SourcePath: str
    FragementPath: str
