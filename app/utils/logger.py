"""
Logger utility for GuildRoster.

Provides functions to configure and retrieve loggers with console and file handlers.
"""

import pathlib
import logging
import sys

from logging.handlers import TimedRotatingFileHandler
from uvicorn.logging import ColourizedFormatter

FORMATTER = logging.Formatter(
    "%(levelname)s | %(asctime)s | %(name)s | %(message)s"
)
LOG_FILE = "logs/app.log"


def get_console_handler():
    """
    Create and return a console log handler with colorized output.
    Returns:
        logging.StreamHandler: Configured console handler.
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        ColourizedFormatter(
            "{levelprefix:<8} | {asctime} | {name} | {message}",
            style="{",
            use_colors=True,
        )
    )
    return console_handler


def get_file_handler():
    """
    Create and return a file log handler with daily rotation.
    Ensures the logs directory exists.
    Returns:
        TimedRotatingFileHandler: Configured file handler.
    """
    logs_dir_path = pathlib.Path().resolve().joinpath("logs")
    if not logs_dir_path.exists():
        logs_dir_path.mkdir(exist_ok=True)
    file_handler = TimedRotatingFileHandler(
        LOG_FILE, when="midnight", backupCount=7
    )
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    """
    Return a configured logger instance with console and file handlers.
    Args:
        logger_name (str): Name of the logger (usually __name__).
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    logger.propagate = False
    return logger
