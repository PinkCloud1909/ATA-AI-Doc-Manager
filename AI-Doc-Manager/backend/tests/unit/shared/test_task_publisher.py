"""Unit tests for task_publisher.is_async_mode and enqueue_rag_ingestion_task.

All Cloud Tasks SDK calls are mocked via sys.modules injection so this test
suite runs without google-cloud-tasks installed.
"""

import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Inject a fake google.cloud.tasks_v2 into sys.modules so the lazy import
# inside enqueue_rag_ingestion_task resolves without the real SDK being present.
# ---------------------------------------------------------------------------
_mock_tasks_v2 = MagicMock(name="tasks_v2")
_mock_tasks_v2.CloudTasksClient = MagicMock(name="CloudTasksClient")
_mock_tasks_v2.HttpMethod = MagicMock(name="HttpMethod")
_mock_tasks_v2.HttpMethod.POST = "POST"
# Proto-plus types used in task construction.
_mock_tasks_v2.HttpRequest = MagicMock(name="HttpRequest")
_mock_tasks_v2.Task = MagicMock(name="Task")
_mock_tasks_v2.OidcToken = MagicMock(name="OidcToken")
_mock_tasks_v2.CreateTaskRequest = MagicMock(name="CreateTaskRequest")

# Ensure google.cloud namespace exists in sys.modules.
if "google" not in sys.modules:
    sys.modules["google"] = ModuleType("google")
if "google.cloud" not in sys.modules:
    sys.modules["google.cloud"] = ModuleType("google.cloud")
sys.modules["google.cloud.tasks_v2"] = _mock_tasks_v2

# Also mock google.protobuf.duration_pb2 for dispatch_deadline construction.
_mock_duration_pb2 = MagicMock(name="duration_pb2")
_mock_duration = MagicMock(name="Duration")
_mock_duration.seconds = 600  # default — tests can override
_mock_duration_pb2.Duration.return_value = _mock_duration
if "google.protobuf" not in sys.modules:
    sys.modules["google.protobuf"] = ModuleType("google.protobuf")
sys.modules["google.protobuf.duration_pb2"] = _mock_duration_pb2

_TASKS_CLIENT_PATH = "app.shared.task_publisher.tasks_v2.CloudTasksClient"


def _reset_client_cache():
    """Reset the module-level _tasks_client so each test gets a fresh mock."""
    from app.shared import task_publisher

    task_publisher._tasks_client = None


