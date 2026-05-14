"""RAG-enabled DMS assistant agent.

The agent exposes a single tool – ``search_documents`` – that embeds the
user's query and retrieves the top-k semantically-similar text chunks from
the vector store (ChromaDB in dev, Vertex AI Vector Search in prod).

The LLM then grounds its answer **exclusively** on those retrieved chunks,
preventing hallucination about document contents.
"""

import logging

from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool

from app.shared.adapters.factory import get_llm_provider, get_vector_store

logger = logging.getLogger(__name__)


def search_documents(query: str, top_k: int = 5) -> str:
    """Search the document knowledge base for information relevant to *query*.

    Args:
        query:  The user's natural-language search question.
        top_k:  Number of document chunks to retrieve (default 5).

    Returns:
        A formatted string with the retrieved text chunks and their source
        metadata (document title, chunk index).  Returns a human-readable
        message when no relevant chunks are found.
    """
    try:
        llm = get_llm_provider()
        vector_store = get_vector_store()

        # Embed the query using QUESTION_ANSWERING task type.
        # Documents are indexed with RETRIEVAL_DOCUMENT; queries must use a
        # compatible asymmetric task type for optimal retrieval quality.
        # See: https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/task-types
        query_embeddings = llm.generate_embeddings(
            [query],
            task_type="QUESTION_ANSWERING",
        )
        if not query_embeddings:
            return "Could not generate query embedding."

        query_embedding = query_embeddings[0]
        results = vector_store.semantic_search(query_embedding, top_k=top_k)

        if not results:
            return (
                "No relevant documents found in the knowledge base for that query. "
                "The document may not have been uploaded and vectorized yet."
            )

        # Format results for the LLM context.
        # ``score`` = cosine similarity ∈ [−1, 1]; higher = more relevant.
        # ``distance`` = raw Chroma value; lower = more relevant.
        parts: list[str] = []
        for i, result in enumerate(results, start=1):
            meta = result.get("metadata", {})
            title = meta.get("title", "Unknown document")
            chunk_idx = meta.get("chunk_index", "?")
            score = result.get("score")
            score_str = f"{score:.4f}" if isinstance(score, float) else "n/a"
            text = result.get("text", "")
            parts.append(
                f"[Chunk {i}] Source: '{title}' (chunk #{chunk_idx}, similarity: {score_str})\n"
                f"{text}"
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
# It has one tool (search_documents) and a grounding instruction that forces
# it to cite retrieved chunks rather than making up answers.
root_agent = Agent(
    model="gemini-2.0-flash",
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
)
