from urllib.parse import urlparse

from src.epub_locator.handlers.default_handler import DefaultHandler
from src.epub_locator.handlers.epub_pub_handler import EpubPubHandler
from src.logster.logster import Logster

EPUB_PUB_DOMAINS = ["www.epub.pub", "spread.epub.pub", "asset.epub.pub", "continuous.epub.pub"]


class EpubHandlerFactory:
    @staticmethod
    def get_handler(url: str, logster: Logster):
        domain = urlparse(url).netloc
        if domain in EPUB_PUB_DOMAINS:
            logster.log(f"Using epub.pub handler for url: {url}")
            return EpubPubHandler(url, logster)
        else:
            logster.log(f"Using default handler for url: {url}")
            return DefaultHandler(url, logster)
