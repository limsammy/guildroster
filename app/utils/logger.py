import pathlib
import logging
import sys

from logging.handlers import TimedRotatingFileHandler

from uvicorn.logging import ColourizedFormatter

FORMATTER = logging.Formatter("%(levelname)s | %(asctime)s | %(name)s | %(message)s")
LOG_FILE = "logs/app.log"


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    # console_handler.setFormatter(FORMATTER)
    console_handler.setFormatter(
        ColourizedFormatter("{levelprefix:<8} @ {name} : {message}", style="{", use_colors=True)
    )
    console_handler.setFormatter(
        ColourizedFormatter("{levelprefix:<8} | {asctime} | {name} | {message}", style="{", use_colors=True)
    )
    return console_handler


def get_file_handler():
    # create logs dir if does not exist
    logs_dir_path = pathlib.Path().resolve().joinpath("logs")
    if not logs_dir_path.exists():
        logs_dir_path.mkdir(exist_ok=True)
    file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", backupCount=7)
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    """Return a logger instance

    Configures base logging level to DEBUG and adds console and file handlers.

    Args:
        logger_name (str): Name of the logger. Should almost always be __name__

    Returns:
        [type]: [description]
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger
