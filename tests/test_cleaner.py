from core.document_processor.cleaner import DocumentCleaner
from core.models import Document, DocumentMetadata


def test_clean_whitespaces():
    dirty_text = "  Hello   \t  World!  \n\n\n\nNew Paragraph  "
    cleaned = DocumentCleaner.clean_whitespaces(dirty_text)
    assert cleaned == "Hello World!\n\nNew Paragraph"


def test_normalize_unicode():
    dirty_text = "ﬁﬃ 1⁄2"
    cleaned = DocumentCleaner.normalize_unicode(dirty_text)
    assert cleaned == "fiffi 1/2"


def test_standardize_bullet_points():
    dirty_text = "• Point 1\n* Point 2\n· Point 3"
    cleaned = DocumentCleaner.standardize_bullet_points(dirty_text)
    assert cleaned == "- Point 1\n- Point 2\n- Point 3"


def test_remove_control_characters():
    dirty_text = "Hello\x00World\x1f!"
    cleaned = DocumentCleaner.remove_control_characters(dirty_text)
    assert cleaned == "HelloWorld!"


def test_repair_hyphenation():
    dirty_text = "This is a multi-\nline word."
    cleaned = DocumentCleaner.repair_hyphenation(dirty_text)
    assert cleaned == "This is a multiline word."


def test_remove_empty_lines():
    dirty_text = "Line 1\n   \nLine 2"
    cleaned = DocumentCleaner.remove_empty_lines(dirty_text)
    assert cleaned == "Line 1\nLine 2"


def test_strip_markdown_noise():
    dirty_text = "Line 1\n---\nLine 2\n<p>Some HTML</p>\n![](image.png)"
    cleaned = DocumentCleaner.strip_markdown_noise(dirty_text)
    assert cleaned == "Line 1\n\nLine 2\nSome HTML\n"


def test_remove_repetitive_lines():
    metadata = DocumentMetadata(source="test.pdf", page_number=3, file_type=".pdf")
    docs = [
        Document(
            content="CONFIDENTIAL REPORT\nThis is the actual content of page 1.\nCopyright 2024",
            metadata=metadata,
        ),
        Document(
            content="CONFIDENTIAL REPORT\nThis is the actual content of page 2.\nCopyright 2024",
            metadata=metadata,
        ),
        Document(
            content="CONFIDENTIAL REPORT\nThis is the actual content of page 3.\nCopyright 2024",
            metadata=metadata,
        ),
    ]

    cleaned_docs = DocumentCleaner.remove_repetitive_lines(docs)
    test_repetitive: bool = "CONFIDENTIAL REPORT" in cleaned_docs[0].content
    assert not test_repetitive

    test_actual: bool = "This is the actual content of page 1." in cleaned_docs[0].content
    assert test_actual
