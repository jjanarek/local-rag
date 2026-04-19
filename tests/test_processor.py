from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest

from core.processor import DocumentProcessor, IngestionPipeline

if TYPE_CHECKING:
    from core.models import DocumentChunk


@pytest.mark.asyncio
async def test_document_processor_fill_pipeline():
    test_file = Path("tests/data/test.pdf")
    processor = DocumentProcessor()

    docs = await processor.process_file(test_file)

    assert len(docs) == 3
    assert "multiline" in docs[0].content.lower()
    assert "CONFIDENTIAL REPORT" not in docs[0].content


@pytest.mark.asyncio
async def test_ingestion_pipeline_success():
    mock_vector_store = AsyncMock()
    mock_embedder = AsyncMock()

    async def mock_embed_logic(chunks: list[DocumentChunk]):
        for chunk in chunks:
            # fake vector
            chunk.embedding = [0.1, 0.2, 0.3]
        return chunks

    mock_embedder.embed_chunks.side_effect = mock_embed_logic

    pipeline = IngestionPipeline(vector_store=mock_vector_store, embedder=mock_embedder)

    test_file = Path("tests/data/test.pdf")
    result = await pipeline.ingest_file(test_file)

    assert result.status == "success"
    assert result.chunks_count > 0
    assert result.source == "test.pdf"
    mock_embedder.embed_chunks.assert_called_once()
    mock_vector_store.upsert.assert_called_once()

    # Get the first arg for the upsert method
    called_chunks = mock_vector_store.upsert.call_args[0][0]
    assert all(c.embedding is not None for c in called_chunks)
