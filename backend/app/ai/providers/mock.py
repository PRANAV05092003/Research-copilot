import hashlib
from typing import Any

from app.ai.providers.base import EmbeddingProvider, LLMProvider


class MockLLMProvider(LLMProvider):
    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.0,
        seed: int | None = None,
    ) -> str:
        # Deterministic dummy output based on prompt hash
        h = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        return f"Mock response for hash {h[:8]}. This is deterministic."

    async def generate_json(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.0,
        seed: int | None = None,
    ) -> dict[str, Any]:
        h = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        # Specific mock logic for citation verification testing
        if "verification" in (system or "").lower() or "entails" in (system or "").lower():
            # Assume prompt contains 'claim' and 'chunk' to mock entailment logic deterministically
            if "mock_unsupported" in prompt:
                return {"verdict": "unsupported", "score": 0.1, "reasoning": "Mock unsupported"}
            elif "mock_weak" in prompt:
                return {"verdict": "weak", "score": 0.6, "reasoning": "Mock weak"}
            else:
                return {"verdict": "verified", "score": 0.95, "reasoning": "Mock verified"}

        return {"mock_key": f"mock_value_{h[:8]}"}


class HashEmbeddingProvider(EmbeddingProvider):
    def _deterministic_vector(self, text: str) -> list[float]:
        """Generate a deterministic 384-d normalized vector based on text hash"""
        seed_val = int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16)

        vec = []
        state = seed_val
        for _ in range(384):
            state = (state * 1103515245 + 12345) & 0x7FFFFFFF
            val = (state / 0x7FFFFFFF) * 2 - 1
            vec.append(val)
        # Normalize
        norm = sum(x * x for x in vec) ** 0.5
        if norm == 0:
            norm = 1
        return [x / norm for x in vec]

    async def embed_query(self, text: str) -> list[float]:
        return self._deterministic_vector(text)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._deterministic_vector(t) for t in texts]
