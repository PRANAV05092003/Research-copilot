import abc
from typing import Any


class LLMProvider(abc.ABC):
    @abc.abstractmethod
    async def generate(self, prompt: str, system: str | None = None, temperature: float = 0.0, seed: int | None = None) -> str:
        """Generate text from LLM"""

    @abc.abstractmethod
    async def generate_json(self, prompt: str, system: str | None = None, temperature: float = 0.0, seed: int | None = None) -> dict[str, Any]:
        """Generate structured JSON from LLM"""

class EmbeddingProvider(abc.ABC):
    @abc.abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """Embed a single search query"""

    @abc.abstractmethod
    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple document chunks"""
