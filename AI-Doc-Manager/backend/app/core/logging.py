import json
import logging
import os
from contextvars import ContextVar
from datetime import datetime, timezone


_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")
# Cloud Logging trace context — populated from the X-Cloud-Trace-Context header
# by the request middleware in app.main.
_trace_ctx: ContextVar[str] = ContextVar("trace", default="")


def set_request_id(request_id: str) -> None:
    _request_id_ctx.set(request_id)


def get_request_id() -> str:
    return _request_id_ctx.get()


def clear_request_id() -> None:
    _request_id_ctx.set("-")


def clear_trace_context() -> None:
    _trace_ctx.set("")


def set_trace_context(trace_header: str | None, project_id: str = "") -> None:
    """Parse ``X-Cloud-Trace-Context`` and store the full ``projects/...`` trace id.

    Cloud Run injects this header on incoming requests.  The value has the
    format ``TRACE_ID/SPAN_ID;o=TRACE_OPTIONS``.  We only need the trace id.

    When *project_id* is available, the trace is formatted as
    ``projects/{PROJECT}/traces/{TRACE_ID}`` so that Cloud Logging can
    correlate container logs with request logs.
    """
    if not trace_header:
        _trace_ctx.set("")
        return
    # The trace id is the first segment before any '/'.
    trace_id = trace_header.split("/", 1)[0].strip()
    if not trace_id:
        _trace_ctx.set("")
        return
    if project_id:
        _trace_ctx.set(f"projects/{project_id}/traces/{trace_id}")
    else:
        _trace_ctx.set(trace_id)


def get_trace_context() -> str:
    return _trace_ctx.get()


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class JsonFormatter(logging.Formatter):
    _reserved = {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
    }

    def __init__(self, project_id: str = ""):
        super().__init__()
        self._project_id = project_id

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "time": datetime.now(timezone.utc).isoformat(),
            # Cloud Logging looks for "severity" in jsonPayload and promotes it
            # to the log entry's severity level.  Using "level" would leave the
            # entry at its default (INFO) regardless of actual severity.
            "severity": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", get_request_id()),
            # Include source location so Cloud Logging can display file/line/func
            # even though the log was emitted as structured JSON.
            "logging.googleapis.com/sourceLocation": {
                "file": record.filename,
                "line": str(record.lineno),
                "function": record.funcName,
            },
        }

        # Request-log correlation: Cloud Logging matches container logs to
        # request logs via the trace id.
        trace = get_trace_context()
        if trace:
            payload["logging.googleapis.com/trace"] = trace

        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in self._reserved and not key.startswith("_")
        }
        payload.update(extras)

        # ── Exception / stack trace ──────────────────────────────────────
        # Error Reporting REQUIRES the stack trace to be in the ``message``
        # field (not a separate field).  If it's anywhere else, Error
        # Reporting won't detect it and exceptions will be invisible.
        if record.exc_info and record.exc_info[1] is not None:
            tb_text = self.formatException(record.exc_info)
            # Append traceback to message so Error Reporting can parse it.
            # Keep the original message as the first line for Logs Explorer.
            current_msg = str(payload["message"])
            payload["message"] = (
                f"{current_msg}\n{tb_text}" if current_msg.strip()
                else tb_text
            )
            # Also include a partial stack for the Logs Explorer JSON viewer.
            payload["stack_trace"] = tb_text

        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO", *, project_id: str = "") -> None:
    """Configure the root logger for Cloud Run structured JSON logging.

    Uses a custom ``JsonFormatter`` that writes single-line JSON to stdout.
    All special Cloud Logging fields (``severity``, ``message``,
    ``logging.googleapis.com/trace``, ``logging.googleapis.com/sourceLocation``)
    are populated automatically.  Exception stack traces are appended to the
    ``message`` field so that Error Reporting can parse them.

    Args:
        level:      Minimum log level (e.g. ``"INFO"``, ``"DEBUG"``).
        project_id: GCP project id used to construct full trace paths for
                    request-log correlation.  If omitted, only the bare
                    trace id is emitted.

    Alternative: ``google-cloud-logging`` StructuredLogHandler
        The google-cloud-logging library provides a ``StructuredLogHandler``
        that can replace the custom ``JsonFormatter``.  To switch, install
        the package and replace the handler setup::

            from google.cloud.logging_v2.handlers.structured_log import (
                StructuredLogHandler,
            )
            handler = StructuredLogHandler(project_id=project_id)
            handler.addFilter(RequestIdFilter())
            root_logger.addHandler(handler)

        The StructuredLogHandler automatically populates ``insertId`` for
        deduplication and ``httpRequest`` for request-log correlation when
        those fields are present on the log record.  The custom formatter is
        retained as the default because it has zero additional dependencies
        and gives full control over the JSON payload.
    """
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter(project_id=project_id))
    handler.addFilter(RequestIdFilter())
    root_logger.addHandler(handler)
    root_logger.setLevel(level.upper())
