"""Unit tests for task_publisher.is_async_mode and enqueue_vectorization_task.

All Cloud Tasks SDK calls are mocked via sys.modules injection so this test
suite runs without google-cloud-tasks installed.
"""

import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Inject a fake google.cloud.tasks_v2 into sys.modules so the lazy import
# inside enqueue_vectorization_task resolves without the real SDK being present.
# ---------------------------------------------------------------------------
_mock_tasks_v2 = MagicMock(name="tasks_v2")
_mock_tasks_v2.CloudTasksClient = MagicMock(name="CloudTasksClient")
_mock_tasks_v2.HttpMethod = MagicMock(name="HttpMethod")
_mock_tasks_v2.HttpMethod.POST = "POST"

# Ensure google.cloud namespace exists in sys.modules.
if "google" not in sys.modules:
    sys.modules["google"] = ModuleType("google")
if "google.cloud" not in sys.modules:
    sys.modules["google.cloud"] = ModuleType("google.cloud")
sys.modules["google.cloud.tasks_v2"] = _mock_tasks_v2

_TASKS_CLIENT_PATH = "app.shared.task_publisher.tasks_v2.CloudTasksClient"


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
    mock_response = MagicMock()
    mock_response.name = "projects/my-project/.../tasks/abc"
    mock_client.create_task.return_value = mock_response
    _mock_tasks_v2.CloudTasksClient.return_value = mock_client
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
# enqueue_vectorization_task
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
        from app.shared.task_publisher import enqueue_vectorization_task

        mock_client = _setup_mock_client()
        task_name = enqueue_vectorization_task(
            document_id="doc-uuid-123",
            force=False,
            settings=self._prod_settings(),
        )

        assert task_name == "projects/my-project/.../tasks/abc"
        mock_client.create_task.assert_called_once()
        call_kwargs = mock_client.create_task.call_args.kwargs
        task = call_kwargs["request"]["task"]
        assert "doc-uuid-123" in task["http_request"]["url"]
        assert "force=false" in task["http_request"]["url"]

    def test_includes_oidc_token_when_sa_set(self):
        from app.shared.task_publisher import enqueue_vectorization_task

        mock_client = _setup_mock_client()
        enqueue_vectorization_task(
            document_id="doc-1",
            settings=self._prod_settings(),
        )

        task = mock_client.create_task.call_args.kwargs["request"]["task"]
        assert "oidc_token" in task["http_request"]
        assert task["http_request"]["oidc_token"]["service_account_email"] == (
            "sa@project.iam.gserviceaccount.com"
        )

    def test_raises_when_queue_name_missing(self):
        from app.shared.task_publisher import enqueue_vectorization_task

        with pytest.raises(RuntimeError, match="CLOUD_TASKS_QUEUE_NAME"):
            enqueue_vectorization_task("doc-1", settings=_settings(environment="production"))

    def test_raises_when_worker_url_missing(self):
        from app.shared.task_publisher import enqueue_vectorization_task

        with pytest.raises(RuntimeError, match="WORKER_SERVICE_URL"):
            enqueue_vectorization_task(
                "doc-1",
                settings=_settings(
                    environment="production",
                    cloud_tasks_queue_name="q",
                ),
            )

    def test_force_true_encoded_in_url(self):
        from app.shared.task_publisher import enqueue_vectorization_task

        mock_client = _setup_mock_client()
        enqueue_vectorization_task(
            document_id="doc-2",
            force=True,
            settings=self._prod_settings(),
        )

        task = mock_client.create_task.call_args.kwargs["request"]["task"]
        assert "force=true" in task["http_request"]["url"]

