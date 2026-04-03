from __future__ import annotations

from typing import TYPE_CHECKING

from .pdf_reader import PDFReader
from .text_reader import TextReader

if TYPE_CHECKING:
    from pathlib import Path

    from .base import BaseReader


class DocumentReaderFactory:
    """
    Factory to return appropriate reader for a file extension.
    """

    _readers: dict[str, type[BaseReader]] = {
        ".pdf": PDFReader,
        ".md": TextReader,
        ".txt": TextReader,
    }
    _supported_extensions_str: str = ", ".join(_readers.keys())

    @classmethod
    def get_reader(cls, file_path: Path) -> BaseReader:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_extension = file_path.suffix.lower()
        reader_cls = cls._readers.get(file_extension)

        if not reader_cls:
            raise ValueError(
                f"Unsupported extension: {file_extension}."
                f"List of supported extensions: {cls._supported_extensions_str}"
            )

        return reader_cls()
