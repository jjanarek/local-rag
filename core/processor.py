from typing import TYPE_CHECKING

from core.document_processor.cleaner import DocumentCleaner
from core.document_processor.factory import DocumentReaderFactory

if TYPE_CHECKING:
    from pathlib import Path

    from core.models import Document


class DocumentProcessor:
    """
    Document processing pipeline
    Orchestrator for the document processing pipeline. Handles extraction, cleaning,
    and filtering of documents.
    """

    def __init__(self) -> None:
        self.factory = DocumentReaderFactory()

    async def process_file(
        self,
        file_path: Path,
    ) -> list[Document]:
        reader = self.factory.get_reader(file_path)

        documents = await reader.load(file_path)

        for doc in documents:
            DocumentCleaner.clean_document(doc)

        documents = DocumentCleaner.remove_repetitive_lines(documents)

        cleaned_documents = [doc for doc in documents if doc.content.strip()]

        return cleaned_documents
