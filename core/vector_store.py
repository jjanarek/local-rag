from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.models import DocumentChunk


class VectorStore(ABC):
    @abstractmethod
    async def upsert(self, chunks: list[DocumentChunk]) -> None:
        """
        Save embeddings in the vector database.
        """
        pass

    @abstractmethod
    async def search(
        self, query_vector: list[float], limit: int
    ) -> list[tuple[DocumentChunk, float]]:
        """
        Find similar vectors to the query vector.
        """
        pass

    @abstractmethod
    async def delete(self, source_name: str) -> None:
        """
        Remove chunks for a given document.
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the connection to the vector store."""
        pass
