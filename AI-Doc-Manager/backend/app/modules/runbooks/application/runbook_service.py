import logging
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.modules.runbooks.domain.agent import runbook_agent

logger = logging.getLogger(__name__)

_APP_NAME = "runbooks_app"


class RunbookService:
    def __init__(self) -> None:
        settings = get_settings()
        self.session_service = DatabaseSessionService(
            db_url=settings.async_database_url
        )
        self.runner = Runner(
            app_name=_APP_NAME,
            agent=runbook_agent,
            session_service=self.session_service,
        )

    async def _get_or_create_session(self, user_id: str, session_id: str):
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

        session = await self.session_service.create_session(
            app_name=_APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        return session

    async def generate(self, user_id: str, session_id: str, prompt: str) -> str:
        await self._get_or_create_session(user_id, session_id)

        adk_message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
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
                "runbook_runner_error",
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
            raise

        for event in reversed(events):
            content = getattr(event, "content", None)
            if content and getattr(content, "role", None) == "model":
                parts = getattr(content, "parts", [])
                text_parts = [
                    getattr(p, "text", None)
                    for p in parts
                    if getattr(p, "text", None)
                ]
                if text_parts:
                    return "".join(text_parts)

        logger.warning(
            "runbook_no_response",
            extra={"session_id": session_id, "event_count": len(events)},
        )
        return "No runbook could be generated."
