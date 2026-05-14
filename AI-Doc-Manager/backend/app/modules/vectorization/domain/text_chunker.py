import logging

logger = logging.getLogger(__name__)


class TextChunker:
    """Splits text into fixed-size chunks with configurable overlap.

    Chunks are split on character boundaries but prefer breaking at
    newline characters when possible.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap must be non-negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str) -> list[str]:
        """Split *text* into chunks and return them as a list of strings.

        Empty or whitespace-only input returns an empty list.
        """
        text = text.strip()
        if not text:
            return []

        chunks: list[str] = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size

            if end >= text_length:
                # Last chunk — take everything remaining
                chunk_text = text[start:].strip()
                if chunk_text:
                    chunks.append(chunk_text)
                break

            # Prefer a paragraph break (\n\n) for cleanest semantic boundaries,
            # fall back to a single newline, then accept the hard character cut.
            boundary = text.rfind("\n\n", start + self.chunk_size // 2, end)
            if boundary != -1:
                end = boundary + 2  # include both newlines
            else:
                boundary = text.rfind("\n", start + self.chunk_size // 2, end)
                if boundary != -1:
                    end = boundary + 1  # include the newline

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(chunk_text)

            # Advance by (end - overlap) to create the sliding window
            start = end - self.chunk_overlap
            if start <= (end - self.chunk_size):
                # Safety: always advance at least 1 char to avoid infinite loop
                start = end

        logger.debug(
            "text_chunked",
            extra={
                "total_chars": text_length,
                "chunk_count": len(chunks),
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
            },
        )
        return chunks
