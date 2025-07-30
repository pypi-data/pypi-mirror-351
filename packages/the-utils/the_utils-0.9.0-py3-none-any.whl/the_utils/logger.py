"""Logger"""

import logging
from datetime import datetime


class PaddedLevelFormatter(logging.Formatter):
    """Formatter that supports microseconds in datefmt."""

    MAX_LEVEL_LENGTH = 8

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created)

        if datefmt:
            return dt.strftime(datefmt)

        return f"{dt.strftime('%Y-%m-%d %H:%M:%S')},{record.msecs:03d}"

    def format(self, record):
        record.levelname = record.levelname.ljust(self.MAX_LEVEL_LENGTH)
        return super().format(record)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = PaddedLevelFormatter(
    "[%(levelname)s %(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S.%f"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
