from typing import List, Optional

from google import genai

from app.core.config import Settings, get_settings
from app.shared.interfaces import ILLMProvider


class GoogleAILlmAdapter(ILLMProvider):
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        api_key = getattr(self.settings, "google_ai_api_key", None)
        self.client = genai.Client(api_key=api_key) if api_key else genai.Client()
        
        # Use appropriate models for embeddings and text generation
        self.embedding_model = "text-embedding-004"
        self.llm_model = "gemini-1.5-pro-latest"

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        # Google AI embedding API via unified SDK
        response = self.client.models.embed_content(
            model=self.embedding_model,
            contents=texts,
        )
        
        # Extract embeddings depending on the response format
        if isinstance(texts, list) and len(texts) > 1:
            return [emb.values for emb in response.embeddings]
        elif isinstance(texts, list) and len(texts) == 1:
            # Sometimes a list of 1 returns a single object or a list of 1
            if isinstance(response.embeddings, list):
                return [response.embeddings[0].values]
            return [response.embeddings.values]
        else:
            return [response.embeddings.values]

    def generate_response(self, prompt: str, context: List[str]) -> str:
        # Construct the grounded prompt
        context_str = "\n\n".join(context)
        full_prompt = f"""
        You are a helpful assistant. Please answer the user's question based strictly on the provided context.
        If the context does not contain the answer, say "I don't have enough information to answer that."
        
        CONTEXT:
        {context_str}
        
        QUESTION:
        {prompt}
        """
        
        response = self.client.models.generate_content(
            model=self.llm_model,
            contents=full_prompt
        )
        return response.text
