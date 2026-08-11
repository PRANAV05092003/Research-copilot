from typing import Any

from app.ai.providers.base import LLMProvider


class ContextCompressor:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.compression_prompt = """
        You are a context compressor.
        Given the following search query and a document chunk, extract only the sentences or facts relevant to the query.
        If the chunk contains no relevant information, output exactly "NO_RELEVANCE".
        
        Query: {query}
        
        Chunk: {chunk_text}
        
        Extracted Context:
        """

    async def compress(self, query: str, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        compressed_chunks = []
        for chunk in chunks:
            prompt = self.compression_prompt.format(query=query, chunk_text=chunk.get("text", ""))
            response = await self.llm_provider.generate(prompt)
            if "NO_RELEVANCE" not in response.strip().upper():
                # Keep the chunk but replace the text with the compressed version
                compressed_chunk = chunk.copy()
                compressed_chunk["text"] = response.strip()
                compressed_chunks.append(compressed_chunk)

        return compressed_chunks
