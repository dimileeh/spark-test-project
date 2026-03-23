# Spark Test Project

E2E test repo for Aira AI agent flows.

---

## Modules

### `logging_utils.py`

A logging utility module that provides a `configure_logger()` helper returning a Python
[`logging.Logger`](https://docs.python.org/3/library/logging.html#logging.Logger) pre-wired with
both a **console** (stderr) handler and a rotating **file** handler.

#### Function signature

```python
configure_logger(
    name: str,
    level: int = logging.DEBUG,
    log_file: str = None,       # defaults to "<name>.log"
    log_dir: str = "logs",
    max_bytes: int = 5_242_880, # 5 MB
    backup_count: int = 3,
    fmt: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt: str = "%Y-%m-%dT%H:%M:%S",
) -> logging.Logger
```

#### Parameters

| Parameter      | Type  | Default                                               | Description                                              |
|----------------|-------|-------------------------------------------------------|----------------------------------------------------------|
| `name`         | `str` | *(required)*                                          | Logger name. Use `__name__` for module-level loggers.    |
| `level`        | `int` | `logging.DEBUG`                                       | Minimum severity level for both handlers.                |
| `log_file`     | `str` | `"<name>.log"`                                        | Log file name (relative to `log_dir`).                   |
| `log_dir`      | `str` | `"logs"`                                              | Directory for the log file; created automatically.       |
| `max_bytes`    | `int` | `5_242_880`                                           | Max file size before rotation (bytes).                   |
| `backup_count` | `int` | `3`                                                   | Number of rotated backup files to keep.                  |
| `fmt`          | `str` | `"%(asctime)s [%(levelname)s] %(name)s: %(message)s"` | Log record format string.                                |
| `datefmt`      | `str` | `"%Y-%m-%dT%H:%M:%S"`                                 | Date/time format string used by the formatter.           |

#### Basic usage

```python
import logging
from logging_utils import configure_logger

logger = configure_logger("my_app", level=logging.INFO)

logger.info("Application started")
logger.warning("Low disk space")
logger.error("Failed to connect to database")
```

Console output (stderr):

```
2024-01-15T12:00:00 [INFO] my_app: Application started
2024-01-15T12:00:01 [WARNING] my_app: Low disk space
2024-01-15T12:00:02 [ERROR] my_app: Failed to connect to database
```

Log file created at `logs/my_app.log` with identical content.

#### Custom log directory and file

```python
logger = configure_logger(
    "data_pipeline",
    level=logging.DEBUG,
    log_file="pipeline.log",
    log_dir="/var/log/myapp",
)
logger.debug("Processing batch 42")
```

#### Module-level logger pattern

```python
# inside mymodule.py
import logging
from logging_utils import configure_logger

logger = configure_logger(__name__, level=logging.INFO)

def process(data):
    logger.info("Starting processing")
    # ...
    logger.debug("Processing details: %s", data)
```

#### Idempotent — safe to call multiple times

Calling `configure_logger()` with the same `name` more than once returns the existing logger
without adding duplicate handlers:

```python
logger_a = configure_logger("app")
logger_b = configure_logger("app")
assert logger_a is logger_b          # same object
assert len(logger_a.handlers) == 2   # still exactly 2 handlers
```

---

## Running Tests

```bash
# Install pytest if needed
pip install pytest

# Run all tests
pytest test_logging_utils.py -v
```

Expected output: **18 passed**.
