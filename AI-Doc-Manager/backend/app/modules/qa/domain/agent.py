"""RAG-enabled DMS assistant agent.

The agent exposes a single tool – ``search_documents`` – that retrieves the
top-k semantically-similar text chunks from the RAG Engine and enriches them
with the originating document's title.

The LLM then grounds its answer **exclusively** on those retrieved chunks,
preventing hallucination about document contents.
"""

import logging

from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from google.genai import types

from app.core.config import get_settings
from app.modules.rag.application.retrieval import retrieve_chunks

logger = logging.getLogger(__name__)

_settings = get_settings()


def search_documents(query: str, top_k: int = 5) -> str:
    """Search the document knowledge base for information relevant to *query*.

    Searches all approved, ingested documents in the RAG Engine corpus.
    When the caller has specific document scope (e.g. runbook generation),
    it should pass document IDs via context — this base function searches
    all available documents.

    Args:
        query:  The user's natural-language search question.
        top_k:  Number of document chunks to retrieve (default 5).

    Returns:
        A formatted string with the retrieved text chunks and their source
        metadata (document title, similarity score).  Returns a human-readable
        message when no relevant chunks are found.
    """
    try:
        results = retrieve_chunks(query=query, top_k=top_k)

        if not results:
            return (
                "No relevant documents found in the knowledge base for that query. "
                "The document may not have been uploaded and ingested yet."
            )

        parts: list[str] = []
        for i, chunk in enumerate(results, start=1):
            title = chunk.document_title or chunk.source_uri or "Unknown document"
            score_str = (
                f"{chunk.score:.4f}"
                if isinstance(chunk.score, float)
                else "n/a"
            )
            parts.append(
                f"[Chunk {i}] Source: '{title}' (similarity: {score_str})\n"
                f"{chunk.text}"
            )

        logger.debug(
            "rag_search_results",
            extra={"query": query, "chunk_count": len(results)},
        )
        return "\n\n---\n\n".join(parts)

    except Exception as exc:
        logger.error("rag_search_error", extra={"error": str(exc)})
        return f"An error occurred while searching the knowledge base: {exc}"


# The root agent used by ChatService.
root_agent = Agent(
    model=_settings.llm_model,
    name="dms_assistant",
    description="A RAG-powered assistant for the Document Management System.",
    instruction="""You are an expert assistant for a Document Management System (DMS).
Your job is to answer questions about the documents stored in the system.

**IMPORTANT RULES:**
1. ALWAYS call the `search_documents` tool FIRST before answering any question about document content.
2. Base your answer ONLY on the retrieved chunks returned by `search_documents`.
3. If the tool returns no results or you cannot find relevant information, clearly say so — do NOT invent an answer.
4. When you cite information, mention the source document title.
5. If the user asks a general question unrelated to documents (e.g. "hello"), you may answer directly without calling the tool.
""",
    tools=[FunctionTool(search_documents)],
    generate_content_config=types.GenerateContentConfig(
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(
                initial_delay=1.0,
                attempts=3,
            ),
        ),
    ),
)
