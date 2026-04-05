from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from core.document_processor import PDFReader, TextReader
from core.document_processor.cleaner import DocumentCleaner

if TYPE_CHECKING:
    from core.models import Document


@pytest.mark.asyncio
async def test_text_reader(tmp_path: Path):
    test_file = tmp_path / "document.txt"
    test_content = "Hello, this is document content."
    test_file.write_text(data=test_content)

    reader = TextReader()
    docs: list[Document] = await reader.load(test_file)

    assert docs[0].content == test_content
    assert docs[0].metadata.file_type == ".txt"
    assert docs[0].metadata.source == str(test_file)


@pytest.mark.asyncio
async def test_pdf_reader_integration(tmp_path):
    test_file = Path("tests/data/test.pdf")
    reader = PDFReader()
    docs = await reader.load(test_file)

    # number of pages
    assert len(docs) == 3
    assert docs[0].metadata.page_number == 1
    assert docs[1].metadata.page_number == 2
    assert docs[2].metadata.page_number == 3

    for doc in docs:
        DocumentCleaner.clean_document(doc)
    docs = DocumentCleaner.remove_repetitive_lines(docs)

    assert "multiline" in docs[0].content.lower()

    for doc in docs:
        assert "CONFIDENTIAL REPORT" not in doc.content
        assert "Internal use only" not in doc.content

    # assert .md cleaning was skipped
    assert "---" in docs[2].content
    assert "[Click Here]" in docs[2].content or "http" in docs[2].content
