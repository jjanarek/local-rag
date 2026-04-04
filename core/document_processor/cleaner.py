from __future__ import annotations

import re
import unicodedata
from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.models import Document


class DocumentCleaner:
    """
    Class used to clean Documents. The class works in step-by-step
    fashion to apply different filters on the Document's content.
    """

    @classmethod
    def clean_document(cls, document: Document) -> Document:
        """
        Main function for cleaning Documents.
        """
        text = document.content
        file_type = document.metadata.file_type.lower()

        text = cls.normalize_unicode(text)
        text = cls.remove_control_characters(text)

        if file_type == ".pdf":
            text = cls.repair_hyphenation(text)

        if file_type == ".md":
            text = cls.strip_markdown_noise(text)

        text = cls.standardize_bullet_points(text)
        text = cls.remove_empty_lines(text)
        text = cls.clean_whitespaces(text)

        document.content = text
        return document

    @classmethod
    def remove_repetitive_lines(
        cls, documents: list[Document], threshold: float = 0.8
    ) -> list[Document]:
        """
        Identify and remove lines that appear more than 'threshold' percent of documents.
        """
        if len(documents) < 3:
            return documents

        line_counts: Counter[str] = Counter()
        for doc in documents:
            lines = {line.strip() for line in doc.content.splitlines() if line.strip()}
            unique_lines = set(lines)
            line_counts.update(unique_lines)

        total_docs = len(documents)
        lines_to_remove = {
            line for line, count in line_counts.items() if (count / total_docs) >= threshold
        }

        for doc in documents:
            new_lines = [
                line for line in doc.content.splitlines() if line.strip() not in lines_to_remove
            ]
            doc.content = "\n".join(new_lines)

        return documents

    @staticmethod
    def clean_whitespaces(text: str) -> str:
        """
        Collapse newlines, remove multiple whitespaces, strip the string.
        """
        if not text:
            return ""
        # Collapse 3+ newlines to 2 (preserves paragraphs)
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Collapse whitespaces into a single space
        text = re.sub(r"[ \t]{2,}", " ", text)
        # Final strip
        return text.strip()

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """
        Normalize characters in the text.
        """
        if not text:
            return ""
        # Remove ligatures, fractions, etc
        return unicodedata.normalize("NFKC", text)

    @staticmethod
    def standardize_bullet_points(text: str) -> str:
        """
        Change all bulletpoints to "-" for consistency.
        """
        if not text:
            return ""
        bullets_pattern = r"[•·▪◦‣⁃*]"
        # Remove bullet point AND whitespace immediately after, replace with "- "
        text = re.sub(f"{bullets_pattern}[ \t]*", "- ", text)

        return text

    @staticmethod
    def remove_control_characters(text: str) -> str:
        """
        Remove non-printable characters found in PDFs
        """
        if not text:
            return ""

        # This pattern matches:
        # 1. \x00-\x08 (Null to Backspace)
        # 2. \x0B-\x0C (Vertical Tab and Form Feed)
        # 3. \x0E-\x1F (Shift Out to Unit Separator)
        # 4. \x7F-\x9F (Delete and C1 Control characters)
        # Notice we SKIP \x09 (Tab), \x0A (Line Feed), and \x0D (Carriage Return).
        control_chars_pattern = r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]"
        return re.sub(control_chars_pattern, "", text)

    @staticmethod
    def strip_markdown_noise(text: str) -> str:
        """
        Remove markdown artifacts from the file (links, horizontal rules, etc.)
        """
        if not text:
            return ""

        # Remove empty links and image tags:
        text = re.sub(r"!?\[\]\([^)]*\)", "", text)

        # Remove horizontal rules ---, ***, ___
        # Use re.MULTILINE to catch the starts of any line
        text = re.sub(r"^\s*([-*_])\s*(?:\1\s*){2,}\s*$", "", text, flags=re.MULTILINE)

        # Remove common HTML tags
        text = re.sub(r"<[^>]+>", "", text)

        return text

    @staticmethod
    def repair_hyphenation(text: str) -> str:
        """
        Join split words.
        """
        if not text:
            return ""
        # Pattern looks for alphanumeric char + hypen + newline +
        # (optional) whitespace + alphanumeric char
        pattern = r"(\w)-\n\s*(\w)"
        return re.sub(pattern, r"\1\2", text)

    @staticmethod
    def remove_empty_lines(text: str) -> str:
        """
        Remove addtional empty lines.
        """
        if not text:
            return ""
        return re.sub(r"^[ \t]+\n?", "", text, flags=re.MULTILINE)
