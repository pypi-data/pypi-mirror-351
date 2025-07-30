"""This file defines a logger used to send logs to the turing task manager.
Those logs are then sent to some kind of UI monitoring processes.
"""

# ───────────────────────────────── imports ────────────────────────────────── #
# Standard Library
import json
from logging import Formatter, LogRecord, Logger, FileHandler
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────── #
from pathlib import Path

LOG_FILE_NAME = ".log"


class TTMLogFormatter(Formatter):
    """File-specific formatter to log messages to the frontend. Uses json format
    to add context to logs, then dumps those to a single line of string.
    """

    def format(self, record: LogRecord):
        """Format the specified record as text. We want to log those events as
        a one-line json string.

        Args:
            record:
                A LogRecord instance representing an event being logged.

        Returns:
            text_log (str):
                A one line json string

        """
        return json.dumps(
            {
                "timestamp": datetime.utcfromtimestamp(record.created).isoformat(),
                "level": record.levelname.lower().strip(),
                "message": record.getMessage(),
            }
        )


def add_ttm_handler(logger: Logger, output_folder: Path):
    """Adds a handler to the given logger that sends the logs to the Frontend
    through asynchronous notifications.

    This handler is dependent on turing-task-manager, and only makes sense to
    use if the code will be handled in a worker using turing task manager.

    Args:
        logger (Logger):
            Instance of the Logger class representing a single logging channel.
        output_folder (Path):
            The Path of the output folder
    """
    log_path = output_folder / LOG_FILE_NAME

    if log_path.exists():
        with open(log_path, "r+") as f:
            f.truncate(0)

    fileHandler = FileHandler(log_path, mode="a+")
    fileHandler.setFormatter(TTMLogFormatter())

    logger.addHandler(fileHandler)
