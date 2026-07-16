"""Secret provider: reads secrets from Secret Manager (production) or env (local).

Design
------
In production, secrets such as JWT signing keys, database passwords, and API
keys must never be stored in environment variables or .env files.  Instead they
are fetched at startup from Google Cloud Secret Manager.

In local development, secrets are read from environment variables (set via
``.env``), which is acceptable because the local environment does not hold
real production credentials.

Cloud Run deployment compatibility
----------------------------------
This module uses the Secret Manager **SDK** approach (``client.access_secret_version``)
rather than Cloud Run's ``--set-secrets`` (env-var injection) or secret-volume
mounts.  The CI/CD pipeline (``cloudbuild.yaml``) intentionally does NOT pass
``--set-secrets`` to ``gcloud run deploy`` — doing so would cause redundant
API calls (Cloud Run fetches once for the env var, the SDK fetches again at
startup) and could mask permission misconfigurations by falling back to a
potentially-stale env-var default.

For secret rotation support, consider switching to Cloud Run **secret volumes**
(``gcloud run deploy --update-secrets=/path=SECRET:VERSION``).  Volume-mounted
secrets are always read from Secret Manager on each file access, so the
container sees rotated values without a restart.  The current in-process cache
requires a redeploy to pick up new secret versions — acceptable for most
workloads but not for long-lived instances.

Usage
-----
.. code-block:: python

    from app.shared.secret_provider import get_secret

    jwt_secret = get_secret("jwt-secret-key", default="change-me")
    db_password = get_secret("db-password")
"""

import logging
from functools import cache

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


def _is_production(settings: Settings) -> bool:
    return settings.environment.lower() in {"production", "prod"}


@cache
def _fetch_from_secret_manager(secret_id: str, project_id: str) -> str:
    """Fetch and cache the latest version of *secret_id* from Secret Manager."""
    from google.cloud import secretmanager  # noqa: PLC0415

    client = secretmanager.SecretManagerServiceClient()
    name = client.secret_version_path(project_id, secret_id, "latest")
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("utf-8")
    logger.debug("secret_fetched", extra={"secret_id": secret_id})
    return payload


def get_secret(
    secret_id: str,
    settings: Settings | None = None,
    *,
    default: str | None = None,
    env_var: str | None = None,
) -> str:
    """Return the value of *secret_id*.

    Resolution order (first match wins):
    1. **Production** (``ENVIRONMENT=production`` or ``prod``):
       Fetches from Secret Manager ``projects/{project}/secrets/{secret_id}/versions/latest``.
    2. **Local**: Reads the environment variable named *env_var* (if given),
       or ``secret_id`` uppercased with dashes replaced by underscores (e.g.
       ``jwt-secret-key`` → ``JWT_SECRET_KEY``).
    3. Returns *default* if nothing matches.

    Args:
        secret_id: Secret Manager secret ID (also used to derive env var name).
        settings:  Optional ``Settings`` instance.
        default:   Fallback value when neither Secret Manager nor env provides one.
        env_var:   Explicit environment variable name override.

    Returns:
        The resolved secret string.

    Raises:
        RuntimeError: If no value is found and no *default* is provided.
    """
    s = settings or get_settings()

    # Production path: Secret Manager
    if _is_production(s):
        try:
            return _fetch_from_secret_manager(secret_id, s.gcp_project_id or "")
        except Exception as exc:
            logger.warning(
                "secret_manager_fetch_failed",
                extra={"secret_id": secret_id, "error": str(exc)},
            )
            logger.warning(
                "secret_manager_fallback",
                extra={
                    "secret_id": secret_id,
                    "reason": "Secret Manager fetch failed; falling back to default",
                },
            )
        # Fall through to default in production if SM fetch fails.

    # Local path: use the provided default (which typically comes from the
    # pydantic-settings model that already reads from .env / env vars).
    # NOTE: we do NOT cache defaults — they come from a specific Settings
    # instance and may differ across tests.
    if default is not None:
        return default

    # Last resort: raw environment variable lookup.
    env_name = env_var or secret_id.replace("-", "_").upper()
    import os
    value = os.getenv(env_name)
    if value:
        return value

    raise RuntimeError(
        f"Secret '{secret_id}' is not configured. "
        f"Set the {env_name} environment variable (local) or create a Secret Manager "
        f"secret named '{secret_id}' (production)."
    )
