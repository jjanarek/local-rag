from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI

from api.routers import ingestion
from core.config import settings
from core.embeddings import setup_embedding_service
from core.llm import setup_chat_service
from core.qdrant_store import setup_qdrant_service

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup logic: load models and connections
    app.state.embedding_service = setup_embedding_service(model_name=settings.EMBEDDING_MODEL_NAME)
    app.state.vector_store = setup_qdrant_service(
        url=settings.QDRANT_URL, collection_name=settings.COLLECTION_NAME
    )
    app.state.chat_service = setup_chat_service(
        base_url=settings.OLLAMA_BASE_URL, model=settings.LLM_MODEL
    )
    yield

    # Shutdown
    await app.state.vector_store.close()


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.include_router(ingestion.router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "app": settings.APP_NAME}
