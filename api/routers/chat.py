from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from api.dependencies import get_chat_service, get_embedding_service, get_vector_store
from core.config import settings
from core.models import ChatRequest, ChatResponse, ChatSource, DocumentChunk
from core.prompts import RAG_SYSTEM_PROMPT, USER_QUERY_TEMPLATE

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from core.embeddings import EmbeddingService
    from core.llm import BaseChatService
    from core.vector_store import VectorStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat_retrieval(
    request: ChatRequest,
    chat_service: BaseChatService = Depends(get_chat_service),  # noqa: B008
    embedding_service: EmbeddingService = Depends(get_embedding_service),  # noqa: B008,
    vector_store: VectorStore = Depends(get_vector_store),  # noqa: B008
) -> ChatResponse | StreamingResponse:

    try:
        query_embedding = await embedding_service.embed_query(request.query)

        top_k, min_score = request.parameters.get_search_params(
            settings.MAX_NUMBER_OF_HITS, settings.MIN_SCORE
        )
        llm_params = request.parameters.get_llm_params()

        hits: list[tuple[DocumentChunk, float]] = await vector_store.search(
            query_embedding, limit=top_k
        )

        sources = [
            ChatSource(
                content=chunk.content,
                source=chunk.metadata.source,
                page_number=chunk.metadata.page_number,
                score=score,
            )
            for chunk, score in hits
            if score >= min_score
        ]

        context_block = "\n---\n".join([s.content for s in sources])
        if not context_block:
            context_block = "No relevant document chunks were found for this query."

        messages = [
            {"role": "system", "content": RAG_SYSTEM_PROMPT.format(context=context_block)},
        ]

        for msg in request.history:
            messages.append({"role": msg.role, "content": msg.content})

        messages.append(
            {"role": "user", "content": USER_QUERY_TEMPLATE.format(query=request.query)}
        )

        if request.stream:

            async def stream_generator() -> AsyncIterator[str]:
                try:
                    yield json.dumps({"sources": [s.model_dump() for s in sources]}) + "\n"

                    async for chunk in chat_service.chat_stream(messages, **llm_params):
                        yield json.dumps({"answer": chunk}) + "\n"
                except Exception as e:
                    logger.exception(f"Streaming error: {e}")
                    yield json.dumps({"error": "LLM Service interrupted. Please try again."}) + "\n"

            return StreamingResponse(stream_generator(), media_type="application/x-ndjson")

        answer = await chat_service.chat(messages, **llm_params)
        return ChatResponse(answer=answer, sources=sources)

    except Exception as e:
        logger.exception("Chat endpoint failed.")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}") from e
