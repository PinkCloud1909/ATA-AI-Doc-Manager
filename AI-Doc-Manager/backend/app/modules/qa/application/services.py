"""Q&A ChatService using Google ADK Runner with DatabaseSessionService.

Session lifecycle (ADK docs):
  1. Try to get existing session via session_service.get_session()
  2. If not found, create a new one via session_service.create_session()
  3. Pass session_id to runner.run_async() — Runner handles history
"""

import logging

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.modules.qa.domain.agent import root_agent

logger = logging.getLogger(__name__)

_APP_NAME = "dms_chat_app"


class ChatService:
    def __init__(self) -> None:
        settings = get_settings()
        # DatabaseSessionService requires an async-compatible DB URL.
        # asyncpg is listed in pyproject.toml and the URL uses postgresql+asyncpg.
        self.session_service = DatabaseSessionService(
            db_url=settings.async_database_url
        )
        # NOTE: Runner does NOT accept auto_create_session — sessions must be
        # managed explicitly via session_service before calling run_async().
        self.runner = Runner(
            app_name=_APP_NAME,
            agent=root_agent,
            session_service=self.session_service,
        )

    async def _get_or_create_session(self, user_id: str, session_id: str):
        """Return existing session or create a fresh one."""
        try:
            session = await self.session_service.get_session(
                app_name=_APP_NAME,
                user_id=user_id,
                session_id=session_id,
            )
            if session is not None:
                return session
        except Exception as exc:
            logger.debug(
                "session_get_failed",
                extra={"session_id": session_id, "reason": str(exc)},
            )

        # Session doesn't exist yet — create it
        session = await self.session_service.create_session(
            app_name=_APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        logger.info(
            "session_created",
            extra={"session_id": session_id, "user_id": user_id},
        )
        return session

    async def chat(self, user_id: str, session_id: str, message: str) -> str:
        """Run one conversation turn and return the agent's text response."""
        # Ensure session exists in the DB before the runner tries to load it
        await self._get_or_create_session(user_id, session_id)

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
