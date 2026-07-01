"""Cloud Tasks task publisher for async vectorization.

This module is the single place that knows how to enqueue a Cloud Tasks HTTP
target task aimed at the internal worker endpoint.

Design
------
- The worker endpoint is ``POST /api/v1/vectorization/worker/{document_id}``.
- Tasks carry the document_id in the URL; no request body is required.
- OIDC authentication is used so only Cloud Tasks (with the right service
  account) can call the worker endpoint.
- ``google-cloud-tasks`` is already in pyproject.toml dependencies.

Local development
-----------------
This module is only called from the router when the queue name is configured
(see ``is_async_mode()``).  In local Docker Compose the queue name is not set,
so the router falls back to synchronous in-process vectorization.

Failure handling
----------------
If ``create_task`` raises, the exception propagates up to the router which
returns a 500.  The document is NOT marked as vectorized, so the caller can
retry.
"""

import json
import logging

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


def is_async_mode(settings: Settings | None = None) -> bool:
    """Return True when Cloud Tasks async mode is active.

    Async mode requires:
    - ENVIRONMENT is production/prod
    - CLOUD_TASKS_QUEUE_NAME is set
    - WORKER_SERVICE_URL is set

    All three must be present; a partial config falls back to sync mode so
    a misconfigured environment fails loudly at task-enqueue time, not silently.
    """
    s = settings or get_settings()
    _PROD_ENVS = {"production", "prod"}
    return bool(
        s.environment.lower() in _PROD_ENVS
        and s.cloud_tasks_queue_name
        and s.worker_service_url
    )


def enqueue_vectorization_task(
    document_id: str,
    force: bool = False,
    settings: Settings | None = None,
) -> str:
    """Enqueue a vectorization task for *document_id* on the Cloud Tasks queue.

    Args:
        document_id: UUID string of the document to vectorize.
        force:       If True, re-vectorize even if already vectorized.
        settings:    Optional Settings override (defaults to get_settings()).

    Returns:
        The Cloud Tasks task name (resource path string).

    Raises:
        RuntimeError: If required config fields are missing.
        google.api_core.exceptions.GoogleAPICallError: On API failure.
    """
    s = settings or get_settings()

    if not s.cloud_tasks_queue_name:
        raise RuntimeError("CLOUD_TASKS_QUEUE_NAME is not configured")
    if not s.worker_service_url:
        raise RuntimeError("WORKER_SERVICE_URL is not configured")
    if not s.gcp_project_id:
        raise RuntimeError("GCP_PROJECT_ID is not configured")

    # Lazy import: google-cloud-tasks is only needed at enqueue time.
    # Keeps local dev imports fast and allows tests to mock tasks_v2.
    from google.cloud import tasks_v2  # noqa: PLC0415

    client = tasks_v2.CloudTasksClient()
    parent = client.queue_path(
        s.gcp_project_id,
        s.cloud_tasks_location,
        s.cloud_tasks_queue_name,
    )

    worker_url = (
        f"{s.worker_service_url.rstrip('/')}"
        f"/api/v1/vectorization/worker/{document_id}"
        f"?force={str(force).lower()}"
    )

    task: dict = {
        "http_request": {
            "http_method": tasks_v2.HttpMethod.POST,
            "url": worker_url,
            "headers": {"Content-Type": "application/json"},
            # Empty body — all parameters are in the URL.
            "body": json.dumps({}).encode(),
        }
    }

    # Add OIDC token so the worker endpoint can verify the caller is Cloud Tasks.
    # The service account must have roles/run.invoker on this Cloud Run service.
    if s.cloud_run_sa_email:
        task["http_request"]["oidc_token"] = {
            "service_account_email": s.cloud_run_sa_email,
            # Audience must match the Cloud Run service URL (no path).
            "audience": s.worker_service_url.rstrip("/"),
        }
    else:
        logger.warning(
            "cloud_tasks_no_oidc",
            extra={
                "reason": "CLOUD_RUN_SA_EMAIL not set; task will be unauthenticated"
            },
        )

    response = client.create_task(request={"parent": parent, "task": task})

    logger.info(
        "cloud_tasks_enqueued",
        extra={"document_id": document_id, "task_name": response.name},
    )
    return response.name
