from __future__ import annotations

from typing import TYPE_CHECKING

from anyio.to_thread import run_sync
from sentence_transformers import SentenceTransformer

if TYPE_CHECKING:
    import numpy as np

    from core.models import DocumentChunk


class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        """
        Lazy loader for the embedding model.
        """

        if self._model is None:
            # load the model on demand
            self._model = SentenceTransformer(self.model_name)
        return self._model

    async def embed_chunks(self, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        """
        Generate embeddings for a list of DocumentChunks.
        IMPORTANT: Updates the chunks in place.
        """
        if not chunks:
            return []

        texts = [chunk.content for chunk in chunks]

        embeddings = await run_sync(self._embed_sync, texts)

        for chunk, vector in zip(chunks, embeddings, strict=True):
            chunk.embedding = vector.tolist()
            chunk.embedding_model_name = self.model_name

        return chunks

    def _embed_sync(self, texts: list[str]) -> np.ndarray:
        """Wrapper for synchronous calculation of embeddings"""
        return self.model.encode(texts, show_progress_bar=False)
