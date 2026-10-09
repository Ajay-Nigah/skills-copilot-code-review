"""School-local calendar date helpers."""

import os
from datetime import date, datetime
from zoneinfo import ZoneInfo

SCHOOL_TIMEZONE = ZoneInfo(os.getenv("SCHOOL_TIMEZONE", "America/New_York"))


def school_today() -> date:
    return datetime.now(SCHOOL_TIMEZONE).date()
