"""Q&A ChatService using Google ADK Runner with DatabaseSessionService.

Session lifecycle: Runner is configured with ``auto_create_session=True``
(ADK 2.x).  Sessions are automatically created on first use — no explicit
session management boilerplate needed.
"""

import logging

from google.adk.runners import Runner
from google.genai import types

from app.core.config import get_settings
from app.core.db import create_adk_session_service
from app.core.exceptions import ExternalServiceError
from app.modules.qa.domain.agent import root_agent

logger = logging.getLogger(__name__)

_APP_NAME = "dms_chat_app"


class ChatService:
    def __init__(self) -> None:
        # Uses create_adk_session_service which handles Cloud SQL Unix socket /
        # Cloud SQL Python Connector resolution automatically based on
        # CLOUD_SQL_CONNECTION_NAME setting.
        settings = get_settings()
        self.session_service = create_adk_session_service(settings)
        # ADK 2.x auto_create_session=True means sessions are created on first
        # use — no need for explicit _get_or_create_session boilerplate.
        self.runner = Runner(
            app_name=_APP_NAME,
            agent=root_agent,
            session_service=self.session_service,
            auto_create_session=True,
        )

    async def chat(self, user_id: str, session_id: str, message: str) -> str:
        """Run one conversation turn and return the agent's text response."""
        adk_message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=message)],
        )

        events: list = []
        try:
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=adk_message,
            ):
                events.append(event)
        except Exception as exc:
            error_message = str(exc)
            logger.error(
                "chat_runner_error",
                extra={"session_id": session_id, "error": error_message},
            )

            if (
                "API_KEY_SERVICE_BLOCKED" in error_message
                or "PERMISSION_DENIED" in error_message
                or "generativelanguage.googleapis.com" in error_message
            ):
                raise ExternalServiceError(
                    "Gemini API key is blocked for Generative Language API. "
                    "Enable generativelanguage.googleapis.com for this key/project, "
                    "or configure a valid server-side GOOGLE_API_KEY."
                ) from exc

            if "Connection refused" in error_message:
                raise ExternalServiceError(
                    "Chat session database is unreachable. Check ASYNC_DATABASE_URL."
                ) from exc

            raise

        # Extract the last model text from the event stream
        for event in reversed(events):
            content = getattr(event, "content", None)
            if content and getattr(content, "role", None) == "model":
                parts = getattr(content, "parts", [])
                text_parts = [
                    getattr(p, "text", None) for p in parts if getattr(p, "text", None)
                ]
                if text_parts:
                    return "".join(text_parts)

        logger.warning(
            "chat_no_response",
            extra={"session_id": session_id, "event_count": len(events)},
        )
        return "No response generated."
