"""
Reusable OpenAPI 3.1 components for consistent API documentation.

All helpers return plain dicts compatible with FastAPI's ``responses`` parameter.
Import from this module in routers to avoid duplicating error descriptions.
"""

from __future__ import annotations

from typing import Any


# ── Error response descriptions (text-only, no model references) ──────────
# These are safe to use everywhere.  They describe the *meaning* of each
# status code without requiring a ``model`` key.  FastAPI uses the global
# exception handlers to produce ``ErrorResponse``-shaped bodies, but
# explicitly listing ``model=ErrorResponse`` on every route would couple
# every router to the exact schema class.  This text-only approach keeps
# routers decoupled while still documenting the error contract.

RESPONSE_DESCRIPTIONS: dict[int, str] = {
    400: "Bad request — malformed input or missing required fields",
    401: "Missing or invalid authentication credentials",
    403: "Authenticated user lacks the required permission",
    404: "The requested resource was not found",
    409: "Resource conflict (e.g. duplicate username or invalid state transition)",
    413: "Uploaded file exceeds the maximum allowed size",
    422: "Request body or parameters failed validation",
    500: "Internal server error",
    503: "A dependent service (database, vector store) is temporarily unavailable",
}


def build_error_responses(*codes: int) -> dict[int | str, dict[str, Any]]:
    """Return an OpenAPI ``responses`` dict for the given status codes.

    Example::

        @router.post("/upload", responses=build_error_responses(401, 403, 413, 422))

    Each entry maps the status code to ``{"description": "..."}`` using the
    shared description strings from :data:`RESPONSE_DESCRIPTIONS`.
    """
    result: dict[int | str, dict[str, Any]] = {}
    for code in codes:
        desc = RESPONSE_DESCRIPTIONS.get(code, f"HTTP {code}")
        result[code] = {"description": desc}
    return result


# ── Convenience sets for common endpoint patterns ─────────────────────────

READ_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {"description": RESPONSE_DESCRIPTIONS[400]},
    401: {"description": RESPONSE_DESCRIPTIONS[401]},
    403: {"description": RESPONSE_DESCRIPTIONS[403]},
    404: {"description": RESPONSE_DESCRIPTIONS[404]},
    500: {"description": RESPONSE_DESCRIPTIONS[500]},
}

LIST_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {"description": RESPONSE_DESCRIPTIONS[400]},
    401: {"description": RESPONSE_DESCRIPTIONS[401]},
    403: {"description": RESPONSE_DESCRIPTIONS[403]},
    422: {"description": RESPONSE_DESCRIPTIONS[422]},
    500: {"description": RESPONSE_DESCRIPTIONS[500]},
}

MUTATE_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {"description": RESPONSE_DESCRIPTIONS[400]},
    401: {"description": RESPONSE_DESCRIPTIONS[401]},
    403: {"description": RESPONSE_DESCRIPTIONS[403]},
    404: {"description": RESPONSE_DESCRIPTIONS[404]},
    409: {"description": RESPONSE_DESCRIPTIONS[409]},
    422: {"description": RESPONSE_DESCRIPTIONS[422]},
    500: {"description": RESPONSE_DESCRIPTIONS[500]},
}

DELETE_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"description": RESPONSE_DESCRIPTIONS[401]},
    403: {"description": RESPONSE_DESCRIPTIONS[403]},
    404: {"description": RESPONSE_DESCRIPTIONS[404]},
    500: {"description": RESPONSE_DESCRIPTIONS[500]},
}

AUTH_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {"description": RESPONSE_DESCRIPTIONS[400]},
    401: {"description": RESPONSE_DESCRIPTIONS[401]},
    422: {"description": RESPONSE_DESCRIPTIONS[422]},
    500: {"description": RESPONSE_DESCRIPTIONS[500]},
}

# Readiness / health probe responses
PROBE_RESPONSES: dict[int | str, dict[str, Any]] = {
    503: {"description": RESPONSE_DESCRIPTIONS[503]},
}


# ── Tag metadata ──────────────────────────────────────────────────────────

TAG_METADATA: list[dict[str, Any]] = [
    {
        "name": "system",
        "description": "Health and readiness probes for load balancers and container orchestrators.",
    },
    {
        "name": "auth",
        "description": (
            "User registration, login, and session introspection. "
            "Public endpoints that do not require prior authentication."
        ),
    },
    {
        "name": "admin",
        "description": (
            "User and role management.  **Requires admin-level permissions.**"
        ),
    },
    {
        "name": "documents",
        "description": (
            "Document upload, metadata management, versioning, and approval workflow. "
            "All endpoints require authentication and role-based permissions."
        ),
    },
    {
        "name": "approvals",
        "description": "Pending-approval queue for reviewers and approvers.",
    },
    {
        "name": "reviews",
        "description": "Document reviews with numeric grading and written feedback.",
    },
    {
        "name": "qa",
        "description": (
            "RAG-powered conversational Q&A.  Send a message and the assistant "
            "searches vectorized documents to compose an answer."
        ),
    },
    {
        "name": "rag",
        "description": (
            "RAG ingestion and retrieval via Vertex AI RAG Engine. "
            "In production, ingestion tasks are enqueued via Cloud Tasks "
            "and processed asynchronously."
        ),
    },
    {
        "name": "runbooks",
        "description": (
            "AI-generated structured markdown runbooks synthesised from "
            "collections of vectorized documents."
        ),
    },
]


# ── App-level description ─────────────────────────────────────────────────

APP_DESCRIPTION: str = (
    "## Document Management System (DMS) Backend\n\n"
    "REST API for uploading, versioning, reviewing, and approving documents.  "
    "Includes RAG-powered semantic search and Q&A, AI-driven runbook generation, "
    "and role-based access control.\n\n"
    "### Authentication\n\n"
    "Most endpoints require a JWT **Bearer** token obtained from `POST /api/v1/auth/login`.  "
    "Include the token in the `Authorization` header:\n\n"
    "    Authorization: Bearer <your_token>\n\n"
    "### Error Responses\n\n"
    "All error responses follow the same structure:\n\n"
    "```json\n"
    '{"detail": "Human-readable message", "code": "machine_readable_code", "request_id": "uuid"}\n'
    "```\n\n"
    "### Pagination\n\n"
    "List endpoints return paginated results with `page`, `page_size`, and `total` fields."
)
