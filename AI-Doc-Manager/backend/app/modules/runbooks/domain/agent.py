import contextvars
import logging

from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool

from app.shared.adapters.factory import get_llm_provider, get_vector_store

logger = logging.getLogger(__name__)

# Context variables to hold state during runbook generation
active_document_ids: contextvars.ContextVar[list[str]] = contextvars.ContextVar(
    "active_document_ids", default=[]
)
active_purpose: contextvars.ContextVar[str] = contextvars.ContextVar(
    "active_purpose", default="onboarding"
)


def search_knowledge_for_runbook(query: str, top_k: int = 10) -> str:
    """Search the document knowledge base for information relevant to the runbook.

    Args:
        query: The natural-language search query.
        top_k: Number of document chunks to retrieve (default 10).

    Returns:
        A formatted string with the retrieved text chunks and their source
        metadata. Returns a warning message when no relevant chunks are found.
    """
    try:
        llm = get_llm_provider()
        vector_store = get_vector_store()

        query_embeddings = llm.generate_embeddings(
            [query],
            task_type="QUESTION_ANSWERING",
        )
        if not query_embeddings:
            return "Could not generate query embedding."

        query_embedding = query_embeddings[0]

        # Fetch document filter from context
        doc_ids = active_document_ids.get()

        results = vector_store.semantic_search(
            query_embedding,
            top_k=top_k,
            filter_document_ids=doc_ids if doc_ids else None,
        )

        if not results:
            return "No relevant information found in the specified documents for that query."

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
            "runbook_search_results",
            extra={"query": query, "chunk_count": len(results)},
        )
        return "\n\n---\n\n".join(parts)

    except Exception as exc:
        logger.error("runbook_search_error", extra={"error": str(exc)})
        return f"An error occurred while searching the knowledge base: {exc}"


# The runbook generator agent
runbook_agent = Agent(
    model="gemini-2.0-flash",
    name="runbook_generator",
    description="An agent that synthesizes technical runbooks and guides from document content.",
    instruction="""You are an expert technical writer and systems engineer.
Your job is to generate a comprehensive, structured Runbook (in Markdown format) based on the query and the documents provided in the context.

**PROCEDURE:**
1. You MUST call the `search_knowledge_for_runbook` tool to retrieve relevant technical details from the documents.
2. Formulate a search query targeting the specified runbook purpose and title.
3. Synthesize the retrieved information into a cohesive, production-ready Markdown runbook.

**RUNBOOK STRUCTURE (Markdown):**
The runbook should be structured as follows:
- **Title**: A clear title reflecting the purpose (e.g., `# [Purpose] Runbook: [Title]`)
- **Overview**: High-level description of what this runbook covers, and the target audience.
- **Prerequisites**: Access rights, dependencies, files, environment variables, tools, or inputs needed.
- **Step-by-Step Procedure**: Clear, numbered steps. Use code blocks for command-line instructions, configuration files, and script paths.
- **Verification / Testing**: How to check if the steps succeeded.
- **Troubleshooting**: Common failure modes and how to resolve them based on the text.
- **References / Citations**: Cite the source documents you used.

**IMPORTANT RULES:**
- DO NOT invent details. If the retrieved chunks do not contain a step or information, state that the information was not found in the source documents.
- Rely ONLY on the information retrieved via `search_knowledge_for_runbook`.
- Format all instructions, commands, and code blocks clearly.
""",
    tools=[FunctionTool(search_knowledge_for_runbook)],
)
