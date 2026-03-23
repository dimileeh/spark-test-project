"""
logging_utils.py - Logging utility module for Spark Test Project.

Provides a configure_logger() function that returns a Python logger
with both console and file handlers pre-configured.
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def configure_logger(
    name: str,
    level: int = logging.DEBUG,
    log_file: str = None,
    log_dir: str = "logs",
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
    fmt: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt: str = "%Y-%m-%dT%H:%M:%S",
) -> logging.Logger:
    """
    Create and return a configured Python logger with console and file handlers.

    Args:
        name:         Logger name (typically __name__ of the calling module).
        level:        Logging level (e.g. logging.DEBUG, logging.INFO).
                      Defaults to logging.DEBUG.
        log_file:     Name of the log file. Defaults to ``<name>.log``.
        log_dir:      Directory in which to create the log file.
                      Defaults to ``"logs"``.
        max_bytes:    Maximum size of a single log file before rotation.
                      Defaults to 5 MB.
        backup_count: Number of rotated backup files to keep. Defaults to 3.
        fmt:          Log record format string.
        datefmt:      Date/time format string for the formatter.

    Returns:
        A :class:`logging.Logger` instance with:
        - A ``StreamHandler`` writing to *stderr* at *level*.
        - A ``RotatingFileHandler`` writing to ``<log_dir>/<log_file>``.

    Example::

        import logging
        from logging_utils import configure_logger

        logger = configure_logger("my_app", level=logging.INFO)
        logger.info("Application started")
    """
    if log_file is None:
        log_file = f"{name}.log"

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers if the logger was already configured.
    if logger.handlers:
        return logger

    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    # --- Console handler ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # --- File handler ---
    os.makedirs(log_dir, exist_ok=True)
    file_path = os.path.join(log_dir, log_file)
    file_handler = RotatingFileHandler(
        file_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
