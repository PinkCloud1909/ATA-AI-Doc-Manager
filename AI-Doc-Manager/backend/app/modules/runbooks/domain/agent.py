"""Runbook generation agent using Google ADK.

The agent exposes a single tool — ``search_knowledge_for_runbook`` — that
retrieves top-k semantically-similar text chunks from the RAG Engine,
optionally filtered to specific document IDs.  Results are enriched with
document titles.

State passing via contextvars
-----------------------------
Document IDs are passed from the service layer to the tool function via
:mod:`contextvars`.  This is safe because:

1. Each FastAPI request runs in its own asyncio Task.
2. Python ``ContextVar`` values are isolated per asyncio Task — setting a value
   in one request's Task never affects another concurrent request.
3. The values are set synchronously in ``generate_runbook_task()`` before the
   first ``await`` point that could yield control to another Task.

If the pattern ever needs to change (e.g. multi-threaded deployment), replace
with ADK session state or an explicit tool-factory per request.
"""

import contextvars
import logging
from uuid import UUID

from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from google.genai import types

from app.core.config import get_settings
from app.modules.rag.application.retrieval import retrieve_chunks

logger = logging.getLogger(__name__)

_settings = get_settings()

# Context variable for per-request document scope isolation.
# See module docstring for thread-safety rationale.
active_document_ids: contextvars.ContextVar[list[UUID]] = contextvars.ContextVar(
    "active_document_ids", default=[]
)


def search_knowledge_for_runbook(query: str, top_k: int = 10) -> str:
    """Search the document knowledge base for information relevant to the runbook.

    Args:
        query:  The natural-language search query.
        top_k:  Number of document chunks to retrieve (default 10).

    Returns:
        A formatted string with the retrieved text chunks and their source
        metadata.  Returns a warning message when no relevant chunks are found.
    """
    try:
        doc_ids = active_document_ids.get()
        results = retrieve_chunks(
            query=query,
            top_k=top_k,
            document_ids=doc_ids if doc_ids else None,
        )

        if not results:
            return "No relevant information found in the specified documents for that query."

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
            "runbook_search_results",
            extra={"query": query, "chunk_count": len(results)},
        )
        return "\n\n---\n\n".join(parts)

    except Exception as exc:
        logger.error("runbook_search_error", extra={"error": str(exc)})
        return f"An error occurred while searching the knowledge base: {exc}"


# The runbook generator agent.
runbook_agent = Agent(
    model=_settings.llm_model,
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
    generate_content_config=types.GenerateContentConfig(
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(
                initial_delay=1.0,
                attempts=3,
            ),
        ),
    ),
)
