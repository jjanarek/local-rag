from __future__ import annotations

from typing import TYPE_CHECKING

from anyio.to_thread import run_sync

from core.models import Document, DocumentMetadata

from .base import BaseReader

if TYPE_CHECKING:
    from pathlib import Path


class TextReader(BaseReader):
    @property
    def supported_extensions(self) -> list[str]:
        return [".txt", ".md"]

    async def load(self, file_path: Path) -> list[Document]:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        def read_sync() -> str:
            with open(file_path, encoding="utf-8") as f:
                return f.read()

        content: str = await run_sync(read_sync)

        metadata = DocumentMetadata(
            source=str(file_path), file_type=file_path.suffix, page_number=None
        )
        return [Document(content=content, metadata=metadata)]
