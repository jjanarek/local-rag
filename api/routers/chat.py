from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from api.dependencies import get_chat_service, get_embedding_service, get_vector_store
from core.config import settings
from core.models import ChatRequest, ChatResponse, ChatSource, DocumentChunk
from core.prompts import RAG_SYSTEM_PROMPT, USER_QUERY_TEMPLATE

if TYPE_CHECKING:
    from core.embeddings import EmbeddingService
    from core.llm import BaseChatService
    from core.vector_store import VectorStore

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat_retrieval(
    request: ChatRequest,
    chat_service: BaseChatService = Depends(get_chat_service),  # noqa: B008
    embedding_service: EmbeddingService = Depends(get_embedding_service),  # noqa: B008,
    vector_store: VectorStore = Depends(get_vector_store),  # noqa: B008
) -> ChatResponse:

    query_embedding = await embedding_service.embed_query(request.query)

    hits: list[tuple[DocumentChunk, float]] = await vector_store.search(
        query_embedding, limit=settings.MAX_NUMBER_OF_HITS
    )

    sources = [
        ChatSource(
            content=chunk.content,
            source=chunk.metadata.source,
            page_number=chunk.metadata.page_number,
            score=score,
        )
        for chunk, score in hits
        if score >= settings.MIN_SCORE
    ]

    context_block = "\n---\n".join([s.content for s in sources])
    if not context_block:
        context_block = "No relevant document chunks were found for this query."

    messages = [
        {"role": "system", "content": RAG_SYSTEM_PROMPT.format(context=context_block)},
    ]

    for msg in request.history:
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": USER_QUERY_TEMPLATE.format(query=request.query)})

    answer = await chat_service.chat(messages)

    return ChatResponse(answer=answer, sources=sources)
