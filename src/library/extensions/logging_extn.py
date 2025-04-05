import logging
import sys
import uuid
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from quart import Quart, g


def get_request_id() -> str:
    if getattr(g, "request_id", None):
        return g.request_id

    new_uuid = uuid.uuid4().hex[:10]
    g.request_id = new_uuid

    return new_uuid


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.req_id = get_request_id() if g.has_request_context() else ""
        return True


def _configure_logger_timezone(timezone: str) -> None:
    from datetime import datetime
    from time import struct_time

    import pytz

    timezone = pytz.timezone(timezone)

    def time_converter(seconds: Optional[float]) -> struct_time:
        if seconds is None:
            return datetime.now(tz=timezone).timetuple()
        return datetime.fromtimestamp(seconds, tz=timezone).timetuple()

    for handler in logging.root.handlers:
        if handler.formatter:
            handler.formatter.converter = time_converter


def configure_logger(app: Quart) -> None:
    log_file_ = app.config.get("LOG_FILE", None)
    log_lvl_ = app.config.get("LOG_LEVEL", "INFO")
    log_fmt_ = app.config.get("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    maxbytes_ = app.config.get("LOG_FILE_MAX_SIZE", 20)
    backup_count_ = app.config.get("LOG_FILE_BACKUP_COUNT", 5)
    datefmt_ = app.config.get("LOG_DATE_FORMAT", "")
    timezone_ = app.config.get("TIMEZONE", "UTC")
    log_handlers: list[logging.Handler] = []
    if log_file_:
        if not Path(log_file_).parent.is_dir():
            Path.mkdir(Path(log_file_).parent, parents=True, exist_ok=True)
        log_handlers.append(
            RotatingFileHandler(
                filename=log_file_,
                maxBytes=maxbytes_ * 1024 * 1024,
                backupCount=backup_count_,
            )
        )

    # Always add StreamHandler to log to console
    sh = logging.StreamHandler(sys.stdout)
    # sh.addFilter(RequestIdFilter())
    log_handlers.append(sh)

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.basicConfig(
        level=log_lvl_,
        format=log_fmt_,
        datefmt=datefmt_,
        handlers=log_handlers,
        force=True,
    )
    _configure_logger_timezone(timezone_)
