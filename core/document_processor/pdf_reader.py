from __future__ import annotations

from typing import TYPE_CHECKING

from anyio.to_thread import run_sync
from pypdf import PdfReader

from core.models import Document, DocumentMetadata

from .base import BaseReader

if TYPE_CHECKING:
    from pathlib import Path


class PDFReader(BaseReader):
    @property
    def supported_extensions(self) -> list[str]:
        return [".pdf"]

    async def load(self, file_path: Path) -> list[Document]:
        """
        Extracts a list of documents page-by-page from a PDF file.
        """

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        def read_sync() -> list[Document]:
            with open(file_path, "rb") as f:
                reader = PdfReader(f)
                total_pages = len(reader.pages)
                list_of_docs = []

                for num_page, page in enumerate(reader.pages, start=1):
                    page_content = page.extract_text()
                    page_content = page_content.strip() if page_content else ""
                    page_metadata = DocumentMetadata(
                        source=str(file_path.name),
                        page_number=num_page,
                        file_type=file_path.suffix,
                        extra={"total_pages": total_pages},
                    )
                    list_of_docs.append(Document(content=page_content, metadata=page_metadata))

            return list_of_docs

        list_of_documents: list[Document] = await run_sync(read_sync)

        return list_of_documents
