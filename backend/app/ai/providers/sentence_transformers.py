from app.ai.providers.base import EmbeddingProvider
from app.config import settings


class SentenceTransformersEmbeddingProvider(EmbeddingProvider):
    def __init__(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        except ImportError:
            raise ImportError(
                "sentence-transformers is not installed. Run `pip install sentence-transformers`"
            )

    async def embed_query(self, text: str) -> list[float]:
        # encode returns numpy array, convert to list of floats
        from typing import cast

        vector = self.model.encode(text)
        return cast(list[float], vector.tolist())

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # batch encode
        from typing import cast

        vectors = self.model.encode(texts)
        return [cast(list[float], vec.tolist()) for vec in vectors]