def _settings(**overrides):
    defaults = {
        "environment": "local",
        "cloud_tasks_queue_name": None,
        "cloud_tasks_location": "us-central1",
        "worker_service_url": None,
        "cloud_run_sa_email": None,
        "gcp_project_id": "my-project",
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _setup_mock_client():
    """Configure _mock_tasks_v2 to return a usable mock client."""
    mock_client = MagicMock()
    mock_client.queue_path.return_value = (
        "projects/my-project/locations/us-central1/queues/dms-vectorization"
    )
    mock_client.task_path.return_value = (
        "projects/my-project/locations/us-central1/queues/"
        "dms-vectorization/tasks/test-task-id"
    )
    mock_response = MagicMock()
    mock_response.name = "projects/my-project/.../tasks/test-task-id"
    mock_client.create_task.return_value = mock_response
    _mock_tasks_v2.CloudTasksClient.return_value = mock_client

    # Reset the proto-type mocks so each test starts clean.
    _mock_tasks_v2.HttpRequest.reset_mock()
    _mock_tasks_v2.Task.reset_mock()
    _mock_tasks_v2.OidcToken.reset_mock()
    _mock_tasks_v2.CreateTaskRequest.reset_mock()

    return mock_client


# ---------------------------------------------------------------------------
# is_async_mode
# ---------------------------------------------------------------------------


class TestIsAsyncMode:
    def test_false_when_local(self):
        from app.shared.task_publisher import is_async_mode

        assert not is_async_mode(_settings())

    def test_false_when_prod_but_no_queue(self):
        from app.shared.task_publisher import is_async_mode

        assert not is_async_mode(_settings(environment="production"))

    def test_false_when_queue_but_no_url(self):
        from app.shared.task_publisher import is_async_mode

        s = _settings(environment="production", cloud_tasks_queue_name="q")
        assert not is_async_mode(s)

    def test_true_when_all_set(self):
        from app.shared.task_publisher import is_async_mode

        s = _settings(
            environment="production",
            cloud_tasks_queue_name="dms-vectorization",
            worker_service_url="https://backend.run.app",
        )
        assert is_async_mode(s)

    def test_true_for_prod_alias(self):
        from app.shared.task_publisher import is_async_mode

        s = _settings(
            environment="prod",
            cloud_tasks_queue_name="q",
            worker_service_url="https://backend.run.app",
        )
        assert is_async_mode(s)


# ---------------------------------------------------------------------------
# enqueue_rag_ingestion_task
# ---------------------------------------------------------------------------


class TestEnqueueVectorizationTask:
    def _prod_settings(self, **extra):
        return _settings(
            environment="production",
            cloud_tasks_queue_name="dms-vectorization",
            worker_service_url="https://backend.run.app",
            cloud_run_sa_email="sa@project.iam.gserviceaccount.com",
            **extra,
        )

    def test_creates_task_with_correct_url(self):
        from app.shared.task_publisher import enqueue_rag_ingestion_task

        _reset_client_cache()
        mock_client = _setup_mock_client()
        task_name = enqueue_rag_ingestion_task(
            document_id="doc-uuid-123",
            force=False,
            settings=self._prod_settings(),
        )

        assert task_name == "projects/my-project/.../tasks/test-task-id"
        mock_client.create_task.assert_called_once()

        # Verify HttpRequest was constructed with the correct URL.
        http_req_call = _mock_tasks_v2.HttpRequest.call_args
        assert http_req_call is not None
        url = http_req_call.kwargs["url"]
        assert "doc-uuid-123" in url
        assert "force=false" in url
        assert http_req_call.kwargs["http_method"] == "POST"
        # Content-Type header should include charset for compatibility.
        headers = http_req_call.kwargs.get("headers", {})
        assert "application/json" in headers.get("Content-Type", "")

    def test_includes_oidc_token_when_sa_set(self):
        from app.shared.task_publisher import enqueue_rag_ingestion_task

        _reset_client_cache()
        _setup_mock_client()
        enqueue_rag_ingestion_task(
            document_id="doc-1",
            settings=self._prod_settings(),
        )

        # Verify OidcToken was constructed with correct SA email.
        oidc_calls = _mock_tasks_v2.OidcToken.call_args_list
        assert len(oidc_calls) >= 1
        sa_email = oidc_calls[0].kwargs["service_account_email"]
        assert sa_email == "sa@project.iam.gserviceaccount.com"

    def test_raises_when_queue_name_missing(self):
        from app.shared.task_publisher import enqueue_rag_ingestion_task

        _reset_client_cache()
        with pytest.raises(RuntimeError, match="CLOUD_TASKS_QUEUE_NAME"):
            enqueue_rag_ingestion_task(
                "doc-1", settings=_settings(environment="production")
            )

    def test_raises_when_worker_url_missing(self):
        from app.shared.task_publisher import enqueue_rag_ingestion_task

        _reset_client_cache()
        with pytest.raises(RuntimeError, match="WORKER_SERVICE_URL"):
            enqueue_rag_ingestion_task(
                "doc-1",
                settings=_settings(
                    environment="production",
                    cloud_tasks_queue_name="q",
                ),
            )

    def test_raises_when_sa_email_missing(self):
        from app.shared.task_publisher import enqueue_rag_ingestion_task

        _reset_client_cache()
        with pytest.raises(RuntimeError, match="CLOUD_RUN_SA_EMAIL"):
            enqueue_rag_ingestion_task(
                "doc-1",
                settings=_settings(
                    environment="production",
                    cloud_tasks_queue_name="q",
                    worker_service_url="https://backend.run.app",
                    cloud_run_sa_email=None,
                ),
            )

    def test_force_true_encoded_in_url(self):
        from app.shared.task_publisher import enqueue_rag_ingestion_task

        _reset_client_cache()
        _setup_mock_client()
        enqueue_rag_ingestion_task(
            document_id="doc-2",
            force=True,
            settings=self._prod_settings(),
        )

        http_req_call = _mock_tasks_v2.HttpRequest.call_args
        url = http_req_call.kwargs["url"]
        assert "force=true" in url

    def test_task_name_set_for_idempotency(self):
        """The constructed Task object must have .name set for deduplication."""
        from app.shared.task_publisher import enqueue_rag_ingestion_task

        _reset_client_cache()
        mock_client = _setup_mock_client()
        # Override task_path to return a deterministic value for assertion.
        mock_client.task_path.return_value = (
            "projects/my-project/locations/us-central1/queues/"
            "dms-vectorization/tasks/rag-ingest-doc-idempotent-1"
        )

        enqueue_rag_ingestion_task(
            document_id="doc-idempotent-1",
            settings=self._prod_settings(),
        )

        # The Task mock was called — grab the returned instance.
        # MagicMock.Task(...) returns a MagicMock. We check what .name was set to.
        task_instance = _mock_tasks_v2.Task.return_value
        # The real code sets task.name = task_name after construction.
        assert task_instance.name == (
            "projects/my-project/locations/us-central1/queues/"
            "dms-vectorization/tasks/rag-ingest-doc-idempotent-1"
        )

    def test_dispatch_deadline_is_set(self):
        """Task must include a dispatch_deadline matching Cloud Run timeout."""
        from app.shared.task_publisher import enqueue_rag_ingestion_task

        _reset_client_cache()
        _setup_mock_client()
        enqueue_rag_ingestion_task(
            document_id="doc-deadline",
            settings=self._prod_settings(),
        )

        task_call = _mock_tasks_v2.Task.call_args
        assert task_call is not None
        deadline = task_call.kwargs.get("dispatch_deadline")
        assert deadline is not None

    def test_already_exists_returns_existing_task_name(self):
        """When a task with the same name exists, return that name (idempotent)."""
        from app.shared.task_publisher import enqueue_rag_ingestion_task
        from google.api_core import exceptions as gcp_exceptions

        _reset_client_cache()
        mock_client = _setup_mock_client()
        # Set up task_path to return the expected task path for assertion.
        expected_path = (
            "projects/my-project/locations/us-central1/queues/"
            "dms-vectorization/tasks/rag-ingest-doc-already-there"
        )
        mock_client.task_path.return_value = expected_path
        mock_client.create_task.side_effect = gcp_exceptions.AlreadyExists(
            "Task already exists"
        )

        task_name = enqueue_rag_ingestion_task(
            document_id="doc-already-there",
            settings=self._prod_settings(),
        )

        # Must return the expected task path from the local task_name variable,
        # even though create_task raised AlreadyExists.
        assert task_name == expected_path

    def test_other_api_errors_propagate(self):
        """Non-AlreadyExists exceptions must propagate up to the caller."""
        from app.shared.task_publisher import enqueue_rag_ingestion_task
        from google.api_core import exceptions as gcp_exceptions

        _reset_client_cache()
        mock_client = _setup_mock_client()
        mock_client.create_task.side_effect = gcp_exceptions.PermissionDenied(
            "no enqueuer role"
        )

        with pytest.raises(gcp_exceptions.PermissionDenied):
            enqueue_rag_ingestion_task(
                document_id="doc-perm-denied",
                settings=self._prod_settings(),
            )
