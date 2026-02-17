from __future__ import annotations

import typing
from datetime import datetime


class JournalRecord(typing.TypedDict, total=False):
    """Represents a log record from the journal.

    see: man 7 systemd.journal-fields
    """

    # User fields
    MESSAGE: typing.Required[str]
    USER_INVOCATION_ID: typing.Required[str]

    # Trusted fields
    _SOURCE_REALTIME_TIMESTAMP: datetime

    # Address fields
    __REALTIME_TIMESTAMP: typing.Required[datetime]


class VarlinkUnit(typing.TypedDict, total=False):
    """Represents the varlink representation of a systemd unit.

    (Other fields may be present, this only represents the fields we currently use.)
    """

    ID: typing.Required[str]
    Type: typing.Required[str]

    Description: str
    SourcePath: str
    FragementPath: str
