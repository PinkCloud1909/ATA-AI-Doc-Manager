import logging

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.modules.qa.domain.agent import root_agent
from google.genai import types

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self):
        settings = get_settings()
        # Initialize ADK DatabaseSessionService using the async DB URL
        self.session_service = DatabaseSessionService(db_url=settings.async_database_url)
        self.runner = Runner(
            app_name="dms_chat_app",
            agent=root_agent,
            session_service=self.session_service,
            auto_create_session=True,
        )

    async def chat(self, user_id: str, session_id: str, message: str) -> str:
        """
        Executes the agent and returns the final text response.
        """
        try:
            events = []
            adk_message = types.Content(role="user", parts=[types.Part.from_text(text=message)])
            
            # Start the ADK execution loop
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=adk_message,
            ):
                events.append(event)

            # Extract the response from the LLM events
            final_text = ""
            for event in reversed(events):
                content = getattr(event, "content", None)
                if content and getattr(content, "role", None) == "model":
                    parts = getattr(content, "parts", [])
                    for part in parts:
                        text = getattr(part, "text", None)
                        if text:
                            final_text += text
                    if final_text:
                        return final_text

            return "No response generated."
        except Exception as e:
            error_message = str(e)
            logger.error("chat_error", extra={"error": error_message, "session_id": session_id})

            if (
                "API_KEY_SERVICE_BLOCKED" in error_message
                or "PERMISSION_DENIED" in error_message
                or "generativelanguage.googleapis.com" in error_message
            ):
                raise ExternalServiceError(
                    "Gemini API key is blocked for Generative Language API. "
                    "Enable generativelanguage.googleapis.com for this key/project, "
                    "or configure a valid server-side GOOGLE_API_KEY."
                ) from e

            if "Connection refused" in error_message:
                raise ExternalServiceError(
                    "Chat session database is unreachable. Check ASYNC_DATABASE_URL."
                ) from e

            raise
