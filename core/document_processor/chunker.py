from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING

import tiktoken
from anyio.to_thread import run_sync
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.models import DocumentChunk

if TYPE_CHECKING:
    from core.models import Document, DocumentMetadata


class DocumentChunker:
    MIN_CHUNK_TOKENS = 20

    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 40) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self._get_tokenizer_length,
            is_separator_regex=False,
            separators=["\n\n", "\n", " ", ""],
        )

    async def chunk_documents(self, documents: list[Document]) -> list[DocumentChunk]:
        """Public entry method to process multiple documents asynchronously."""
        return await run_sync(self._process_all_sync, documents)

    def _process_all_sync(self, documents: list[Document]) -> list[DocumentChunk]:
        all_chunks = []
        for doc in documents:
            all_chunks.extend(self._process_single_document(doc))
        return all_chunks

    def _process_single_document(self, document: Document) -> list[DocumentChunk]:
        """Logic for splitting one Document into multiple DocumentChunks"""
        context_block = self._create_context_block(document.metadata)
        raw_texts = self.splitter.split_text(document.content)

        chunks = []
        for i, text in enumerate(raw_texts):
            if self._get_tokenizer_length(text) < self.MIN_CHUNK_TOKENS:
                continue
            combined_text = f"{context_block}{text}"
            chunk_hash = self._create_chunk_id(text, document.metadata)
            chunks.append(
                DocumentChunk(
                    content=combined_text,
                    chunk_id=chunk_hash,
                    metadata=document.metadata,
                    chunk_index=i,
                )
            )

        return chunks

    def _create_chunk_id(self, content: str, metadata: DocumentMetadata) -> str:
        """Deterministic hashing for idempotency (content + sorted metadata)"""
        metadata_json = json.dumps(metadata.model_dump(), sort_keys=True)
        combined_string = f"{content}|{metadata_json}"

        return hashlib.sha256(combined_string.encode("utf-8")).hexdigest()

    def _create_context_block(self, metadata: DocumentMetadata) -> str:
        """The formatted [CONTEXT] block"""
        return f"[CONTEXT]\nSource: {metadata.source}\nPage: {metadata.page_number or 'N/A'}\n---\n"

    def _get_tokenizer_length(self, text: str) -> int:
        """Function for splitter length function."""
        # 'cl100k_base' is a standard for modern LLMs
        return len(self.encoder.encode(text))
