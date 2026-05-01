from __future__ import annotations

from typing import TYPE_CHECKING, cast

from fastapi import Request  # noqa: TC002

from core.processor import IngestionPipeline

if TYPE_CHECKING:
    from core.embeddings import EmbeddingService
    from core.llm import BaseChatService
    from core.vector_store import VectorStore


def get_vector_store(request: Request) -> VectorStore:
    """Provider for the vector database client."""
    return cast("VectorStore", request.app.state.vector_store)


def get_embedding_service(request: Request) -> EmbeddingService:
    """Provider for the embedding service."""
    return cast("EmbeddingService", request.app.state.embedding_service)


def get_chat_service(request: Request) -> BaseChatService:
    """Provider for the LLM chat service."""
    return cast("BaseChatService", request.app.state.chat_service)


def get_ingestion_pipeline(request: Request) -> IngestionPipeline:
    """
    Provider for the Ingestion Pipeline.
    A fresh orchestrator is created for every request, with singleton
    services for Vector Store and Embedding Service injected.
    """
    return IngestionPipeline(
        vector_store=request.app.state.vector_store, embedder=request.app.state.embedding_service
    )
