"""
test_logging_utils.py - Unit tests for logging_utils.configure_logger().

Run with:
    pytest test_logging_utils.py -v
"""

import logging
import os
import tempfile

import pytest

from logging_utils import configure_logger


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _clear_logger(name: str) -> None:
    """Remove a logger from the logging manager so tests start fresh."""
    logger = logging.getLogger(name)
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    logging.Logger.manager.loggerDict.pop(name, None)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestConfigureLoggerReturnValue:
    """configure_logger() must return a properly typed Logger."""

    def test_returns_logger_instance(self, tmp_path):
        name = "test.returns_logger"
        _clear_logger(name)
        logger = configure_logger(name, log_dir=str(tmp_path))
        assert isinstance(logger, logging.Logger)

    def test_logger_has_correct_name(self, tmp_path):
        name = "test.correct_name"
        _clear_logger(name)
        logger = configure_logger(name, log_dir=str(tmp_path))
        assert logger.name == name


class TestConfigureLoggerLevel:
    """The logger and its handlers must respect the requested level."""

    @pytest.mark.parametrize(
        "level",
        [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL],
    )
    def test_logger_level_set(self, tmp_path, level):
        name = f"test.level_{level}"
        _clear_logger(name)
        logger = configure_logger(name, level=level, log_dir=str(tmp_path))
        assert logger.level == level

    def test_handlers_level_set(self, tmp_path):
        name = "test.handler_level"
        _clear_logger(name)
        logger = configure_logger(name, level=logging.WARNING, log_dir=str(tmp_path))
        for handler in logger.handlers:
            assert handler.level == logging.WARNING


class TestConfigureLoggerHandlers:
    """Logger must have exactly one console handler and one file handler."""

    def test_has_two_handlers(self, tmp_path):
        name = "test.two_handlers"
        _clear_logger(name)
        logger = configure_logger(name, log_dir=str(tmp_path))
        assert len(logger.handlers) == 2

    def test_has_stream_handler(self, tmp_path):
        name = "test.stream_handler"
        _clear_logger(name)
        logger = configure_logger(name, log_dir=str(tmp_path))
        stream_handlers = [
            h for h in logger.handlers if isinstance(h, logging.StreamHandler)
            # RotatingFileHandler is a subclass of StreamHandler; exclude it.
            and type(h) is logging.StreamHandler
        ]
        assert len(stream_handlers) == 1

    def test_has_file_handler(self, tmp_path):
        name = "test.file_handler"
        _clear_logger(name)
        logger = configure_logger(name, log_dir=str(tmp_path))
        from logging.handlers import RotatingFileHandler
        file_handlers = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
        assert len(file_handlers) == 1


class TestConfigureLoggerFileCreation:
    """configure_logger() must create the log file in the expected location."""

    def test_log_file_created(self, tmp_path):
        name = "test.file_created"
        _clear_logger(name)
        configure_logger(name, log_dir=str(tmp_path))
        expected = tmp_path / f"{name}.log"
        assert expected.exists()

    def test_custom_log_file_name(self, tmp_path):
        name = "test.custom_filename"
        _clear_logger(name)
        configure_logger(name, log_file="custom.log", log_dir=str(tmp_path))
        expected = tmp_path / "custom.log"
        assert expected.exists()

    def test_log_dir_created_if_missing(self, tmp_path):
        name = "test.dir_creation"
        _clear_logger(name)
        nested = tmp_path / "a" / "b" / "c"
        configure_logger(name, log_dir=str(nested))
        assert nested.is_dir()


class TestConfigureLoggerOutput:
    """Messages emitted by the logger must appear in the log file."""

    def test_info_message_written_to_file(self, tmp_path):
        name = "test.info_output"
        _clear_logger(name)
        logger = configure_logger(name, level=logging.DEBUG, log_dir=str(tmp_path))
        logger.info("hello from test")
        # Flush and close to ensure the buffer is written.
        for handler in logger.handlers:
            handler.flush()
        log_file = tmp_path / f"{name}.log"
        content = log_file.read_text(encoding="utf-8")
        assert "hello from test" in content

    def test_debug_message_written_to_file(self, tmp_path):
        name = "test.debug_output"
        _clear_logger(name)
        logger = configure_logger(name, level=logging.DEBUG, log_dir=str(tmp_path))
        logger.debug("debug payload")
        for handler in logger.handlers:
            handler.flush()
        log_file = tmp_path / f"{name}.log"
        content = log_file.read_text(encoding="utf-8")
        assert "debug payload" in content

    def test_message_below_level_not_written(self, tmp_path):
        name = "test.filtered_output"
        _clear_logger(name)
        logger = configure_logger(name, level=logging.WARNING, log_dir=str(tmp_path))
        logger.debug("should be filtered")
        for handler in logger.handlers:
            handler.flush()
        log_file = tmp_path / f"{name}.log"
        content = log_file.read_text(encoding="utf-8")
        assert "should be filtered" not in content


class TestConfigureLoggerIdempotent:
    """Calling configure_logger() twice with the same name must not add extra handlers."""

    def test_no_duplicate_handlers_on_second_call(self, tmp_path):
        name = "test.idempotent"
        _clear_logger(name)
        configure_logger(name, log_dir=str(tmp_path))
        configure_logger(name, log_dir=str(tmp_path))
        logger = logging.getLogger(name)
        assert len(logger.handlers) == 2
