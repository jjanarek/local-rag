import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from api.dependencies import (
    get_chat_service,
    get_embedding_service,
    get_ingestion_pipeline,
    get_vector_store,
)
from api.main import app
from core.models import DocumentChunk, DocumentMetadata, IngestionResult


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://text") as ac:
        response = await ac.get("/health")

    assert response.status_code == 200
    assert response.json().get("status") == "ok"


@pytest.mark.asyncio
async def test_chat_non_streaming():
    mock_chat = AsyncMock()
    mock_chat.chat.return_value = "This is a mock answer."

    mock_embed = AsyncMock()
    mock_embed.embed_query.return_value = [0.1] * 384

    mock_vector = AsyncMock()
    mock_hit = (
        DocumentChunk(
            chunk_id="1",
            content="Mock content",
            metadata=DocumentMetadata(source="test.pdf", page_number=1, file_type="pdf"),
            chunk_index=0,
        ),
        0.95,  # score
    )
    mock_vector.search.return_value = [mock_hit]

    app.dependency_overrides[get_chat_service] = lambda: mock_chat
    app.dependency_overrides[get_embedding_service] = lambda: mock_embed
    app.dependency_overrides[get_vector_store] = lambda: mock_vector

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {"query": "Hello", "stream": False}
        response = await ac.post("/chat/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "This is a mock answer."
    assert len(data["sources"]) == 1
    assert data["sources"][0]["source"] == "test.pdf"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_chat_streaming():
    mock_chat = MagicMock()
    mock_chat.chat = AsyncMock(return_value="Fallback answer.")

    async def mock_generator(*args, **kwargs):
        yield "Hello"
        yield " world"

    mock_chat.chat_stream = mock_generator

    mock_embed = AsyncMock()
    mock_embed.embed_query.return_value = [0.1] * 384

    mock_vector = AsyncMock()
    mock_vector.search.return_value = []

    app.dependency_overrides[get_chat_service] = lambda: mock_chat
    app.dependency_overrides[get_embedding_service] = lambda: mock_embed
    app.dependency_overrides[get_vector_store] = lambda: mock_vector

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"query": "Hello", "stream": True}

        async with client.stream("POST", "/chat/", json=payload) as response:
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/x-ndjson"

            lines = []
            async for line in response.aiter_lines():
                if line.strip():
                    lines.append(json.loads(line))

    assert len(lines) >= 3
    assert "sources" in lines[0]
    assert lines[1]["answer"] == "Hello"
    assert lines[2]["answer"] == " world"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_ingest_file_success():
    mock_pipeline = AsyncMock()
    mock_pipeline.ingest_file.return_value = IngestionResult(
        status="success", file_path="test.txt", chunks_count=5, source="test.txt", duration=1.2
    )

    app.dependency_overrides[get_ingestion_pipeline] = lambda: mock_pipeline

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        files = {"file": ("test.txt", b"Hello World", "text/plain")}
        response = await client.post("/ingest/file", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["chunks_count"] == 5

    mock_pipeline.ingest_file.assert_called_once()
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_ingest_unsupported():

    # To prevent provider from crashing on enmtpy app.state:
    app.dependency_overrides[get_ingestion_pipeline] = lambda: MagicMock()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        files = {"file": ("random.exe", b"bad code", "application/x-msdownload")}
        response = await client.post("/ingest/file", files=files)

    assert response.status_code == 400
    assert "not supported" in response.json()["detail"]
