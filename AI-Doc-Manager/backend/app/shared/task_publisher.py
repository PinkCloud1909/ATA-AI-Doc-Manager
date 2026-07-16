"""Cloud Tasks for async RAG ingestion.

This module is the single place that knows how to enqueue a Cloud Tasks HTTP
target task aimed at the internal worker endpoint.

Design
------
- The worker endpoint is ``POST /api/v1/rag/worker/{document_id}``.
- Tasks carry the document_id in the URL; no request body is required.
- OIDC authentication is used so only Cloud Tasks (with the right service
  account) can call the worker endpoint.
- **Idempotency**: Task names are derived from ``document_id`` so that
  re-enqueuing the same document overwrites the pending task (Cloud Tasks
  returns ``ALREADY_EXISTS`` → we catch it and return the existing task name).
  This prevents duplicate ingestion of the same document when the
  ``CreateTask`` call is retried due to a transient network error.

Local development
-----------------
This module is only called from the router when the queue name is configured
(see ``is_async_mode()``).  In local Docker Compose the queue name is not set,
so the router falls back to synchronous in-process ingestion.

Failure handling
----------------
If ``create_task`` raises (other than ``AlreadyExists``), the exception
propagates up to the router which returns a 500.  The document is NOT marked
as ``COMPLETED``, so the caller can retry.

Required IAM
------------
+---------------------------------------------------+----------------------------------+
| Principal                                         | Role                             |
+===================================================+==================================+
| Backend SA (dms-backend-sa)                       | ``roles/cloudtasks.enqueuer``    |
+---------------------------------------------------+----------------------------------+
| Backend SA on Tasks SA (dms-tasks-sa)             | ``roles/iam.serviceAccountUser`` |
| (allows the backend to create OIDC-authenticated  |                                  |
| tasks that impersonate the Tasks SA)              |                                  |
+---------------------------------------------------+----------------------------------+
| Tasks SA (dms-tasks-sa) on Cloud Run service      | ``roles/run.invoker``            |
+---------------------------------------------------+----------------------------------+
"""

from __future__ import annotations

import logging
import threading
from typing import Any

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level cached Cloud Tasks client — creating a new gRPC channel per
# enqueue is wasteful.  Protected by a lock for thread safety.
# ---------------------------------------------------------------------------
_tasks_client: Any = None
_tasks_client_lock = threading.Lock()

# Cloud Tasks task names may contain letters, numbers, and hyphens.
# This prefix makes task names human-readable in logs and the Cloud Console.
_TASK_NAME_PREFIX = "rag-ingest"


def _get_tasks_client() -> Any:
    """Return a cached CloudTasksClient, creating it once on first access."""
    global _tasks_client
    if _tasks_client is None:
        with _tasks_client_lock:
            if _tasks_client is None:  # double-checked locking
                from google.cloud import tasks_v2  # noqa: PLC0415

                _tasks_client = tasks_v2.CloudTasksClient()
    return _tasks_client


def is_async_mode(settings: Settings | None = None) -> bool:
    """Return ``True`` when Cloud Tasks async mode is active.

    Async mode requires all three conditions to be met:
    - ``ENVIRONMENT`` is ``production`` or ``prod``
    - ``CLOUD_TASKS_QUEUE_NAME`` is set
    - ``WORKER_SERVICE_URL`` is set

    A partial config falls back to sync mode so a misconfigured environment
    fails loudly at task-enqueue time rather than silently skipping work.
    """
    s = settings or get_settings()
    _PROD_ENVS = {"production", "prod"}
    return bool(
        s.environment.lower() in _PROD_ENVS
        and s.cloud_tasks_queue_name
        and s.worker_service_url
    )


def enqueue_rag_ingestion_task(
    document_id: str,
    force: bool = False,
    settings: Settings | None = None,
) -> str:
    """Enqueue a RAG ingestion task for *document_id* on the Cloud Tasks queue.

    Args:
        document_id: UUID string of the document to ingest.
        force:       If ``True``, re-ingest even if already completed.
        settings:    Optional ``Settings`` override (defaults to ``get_settings()``).

    Returns:
        The Cloud Tasks task name (full resource path).

    Raises:
        RuntimeError: If required config fields are missing.
        google.api_core.exceptions.GoogleAPICallError: On non-retryable API
            failure.  ``AlreadyExists`` (409) is handled internally — it
            means a task for this document already exists on the queue and
            the caller receives the existing task name.
    """
    s = settings or get_settings()

    # ── Config pre-flight checks ──────────────────────────────────────
    if not s.cloud_tasks_queue_name:
        raise RuntimeError("CLOUD_TASKS_QUEUE_NAME is not configured")
    if not s.worker_service_url:
        raise RuntimeError("WORKER_SERVICE_URL is not configured")
    if not s.gcp_project_id:
        raise RuntimeError("GCP_PROJECT_ID is not configured")
    if not s.cloud_run_sa_email:
        raise RuntimeError(
            "CLOUD_RUN_SA_EMAIL must be set in production so Cloud Tasks "
            "can attach an OIDC token to worker requests. Without it, the "
            "worker endpoint cannot verify the caller identity."
        )

    from google.api_core import exceptions as gcp_exceptions  # noqa: PLC0415
    from google.cloud import tasks_v2  # noqa: PLC0415

    client = _get_tasks_client()
    parent = client.queue_path(
        s.gcp_project_id,
        s.cloud_tasks_location,
        s.cloud_tasks_queue_name,
    )

    # ── Construct the worker URL ──────────────────────────────────────
    worker_url = (
        f"{s.worker_service_url.rstrip('/')}"
        f"/api/v1/rag/worker/{document_id}"
        f"?force={str(force).lower()}"
    )

    # ── Build the HTTP target task ────────────────────────────────────
    http_request = tasks_v2.HttpRequest(
        http_method=tasks_v2.HttpMethod.POST,
        url=worker_url,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )

    http_request.oidc_token = tasks_v2.OidcToken(
        service_account_email=s.cloud_run_sa_email,
        audience=s.worker_service_url.rstrip("/"),
    )

    from google.protobuf import duration_pb2  # noqa: PLC0415

    dispatch_deadline = duration_pb2.Duration()
    dispatch_deadline.FromSeconds(600)  # 10 minutes — match Cloud Run

    task = tasks_v2.Task(
        http_request=http_request,
        dispatch_deadline=dispatch_deadline,
    )

    task_name = client.task_path(
        s.gcp_project_id,
        s.cloud_tasks_location,
        s.cloud_tasks_queue_name,
        f"{_TASK_NAME_PREFIX}-{document_id}",
    )
    task.name = task_name

    try:
        response = client.create_task(
            request=tasks_v2.CreateTaskRequest(parent=parent, task=task)
        )
        logger.info(
            "cloud_tasks_enqueued",
            extra={
                "document_id": document_id,
                "task_name": response.name,
                "force": force,
            },
        )
        return response.name
    except gcp_exceptions.AlreadyExists:
        logger.info(
            "cloud_tasks_already_exists",
            extra={
                "document_id": document_id,
                "task_name": task_name,
                "detail": (
                    "A RAG ingestion task for this document is already "
                    "pending on the queue.  Skipping duplicate enqueue."
                ),
            },
        )
        return task_name
    except Exception:
        logger.exception(
            "cloud_tasks_enqueue_failed",
            extra={"document_id": document_id},
        )
        raise
