import logging
from app.utils.logger import get_logger, LOG_FILE


def test_get_logger_returns_logger():
    logger = get_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    # Should have at least two handlers: console and file
    handler_types = {type(h) for h in logger.handlers}
    from logging import StreamHandler
    from logging.handlers import TimedRotatingFileHandler

    assert StreamHandler in handler_types
    assert TimedRotatingFileHandler in handler_types


def test_logger_logs_to_file(tmp_path, monkeypatch):
    # Patch LOG_FILE to a temp location
    log_file = tmp_path / "test.log"
    monkeypatch.setattr("app.utils.logger.LOG_FILE", str(log_file))
    logger = get_logger("test_logger_file")
    test_message = "Hello, logger!"
    logger.info(test_message)
    # Flush file handler
    for handler in logger.handlers:
        if hasattr(handler, "flush"):
            handler.flush()
    with open(log_file, "r") as f:
        contents = f.read()
    assert test_message in contents
