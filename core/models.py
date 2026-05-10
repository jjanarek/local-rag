from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DocumentMetadata(BaseModel):
    source: str = Field(..., description="The name or path of the source file.")
    file_type: str = Field(..., description="The original file format.")
    page_number: int | None = Field(
        default=None, description="The page number from which the text was extracted"
    )
    extra: dict[str, Any] = Field(default_factory=dict, description="Any additional metadata.")


class Document(BaseModel):
    content: str = Field(..., description="The extracted text content.")
    metadata: DocumentMetadata = Field(..., description="Metadata for the content.")


class DocumentChunk(BaseModel):
    chunk_id: str = Field(..., description="A unique hash of the content and metadata")
    content: str = Field(
        ..., description="The chunked text content (potentially with context prepended)"
    )
    metadata: DocumentMetadata = Field(
        ..., description="Metadata inherited from the parent document"
    )
    chunk_index: int = Field(..., description="The index of the chunk within the document.")
    embedding: list[float] | None = Field(
        default=None, description="The vector embedding for this chunk"
    )
    embedding_model_name: str | None = Field(
        default=None, description="The name of the model used to generate the embedding."
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="The UTC timestamp when this chunk was created.",
    )


class IngestionResult(BaseModel):
    status: str = Field(..., description="Status: 'success', 'error', or 'skipped'")
    file_path: str = Field(..., description="Path of the processed file.")
    chunks_count: int = Field(default=0, description="Number of chunks created and stored.")
    source: str | None = Field(default=None, description="Source identifier from metadata.")
    duration: float = Field(default=0.0, description="Time taken in seconds.")
    message: str | None = Field(default=None, description="Error message or success details.")
    processed_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="The UTC timestamp when the ingestion was completed.",
    )


class Message(BaseModel):
    role: str = Field(..., description="Role: system, user, or assistant")
    content: str = Field(..., description="Text content")


class ChatParameters(BaseModel):
    model_config = ConfigDict(extra="allow")

    top_k: int | None = Field(
        default=None, ge=1, le=50, description="Max number of retrieved documents."
    )
    min_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Minimal similarity score for retrieved documents for inference.",
    )

    def get_search_params(self, default_k: int, default_score: float) -> tuple[int, float]:
        return (
            self.top_k if self.top_k is not None else default_k,
            self.min_score if self.min_score is not None else default_score,
        )

    def get_llm_params(self) -> dict[Any, Any]:
        """Return only parameters intended for the LLM"""
        params = self.model_dump(exclude_none=True)
        params.pop("top_k", None)
        params.pop("min_score", None)
        return params


class ChatRequest(BaseModel):
    query: str = Field(..., description="The user's query.")
    history: list[Message] = Field(default_factory=list, description="Conversation history.")
    stream: bool = Field(default=False, description="Whether to stream the response.")
    parameters: ChatParameters = Field(
        default_factory=ChatParameters, description="Set of parameters for search and LLMs"
    )


class ChatSource(BaseModel):
    content: str = Field(..., description="The text chunk used as context.")
    source: str = Field(..., description="The source document name.")
    page_number: int | None = Field(None, description="The page number if applicable.")
    score: float = Field(..., description="The similarity score.")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="The generated response from the LLM.")
    sources: list[ChatSource] = Field(
        default_factory=list, description="The context chunks used for retrieval."
    )
