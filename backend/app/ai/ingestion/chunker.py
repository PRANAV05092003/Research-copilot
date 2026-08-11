from typing import Any


class Chunker:
    def __init__(self, target_tokens: int = 800, overlap_tokens: int = 120):
        self.target_tokens = target_tokens
        self.overlap_tokens = overlap_tokens
        # Heuristic: 1 token ~= 4 chars
        self.target_chars = target_tokens * 4
        self.overlap_chars = overlap_tokens * 4

    def chunk(self, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Splits pages into overlapping chunks while retaining page number mapping.
        Returns a list of dicts: {"text": str, "page_number": int, "token_count": int}
        """
        chunks = []

        for page in pages:
            text = page["text"]
            page_num = page["page_number"]

            # Simple paragraph/sentence fallback splitting
            # For this MVP, we use character-based sliding window over the text
            start = 0
            text_len = len(text)

            while start < text_len:
                end = start + self.target_chars

                # Attempt to snap to the nearest sentence boundary (period + space) backwards
                if end < text_len:
                    nearest_boundary = text.rfind(". ", start, end)
                    if nearest_boundary != -1 and nearest_boundary > start + (
                        self.target_chars // 2
                    ):
                        end = nearest_boundary + 1

                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunks.append(
                        {
                            "text": chunk_text,
                            "page_number": page_num,
                            "token_count": len(chunk_text) // 4,
                        }
                    )

                start = end - self.overlap_chars
                if start >= text_len or end >= text_len:
                    break

        return chunks
