from src.epub_locator.epub_handler import EpubHandler
from src.epub_locator.epub_handler_factory import EpubHandlerFactory
from src.logster.logster import Logster


class EpubLocator:
    def __init__(self, logster: Logster, url: str):
        self.logster: Logster = logster
        self.url: str = url
        self.handler: EpubHandler = EpubHandlerFactory.get_handler(url, logster)

    def get_epub_base_url(self) -> str:
        return self.handler.get_epub_base_url()

    def get_ebook_name(self) -> str:
        return self.handler.get_ebook_name()
