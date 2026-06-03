from __future__ import annotations

import re
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.documents.domain.models import Document
from app.shared.enums import Status


@dataclass
class ChatSource:
    document: Document
    score: float


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[\wÀ-ỹ]+", text.lower())
        if len(token) >= 3
    }


class ChatService:
    """RAG-style chat service with local fallback.

    Production can swap the search/generation internals to Vertex AI Vector
    Search and Vertex AI Gemini. The public behavior stays the same:
    approved knowledge base first, generated runbook second.
    """

    def search_approved_sources(
        self,
        session: Session,
        message: str,
        limit: int = 3,
    ) -> list[ChatSource]:
        query_tokens = _tokens(message)
        approved_docs = session.execute(
            select(Document).where(Document.status == Status.APPROVED)
        ).scalars().all()

        ranked: list[ChatSource] = []
        for document in approved_docs:
            haystack = " ".join(
                value or ""
                for value in [
                    document.title,
                    document.description,
                    document.original_filename,
                    document.document_type.value,
                ]
            )
            doc_tokens = _tokens(haystack)
            overlap = len(query_tokens & doc_tokens)
            if overlap > 0:
                score = overlap / max(len(query_tokens), 1)
                ranked.append(ChatSource(document=document, score=round(score, 3)))

        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[:limit]

    def answer(self, session: Session, message: str) -> tuple[str, list[ChatSource], bool]:
        sources = self.search_approved_sources(session, message)
        if sources:
            lines = [
                "Tôi ưu tiên trả lời dựa trên các tài liệu đã được phê duyệt trong hệ thống.",
                "",
            ]
            for index, source in enumerate(sources, start=1):
                doc = source.document
                lines.append(
                    f"{index}. {doc.title} (v{doc.version}, {doc.document_type.value}) "
                    f"- độ liên quan {source.score:.2f}."
                )
                if doc.description:
                    lines.append(f"   Ghi chú: {doc.description}")
            lines.extend(
                [
                    "",
                    "Khuyến nghị: mở các nguồn trên để kiểm tra chi tiết trước khi áp dụng vào vận hành.",
                ]
            )
            return "\n".join(lines), sources, True

        generated = self.generate_runbook_text(message)
        return generated, [], False

    def generate_runbook_text(self, prompt: str) -> str:
        topic = prompt.strip() or "quy trình vận hành"
        return "\n".join(
            [
                f"Runbook đề xuất cho yêu cầu: {topic}",
                "",
                "1. Mục tiêu",
                "Xác định phạm vi xử lý, người chịu trách nhiệm, tiêu chí thành công và dữ liệu cần thu thập.",
                "",
                "2. Điều kiện kích hoạt",
                "Áp dụng khi có cảnh báo, yêu cầu vận hành, thay đổi hệ thống hoặc cần chuẩn hóa thao tác lặp lại.",
                "",
                "3. Các bước thực hiện",
                "- Kiểm tra trạng thái dịch vụ và log gần nhất.",
                "- Xác nhận ảnh hưởng với người phụ trách nghiệp vụ.",
                "- Thực hiện thay đổi theo checklist đã phê duyệt.",
                "- Ghi nhận bằng chứng, thời gian, người thực hiện và kết quả.",
                "",
                "4. Kiểm tra sau xử lý",
                "Xác nhận health check, dữ liệu chính, quyền truy cập và cảnh báo monitoring đã ổn định.",
                "",
                "5. Rollback",
                "Khôi phục cấu hình/phiên bản trước đó nếu tiêu chí thành công không đạt hoặc phát sinh lỗi nghiêm trọng.",
            ]
        )
