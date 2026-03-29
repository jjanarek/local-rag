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
