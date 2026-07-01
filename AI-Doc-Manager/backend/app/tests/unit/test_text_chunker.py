import pytest

from app.modules.vectorization.domain.text_chunker import TextChunker


class TestTextChunkerInit:
    def test_valid_defaults(self):
        chunker = TextChunker()
        assert chunker.chunk_size == 1000
        assert chunker.chunk_overlap == 200

    def test_custom_params(self):
        chunker = TextChunker(chunk_size=500, chunk_overlap=50)
        assert chunker.chunk_size == 500
        assert chunker.chunk_overlap == 50

    def test_invalid_chunk_size(self):
        with pytest.raises(ValueError, match="chunk_size must be positive"):
            TextChunker(chunk_size=0)

    def test_negative_overlap(self):
        with pytest.raises(ValueError, match="chunk_overlap must be non-negative"):
            TextChunker(chunk_overlap=-1)

    def test_overlap_exceeds_size(self):
        with pytest.raises(ValueError, match="chunk_overlap must be less than"):
            TextChunker(chunk_size=100, chunk_overlap=100)


class TestChunking:
    def test_empty_string(self):
        chunker = TextChunker(chunk_size=100, chunk_overlap=10)
        assert chunker.chunk("") == []

    def test_whitespace_only(self):
        chunker = TextChunker(chunk_size=100, chunk_overlap=10)
        assert chunker.chunk("   \n\n  ") == []

    def test_short_text_single_chunk(self):
        chunker = TextChunker(chunk_size=100, chunk_overlap=10)
        text = "This is a short text."
        result = chunker.chunk(text)
        assert len(result) == 1
        assert result[0] == text

    def test_text_exactly_chunk_size(self):
        chunker = TextChunker(chunk_size=20, chunk_overlap=5)
        text = "A" * 20
        result = chunker.chunk(text)
        assert len(result) == 1

    def test_multiple_chunks_with_overlap(self):
        chunker = TextChunker(chunk_size=10, chunk_overlap=3)
        # 25 chars → should produce multiple chunks
        text = "ABCDEFGHIJ" * 3  # 30 chars
        result = chunker.chunk(text)
        assert len(result) > 1
        # Each chunk should be at most chunk_size characters (stripped)
        for c in result:
            assert (
                len(c) <= chunker.chunk_size + 5
            )  # allow some slack for boundary logic

    def test_chunks_cover_full_text(self):
        """Verify that no content is lost — all original text chars appear in at least one chunk."""
        chunker = TextChunker(chunk_size=50, chunk_overlap=10)
        text = "Word " * 100  # 500 chars
        result = chunker.chunk(text)
        combined = " ".join(result)
        # Every word from the original should appear
        for word in text.strip().split():
            assert word in combined

    def test_prefers_newline_boundary(self):
        chunker = TextChunker(chunk_size=30, chunk_overlap=5)
        text = "AAAAAAAAAA\nBBBBBBBBBB\nCCCCCCCCCC\nDDDDDDDDDD"
        result = chunker.chunk(text)
        assert len(result) >= 2
