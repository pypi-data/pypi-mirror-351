from __future__ import annotations
from typing import Optional


class TimeZone():
    """
    TimeZone, e.g. CEST, Europe/Berlin, UTC+4.


    Attributes
    ----------
    zone_id : string
        ID of the time zone.
    offset : str
        Offset to UTC, e.g. "+1400"
    display_name : string
        A human-friendly name of the time zone:
    """

    def __init__(self, zone_id: Optional[str], offset: Optional[str], display_name: str):
        self.zone_id = zone_id
        self.offset = offset
        self.display_name = display_name
