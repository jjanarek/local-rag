from __future__ import annotations

import time
from typing import TYPE_CHECKING

from core.document_processor.chunker import DocumentChunker
from core.document_processor.cleaner import DocumentCleaner
from core.document_processor.factory import DocumentReaderFactory
from core.models import IngestionResult

if TYPE_CHECKING:
    from pathlib import Path

    from core.embeddings import EmbeddingService
    from core.models import Document
    from core.vector_store import VectorStore


class DocumentProcessor:
    """
    Document processing pipeline
    Orchestrator for the document processing pipeline. Handles extraction, cleaning,
    and filtering of documents.
    """

    def __init__(self) -> None:
        self.factory = DocumentReaderFactory()

    async def process_file(self, file_path: Path, source_name: str | None = None) -> list[Document]:
        reader = self.factory.get_reader(file_path)

        documents = await reader.load(file_path)

        if source_name:
            for doc in documents:
                doc.metadata.source = source_name

        for doc in documents:
            DocumentCleaner.clean_document(doc)

        documents = DocumentCleaner.remove_repetitive_lines(documents)

        cleaned_documents = [doc for doc in documents if doc.content.strip()]

        return cleaned_documents


class IngestionPipeline:
    """
    High-level orchestrator for ingesting files into RAG system.
    Coordinates: extraction, cleaning, chunking, embedding, and storing documents.
    """

    def __init__(self, vector_store: VectorStore, embedder: EmbeddingService) -> None:
        """
        Initialize the pipeline with a vector store.
        Args:
            vector_store: destination for processed embeddings
        """

        self.embedder = embedder
        self.vector_store = vector_store

        # Lightweight pipeline-specific artifacts
        self.processor = DocumentProcessor()
        self.chunker = DocumentChunker()

    async def ingest_file(
        self, file_path: Path, original_filename: str | None = None
    ) -> IngestionResult:
        """
        Process a single file from raw bytes to vector store.
        This method contains the actual recipe for ingesting files into vector database.
        The recipe is performed step by step so that the errors are handled gracefully.
        """
        start_time = time.perf_counter()
        source_name = original_filename or file_path.name

        try:
            documents = await self.processor.process_file(file_path, source_name=source_name)
            if not documents:
                return IngestionResult(
                    status="skipped",
                    file_path=str(file_path),
                    source=source_name,
                    message="No text content was extracted from the file.",
                )
            chunks = await self.chunker.chunk_documents(documents)

            # Embedd the chunks
            await self.embedder.embed_chunks(chunks)

            # Store vector
            await self.vector_store.upsert(chunks)

            duration = time.perf_counter() - start_time
            return IngestionResult(
                status="success",
                file_path=str(file_path),
                source=documents[0].metadata.source,
                chunks_count=len(chunks),
                duration=round(duration, 2),
                message="Ingestion successful.",
            )
        except Exception as e:
            duration = time.perf_counter() - start_time
            return IngestionResult(
                status="error",
                file_path=str(file_path),
                source=source_name,
                duration=round(duration, 2),
                message=f"Ingestion failed: {str(e)}",
            )
