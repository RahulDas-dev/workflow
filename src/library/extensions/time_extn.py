import os
import time

from quart import Quart


def configure_timezone(app: Quart, default_timezone: str = "UTC") -> None:
    time_zone_ = app.config.get("TIMEZONE", default_timezone)
    os.environ["TZ"] = time_zone_
    if hasattr(time, "tzset") and os.name != "nt":
        time.tzset()
