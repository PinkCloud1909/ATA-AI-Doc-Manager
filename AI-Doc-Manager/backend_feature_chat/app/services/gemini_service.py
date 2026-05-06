"""
services/gemini_service.py
Wrapper cho Vertex AI Gemini API.
- generate_answer():   non-streaming, dùng cho REST /chat
- stream_answer():     async generator, dùng cho WebSocket streaming
- generate_title():    tóm tắt ngắn để đặt tên ChatSession
"""
from __future__ import annotations

import structlog
from typing import AsyncGenerator
from tenacity import retry, stop_after_attempt, wait_exponential

import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    GenerationConfig,
    Content,
    Part,
    HarmCategory,
    HarmBlockThreshold,
)

from app.core.config import settings
from app.schemas.chat import SourceReference

logger = structlog.get_logger()

# ── Lazy init ─────────────────────────────────────────────────────────────────
_model: GenerativeModel | None = None
_model_flash: GenerativeModel | None = None

_SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH:       HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT:        HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

_GENERATION_CONFIG = GenerationConfig(
    temperature=0.3,       # thấp để câu trả lời nhất quán, ít hallucinate
    top_p=0.95,
    max_output_tokens=2048,
)


def _get_model(flash: bool = False) -> GenerativeModel:
    global _model, _model_flash
    vertexai.init(project=settings.GCP_PROJECT_ID, location=settings.VERTEX_AI_LOCATION)
    if flash:
        if _model_flash is None:
            _model_flash = GenerativeModel(
                settings.GEMINI_MODEL_FLASH,
                safety_settings=_SAFETY_SETTINGS,
                generation_config=_GENERATION_CONFIG,
            )
        return _model_flash
    else:
        if _model is None:
            _model = GenerativeModel(
                settings.GEMINI_MODEL,
                safety_settings=_SAFETY_SETTINGS,
                generation_config=_GENERATION_CONFIG,
            )
        return _model


# ── Prompt builders ───────────────────────────────────────────────────────────

def _build_rag_prompt(
    query: str,
    sources: list[SourceReference],
    source_contents: dict[str, str],  # {document_id: text_content}
) -> str:
    """
    Xây dựng RAG prompt khi có kết quả từ Vertex AI Vector Search.
    """
    context_blocks = []
    for s in sources:
        content = source_contents.get(s.document_id, "")
        if content:
            context_blocks.append(
                f"[Tài liệu: {s.original_filename} - v{s.version}]\n{content[:3000]}"
            )

    context = "\n\n---\n\n".join(context_blocks)

    return f"""Bạn là AI trợ lý chuyên về quản lý tài liệu kỹ thuật và runbook.
Hãy trả lời câu hỏi dưới đây DỰA TRÊN các tài liệu được cung cấp.
Nếu tài liệu không đủ thông tin, hãy nói rõ phần nào bạn trả lời từ tài liệu,
phần nào từ kiến thức chung.
Trả lời bằng tiếng Việt, ngắn gọn và chính xác.

=== TÀI LIỆU THAM KHẢO ===
{context}

=== CÂU HỎI ===
{query}

=== TRẢ LỜI ==="""


def _build_fallback_prompt(query: str, history: list[dict]) -> str:
    """
    Prompt khi KHÔNG có tài liệu phù hợp trong Vector Index.
    Gemini trả lời từ kiến thức chung nhưng có disclaimer.
    """
    history_text = ""
    if history:
        history_text = "\n".join([
            f"{'User' if h['role'] == 'user' else 'AI'}: {h['content']}"
            for h in history[-6:]  # last 3 turns
        ])

    return f"""Bạn là AI trợ lý chuyên về quản lý tài liệu kỹ thuật và runbook.
Không tìm thấy tài liệu phù hợp trong hệ thống. Hãy trả lời từ kiến thức chung của bạn.
Luôn bắt đầu câu trả lời với: "Tôi không tìm thấy tài liệu cụ thể trong hệ thống, nhưng..."
Trả lời bằng tiếng Việt.

{f"=== LỊCH SỬ HỘI THOẠI ==={chr(10)}{history_text}{chr(10)}" if history_text else ""}
=== CÂU HỎI ===
{query}

=== TRẢ LỜI ==="""


# ── Public API ────────────────────────────────────────────────────────────────

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_answer(
    query: str,
    sources: list[SourceReference],
    source_contents: dict[str, str],
    conversation_history: list[dict] | None = None,
) -> tuple[str, str]:
    """
    Non-streaming answer cho REST endpoint.
    Returns: (answer_text, model_name)
    """
    model = _get_model()

    if sources:
        prompt = _build_rag_prompt(query, sources, source_contents)
    else:
        prompt = _build_fallback_prompt(query, conversation_history or [])

    logger.info("gemini_generate", has_sources=bool(sources), query_len=len(query))

    response = await model.generate_content_async(prompt)
    answer = response.text.strip()

    return answer, settings.GEMINI_MODEL


async def stream_answer(
    query: str,
    sources: list[SourceReference],
    source_contents: dict[str, str],
    conversation_history: list[dict] | None = None,
) -> AsyncGenerator[str, None]:
    """
    Streaming answer cho WebSocket endpoint.
    Yields text chunks (tokens) một cách async.
    """
    model = _get_model()

    if sources:
        prompt = _build_rag_prompt(query, sources, source_contents)
    else:
        prompt = _build_fallback_prompt(query, conversation_history or [])

    logger.info("gemini_stream_start", has_sources=bool(sources))

    async for chunk in await model.generate_content_async(prompt, stream=True):
        if chunk.text:
            yield chunk.text

    logger.info("gemini_stream_done")


async def generate_title(first_message: str) -> str:
    """
    Tóm tắt câu hỏi đầu tiên thành tiêu đề ngắn cho ChatSession.
    Dùng gemini-flash để tiết kiệm chi phí.
    """
    model = _get_model(flash=True)
    prompt = (
        f"Tóm tắt câu hỏi sau thành tiêu đề ngắn gọn (tối đa 8 từ), "
        f"không dùng dấu ngoặc kép:\n{first_message[:200]}"
    )
    try:
        response = await model.generate_content_async(prompt)
        return response.text.strip()[:100]
    except Exception:
        return first_message[:60]
