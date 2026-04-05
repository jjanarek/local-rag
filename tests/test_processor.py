from pathlib import Path

import pytest

from core.processor import DocumentProcessor


@pytest.mark.asyncio
async def test_document_processor_fill_pipeline():
    test_file = Path("tests/data/test.pdf")
    processor = DocumentProcessor()

    docs = await processor.process_file(test_file)

    assert len(docs) == 3
    assert "multiline" in docs[0].content.lower()
    assert "CONFIDENTIAL REPORT" not in docs[0].content
