from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    source: str = Field(..., description="The name or path of the source file.")
    page_number: int | None = Field(
        None, description="The page number from which the text was extracted"
    )
    file_type: str = Field(..., description="The original file format.")
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
