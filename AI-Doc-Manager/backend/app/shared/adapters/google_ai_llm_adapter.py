import logging

from google import genai
from google.genai import types

from app.core.config import Settings, get_settings
from app.shared.interfaces import ILLMProvider

logger = logging.getLogger(__name__)


class GoogleAILlmAdapter(ILLMProvider):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        # NOTE: Config field is `google_api_key` (not `google_ai_api_key`)
        api_key = getattr(self.settings, "google_api_key", None)
        self.client = genai.Client(api_key=api_key) if api_key else genai.Client()

        # gemini-embedding-2 supports RETRIEVAL_DOCUMENT task type for better indexing quality
        self.embedding_model = self.settings.embedding_model
        self.llm_model = self.settings.llm_model

    def generate_embeddings(
        self,
        texts: list[str],
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> list[list[float]]:
        """Generate embeddings for a list of text chunks.

        embed_content() with a list of strings always returns
        response.embeddings as List[ContentEmbedding], regardless of length.
        """
        if not texts:
            return []

        response = self.client.models.embed_content(
            model=self.embedding_model,
            contents=texts,
            config=types.EmbedContentConfig(task_type=task_type),
        )
        embeddings = [emb.values for emb in response.embeddings]
        logger.debug(
            "embeddings_generated",
            extra={
                "model": self.embedding_model,
                "task_type": task_type,
                "count": len(embeddings),
            },
        )
        return embeddings

    def generate_response(self, prompt: str, context: list[str]) -> str:
        """Generate a grounded answer from the provided context chunks."""
        context_str = "\n\n".join(context)
        full_prompt = (
            "You are a helpful assistant. Answer the user's question based strictly "
            "on the provided context. If the context does not contain the answer, "
            'say "I don\'t have enough information to answer that."\n\n'
            f"CONTEXT:\n{context_str}\n\nQUESTION:\n{prompt}"
        )

        response = self.client.models.generate_content(
            model=self.llm_model,
            contents=full_prompt,
        )
        return response.text
