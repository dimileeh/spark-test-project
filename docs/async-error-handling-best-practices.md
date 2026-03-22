# Best Practices for Async Error Handling in Python FastAPI Applications

**Task:** task-e6de0131  
**Author:** Cody (Aira AI Agent)  
**Date:** 2026-03-22

---

## Table of Contents

1. [Introduction](#introduction)
2. [Structured Exception Hierarchies](#structured-exception-hierarchies)
3. [Middleware Patterns](#middleware-patterns)
4. [Retry Strategies for External APIs](#retry-strategies-for-external-apis)
5. [Structured Logging](#structured-logging)
6. [Putting It All Together](#putting-it-all-together)
7. [Summary Checklist](#summary-checklist)
8. [References](#references)

---

## Introduction

FastAPI is an ASGI framework built on Starlette. Every request handler is an `async` coroutine, which means error handling must account for both standard Python exceptions and asyncio-specific concerns (`CancelledError`, `TimeoutError`, task lifecycle).

Robust async error handling in FastAPI rests on four pillars:

1. A **structured exception hierarchy** that maps domain errors to HTTP semantics.
2. **Middleware patterns** that enforce consistent error shapes across every endpoint.
3. **Retry strategies** that make calls to external APIs resilient.
4. **Structured logging** that makes errors observable and traceable in production.

---

## Structured Exception Hierarchies

### Why Custom Exceptions?

Using bare `HTTPException` everywhere mixes HTTP semantics with business logic. Custom exceptions let you:

- Express intent clearly (`UserNotFoundError` vs. `HTTPException(404)`).
- Handle whole categories of errors in a single handler.
- Evolve HTTP status codes without changing business logic.

### Recommended Hierarchy

```python
# exceptions.py

class AppError(Exception):
    """Root of all application-defined exceptions.

    Every custom exception should inherit from here so a single
    catch-all handler can intercept any unhandled app error.
    """
    http_status: int = 500
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None, **context):
        self.message = message or self.__class__.message
        self.context = context  # arbitrary key/value for logs
        super().__init__(self.message)


# ── 4xx Client errors ──────────────────────────────────────────────────────
class ClientError(AppError):
    """Base for all errors caused by the client (4xx)."""
    http_status = 400
    error_code = "CLIENT_ERROR"


class ValidationError(ClientError):
    http_status = 422
    error_code = "VALIDATION_ERROR"
    message = "Request data failed validation."


class NotFoundError(ClientError):
    http_status = 404
    error_code = "NOT_FOUND"
    message = "The requested resource does not exist."


class AuthenticationError(ClientError):
    http_status = 401
    error_code = "UNAUTHENTICATED"
    message = "Authentication credentials are missing or invalid."


class AuthorizationError(ClientError):
    http_status = 403
    error_code = "FORBIDDEN"
    message = "You do not have permission to perform this action."


class ConflictError(ClientError):
    http_status = 409
    error_code = "CONFLICT"
    message = "The request conflicts with the current state of the resource."


class RateLimitError(ClientError):
    http_status = 429
    error_code = "RATE_LIMITED"
    message = "Too many requests. Please slow down."


# ── 5xx Server / infrastructure errors ────────────────────────────────────
class ServerError(AppError):
    """Base for all errors caused by server-side failures (5xx)."""
    http_status = 500
    error_code = "SERVER_ERROR"


class ExternalServiceError(ServerError):
    """An upstream API or service returned an error or timed out."""
    http_status = 502
    error_code = "EXTERNAL_SERVICE_ERROR"
    message = "An upstream service failed to respond correctly."


class DatabaseError(ServerError):
    http_status = 503
    error_code = "DATABASE_ERROR"
    message = "A database error occurred."
```

### Key Design Rules

| Rule | Rationale |
|---|---|
| Inherit from a single `AppError` root | One global handler can catch every custom error. |
| Keep `http_status` and `error_code` on the class | Status/code survive without an active request context. |
| Pass `**context` to exceptions | Structured log handlers can extract extra fields without string parsing. |
| Never catch `asyncio.CancelledError` without re-raising | It signals task cancellation; swallowing it causes hangs. |

```python
# ✅ Correct – always re-raise CancelledError
try:
    result = await some_coroutine()
except asyncio.CancelledError:
    logger.warning("Task was cancelled")
    raise  # mandatory

# ❌ Wrong – swallowing CancelledError causes the task to appear alive
except asyncio.CancelledError:
    pass
```

---

## Middleware Patterns

### Starlette's Exception Middleware Stack

Starlette (FastAPI's foundation) wraps every request through two middleware layers:

```
ServerErrorMiddleware   ← catches everything, returns 500
  └─ Installed Middleware
       └─ ExceptionMiddleware  ← catches HTTPException / registered handlers
            └─ Router → Endpoints
```

### Pattern 1 — Global Exception Handler (Recommended Starting Point)

Register handlers for your base exception classes so every endpoint automatically returns a consistent error envelope:

```python
# main.py
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from exceptions import AppError

app = FastAPI()


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Convert any AppError subclass to a uniform JSON error response."""
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Surface Pydantic validation errors in the standard envelope."""
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed.",
                "detail": exc.errors(),
            }
        },
    )
```

### Pattern 2 — Logging Middleware

A dedicated middleware logs every request and captures uncaught exceptions before they bubble to `ServerErrorMiddleware`:

```python
# middleware/logging.py
import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                "Unhandled exception",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                },
            )
            raise  # always re-raise to let Starlette's 500 handler respond
        else:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                },
            )
            response.headers["X-Request-ID"] = request_id
            return response


# Register in main.py
app.add_middleware(RequestLoggingMiddleware)
```

### Pattern 3 — Error-Normalising Middleware for Third-Party Libraries

Some libraries raise their own exceptions. A thin middleware catches and translates them:

```python
# middleware/error_normaliser.py
import httpx
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from exceptions import ExternalServiceError


class ErrorNormaliserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            return await call_next(request)
        except httpx.TimeoutException as exc:
            raise ExternalServiceError(
                "Upstream request timed out.", upstream=str(exc)
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise ExternalServiceError(
                f"Upstream returned {exc.response.status_code}.",
                upstream_status=exc.response.status_code,
            ) from exc
```

### Middleware Registration Order

```python
# Order matters — middleware is applied bottom-up for requests
app.add_middleware(ErrorNormaliserMiddleware)   # innermost (applied last)
app.add_middleware(RequestLoggingMiddleware)    # outermost (applied first)
```

---

## Retry Strategies for External APIs

### Principles

1. **Only retry idempotent operations** — GET, HEAD, PUT, DELETE are generally safe; POST/PATCH may not be.
2. **Use exponential back-off with jitter** — avoids thundering-herd problems.
3. **Set a hard cap on total attempts** — three to five retries cover most transient failures.
4. **Respect `Retry-After` headers** — honour the server's explicit back-off directive.
5. **Circuit-break on sustained failures** — stop hammering a service that is clearly down.

### Implementation with `tenacity`

[tenacity](https://tenacity.readthedocs.io/) is the de-facto standard retry library for Python and is fully async-compatible:

```python
# utils/retry.py
import asyncio
import logging
import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
    before_sleep_log,
    RetryError,
)

logger = logging.getLogger(__name__)

RETRYABLE = (
    httpx.TimeoutException,
    httpx.ConnectError,
    httpx.RemoteProtocolError,
)


def is_retryable_status(exc: BaseException) -> bool:
    """Retry on 429 (rate limited) and 5xx server errors."""
    return (
        isinstance(exc, httpx.HTTPStatusError)
        and exc.response.status_code in {429, 500, 502, 503, 504}
    )


@retry(
    retry=retry_if_exception_type(RETRYABLE) | retry_if_exception(is_retryable_status),
    stop=stop_after_attempt(4),
    wait=wait_exponential_jitter(initial=0.5, max=30, jitter=1),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
async def fetch_with_retry(client: httpx.AsyncClient, url: str, **kwargs) -> httpx.Response:
    """GET a URL with automatic exponential-backoff retries."""
    response = await client.get(url, **kwargs)
    response.raise_for_status()
    return response
```

### Respecting `Retry-After`

```python
import time


async def fetch_respecting_retry_after(
    client: httpx.AsyncClient, url: str, max_attempts: int = 4
) -> httpx.Response:
    for attempt in range(1, max_attempts + 1):
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429 and attempt < max_attempts:
                retry_after = float(
                    exc.response.headers.get("Retry-After", 2 ** attempt)
                )
                logger.warning(
                    "Rate limited; sleeping %.1fs (attempt %d/%d)",
                    retry_after, attempt, max_attempts,
                )
                await asyncio.sleep(retry_after)
            else:
                raise
    raise ExternalServiceError("Max retry attempts reached.", url=url)
```

### Circuit Breaker Pattern

Use [circuitbreaker](https://pypi.org/project/circuitbreaker/) or implement a lightweight version:

```python
# utils/circuit_breaker.py
import asyncio
import time
from enum import Enum


class State(Enum):
    CLOSED = "closed"       # normal operation
    OPEN = "open"           # rejecting calls
    HALF_OPEN = "half_open" # probing recovery


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._failures = 0
        self._state = State.CLOSED
        self._opened_at: float | None = None

    @property
    def state(self) -> State:
        if self._state is State.OPEN:
            if time.monotonic() - self._opened_at >= self.recovery_timeout:
                self._state = State.HALF_OPEN
        return self._state

    async def call(self, coro):
        if self.state is State.OPEN:
            raise ExternalServiceError("Circuit is open; upstream unavailable.")
        try:
            result = await coro
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            raise

    def _on_success(self):
        self._failures = 0
        self._state = State.CLOSED

    def _on_failure(self):
        self._failures += 1
        if self._failures >= self.failure_threshold:
            self._state = State.OPEN
            self._opened_at = time.monotonic()
```

---

## Structured Logging

### Why Structured Logging?

Plain-text log lines are hard to query at scale. Structured logging emits each log record as a JSON object, making it trivially filterable in tools like Loki, Elasticsearch, or CloudWatch Logs Insights.

### Setup with `python-json-logger`

```bash
pip install python-json-logger
```

```python
# logging_config.py
import logging
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
    # silence noisy third-party libraries
    "loggers": {
        "uvicorn.access": {"level": "WARNING"},
        "httpx": {"level": "WARNING"},
    },
}


def configure_logging() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)
```

### Binding Request Context

Use Python's `contextvars` to propagate a `request_id` to every log record emitted inside a request lifecycle — without threading or passing it manually:

```python
# context.py
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


# middleware/logging.py (updated)
import uuid
from context import request_id_var

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        token = request_id_var.set(request_id)
        try:
            return await call_next(request)
        finally:
            request_id_var.reset(token)


# A logging Filter that injects the request_id into every record
class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True
```

Add the filter to the handler in `LOGGING_CONFIG`:

```python
"handlers": {
    "console": {
        "class": "logging.StreamHandler",
        "formatter": "json",
        "filters": ["request_id_filter"],
    }
},
"filters": {
    "request_id_filter": {
        "()": "logging_config.RequestIdFilter",
    }
},
```

### Logging Inside Exception Handlers

```python
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    log_method = logger.warning if exc.http_status < 500 else logger.error
    log_method(
        exc.message,
        extra={
            "error_code": exc.error_code,
            "http_status": exc.http_status,
            **exc.context,  # any extra fields passed at raise-site
        },
        exc_info=exc.http_status >= 500,  # include traceback only for 5xx
    )
    return JSONResponse(
        status_code=exc.http_status,
        content={"error": {"code": exc.error_code, "message": exc.message}},
    )
```

### Async-Safe Logging Conventions

| Convention | Why |
|---|---|
| Use `logger.exception()` inside `except` blocks | Automatically attaches the current traceback. |
| Never use `logging.basicConfig()` after app startup | It is not thread/task-safe once handlers are attached. |
| Avoid blocking I/O in log handlers | File handlers block the event loop; use `QueueHandler` + a background thread for file logging. |
| Log at the point of origin, not the re-raise site | Avoids duplicate log lines for the same error. |

```python
# ✅ Log once, at the origin
async def get_user(user_id: int) -> User:
    try:
        return await db.fetch_user(user_id)
    except DBConnectionError as exc:
        logger.error("Database connection failed", extra={"user_id": user_id})
        raise DatabaseError() from exc

# ❌ Avoid: logging again in the handler produces a duplicate line
@app.exception_handler(DatabaseError)
async def db_handler(request, exc):
    logger.error("DB error")  # already logged above
    ...
```

---

## Putting It All Together

A minimal but production-ready FastAPI app using all four pillars:

```python
# main.py
from fastapi import FastAPI
from exceptions import AppError, NotFoundError
from middleware.logging import RequestLoggingMiddleware
from middleware.error_normaliser import ErrorNormaliserMiddleware
from logging_config import configure_logging
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
import logging

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

# Middleware (applied outermost → innermost)
app.add_middleware(ErrorNormaliserMiddleware)
app.add_middleware(RequestLoggingMiddleware)


# Exception handlers
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    log_method = logger.warning if exc.http_status < 500 else logger.error
    log_method(exc.message, extra={"error_code": exc.error_code, **exc.context},
               exc_info=exc.http_status >= 500)
    return JSONResponse(
        status_code=exc.http_status,
        content={"error": {"code": exc.error_code, "message": exc.message}},
    )


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR", "message": "Validation failed.",
                            "detail": exc.errors()}},
    )


# Example endpoint
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await user_service.get(user_id)
    if user is None:
        raise NotFoundError(f"User {user_id} not found.", user_id=user_id)
    return user
```

---

## Summary Checklist

- [ ] Define a custom `AppError` root and domain-specific subclasses with `http_status` and `error_code`.
- [ ] Never swallow `asyncio.CancelledError` — always re-raise it.
- [ ] Register a global `@app.exception_handler(AppError)` that formats a consistent JSON error envelope.
- [ ] Add `RequestLoggingMiddleware` to log every request, its status code, and duration.
- [ ] Add `ErrorNormaliserMiddleware` to translate third-party exceptions into `AppError` subclasses.
- [ ] Use `tenacity` for async retry logic with exponential back-off and jitter.
- [ ] Honour `Retry-After` response headers when rate-limited.
- [ ] Wrap brittle external calls in a circuit breaker to prevent cascade failures.
- [ ] Configure `python-json-logger` (or equivalent) for structured JSON log output.
- [ ] Propagate `request_id` via `contextvars` so every log line is traceable.
- [ ] Log 4xx errors at `WARNING`, 5xx errors at `ERROR`; include tracebacks only for 5xx.
- [ ] Avoid blocking I/O in log handlers — use `QueueHandler` for file output.

---

## References

- [FastAPI — Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Starlette — Exceptions](https://www.starlette.io/exceptions/)
- [Python asyncio — Exceptions](https://docs.python.org/3/library/asyncio-exceptions.html)
- [tenacity documentation](https://tenacity.readthedocs.io/)
- [python-json-logger](https://github.com/madzak/python-json-logger)
- [Python logging — HOWTO](https://docs.python.org/3/howto/logging.html)
- [PEP 654 — Exception Groups and `except*`](https://peps.python.org/pep-0654/) _(Python 3.11+)_
