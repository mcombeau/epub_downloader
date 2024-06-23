from abc import ABC, abstractmethod
from src.logster.logster import Logster


class EpubHandler(ABC):
    def __init__(self, url: str, logster: Logster):
        self.url = url
        self.logster = logster
        self.ebook_name: str = "unknown_ebook"

    @abstractmethod
    def get_epub_base_url(self) -> str:
        pass

    def get_ebook_name(self) -> str:
        return self.ebook_name
