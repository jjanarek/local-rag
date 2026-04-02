from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from core.models import Document


class BaseReader(ABC):
    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """
        Return a list of file extensions supported by this reader.
        Example: [".pdf"] or [".md", ".txt"]
        """
        pass

    @abstractmethod
    async def load(self, file_path: Path) -> list[Document]:
        """
        Asynchronously read a file and return a list of Document objects.
        """
        pass
