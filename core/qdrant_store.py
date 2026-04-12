from __future__ import annotations

import uuid

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from core.models import DocumentChunk, DocumentMetadata
from core.vector_store import VectorStore


class QdrantStore(VectorStore):
    def __init__(self, url: str, collection_name: str, api_key: str | None = None) -> None:
        self.url = url
        self.collection_name = collection_name
        self.api_key = api_key
        self.client = AsyncQdrantClient(url=self.url)
        self.collection = None

    async def _ensure_collection_exists(
        self,
    ) -> None:
        """
        Make sure the vector database contains the collection which is used to
        store/search vectors.
        """
        if not await self.client.collection_exists(self.collection_name):
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )

    async def upsert(self, chunks: list[DocumentChunk]) -> None:
        """
        Upsert DocumentChunks into the vector database.
        """
        await self._ensure_collection_exists()

        points = []
        for chunk in chunks:
            if not chunk.embedding:
                continue
            points.append(
                PointStruct(
                    id=self._get_uuid_for_qdrant(chunk.chunk_id),
                    vector=chunk.embedding,
                    payload={
                        "content": chunk.content,
                        "metadata": chunk.metadata.model_dump(),
                        "chunk_index": chunk.chunk_index,
                        "chunk_hash": chunk.chunk_id,
                    },
                )
            )
        if points:
            await self.client.upsert(collection_name=self.collection_name, points=points)

    def _get_uuid_for_qdrant(self, chunk_id: str) -> str:
        return str(uuid.UUID(chunk_id[:32]))

    async def search(self, query_vector: list[float], limit: int) -> list[DocumentChunk]:
        """
        Perform a search using a query vector.
        Returns a list of DocumentChunks
        """
        await self._ensure_collection_exists()

        response = await self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True,
        )

        results = []
        for hit in response.points:
            if not hit.payload:
                continue

            metadata = DocumentMetadata.model_validate(hit.payload["metadata"])

            chunk = DocumentChunk(
                chunk_id=hit.payload["chunk_hash"],
                content=hit.payload["content"],
                metadata=metadata,
                chunk_index=hit.payload["chunk_index"],
            )
            results.append(chunk)

        return results

    async def delete(self, source_name: str) -> None:
        """Delete the entries in vector database for a given source_name"""
        await self._ensure_collection_exists()

        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[FieldCondition(key="metadata.source", match=MatchValue(value=source_name))]
            ),
        )

    async def close(
        self,
    ) -> None:
        """Gracefully close the connection to QDrant vector database."""
        await self.client.close()
