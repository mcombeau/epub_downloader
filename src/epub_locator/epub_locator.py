from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup, Tag

from logster.logster import Logster


class EpubLocator:
    def __init__(self, logster: Logster, url: str):
        self.logster: Logster = logster
        self.url: str = url
        self.ebook_name: str = "unknown_ebook"

    def get_epub_base_url(self) -> str:
        parse_result = urlparse(self.url)
        if parse_result.netloc == "www.epub.pub":
            spread_url: str = self._get_epub_pub_spread_url()
            content_opf_url: str = self._get_epub_pub_ebook_content_opf_url(spread_url)
            parts: list[str] = content_opf_url.split("/")
            epub_base_url_parts: list[str] = []
            for part in parts:
                epub_base_url_parts.append(part)
                if part.endswith(".epub"):
                    self.ebook_name = part.split('.')[0]
                    break
            epub_base_url: str = "/".join(epub_base_url_parts)
            self.logster.log(f"Determined EPUB base URL: {epub_base_url}")
            return epub_base_url
        else:
            self.logster.log(f"Determined EPUB base URL: {self.url}")
            self.ebook_name = self.url.split('/')[-1]
            return self.url

    def get_ebook_name(self) -> str:
        return self.ebook_name

    def _get_epub_pub_spread_url(self) -> str:
        response = requests.get(self.url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        read_online_button: str = soup.find("a", class_="btn-read")
        if not read_online_button or not isinstance(read_online_button, Tag):
            raise RuntimeError("Failed to find the 'Read Online' link.")

        domain: str = read_online_button.get("data-domain", "")
        spread_id: str = read_online_button.get("data-readid", "")
        read_online_url: str = f"{domain}/epub/{spread_id}"

        return read_online_url

    def _get_epub_pub_ebook_content_opf_url(self, spread_url: str) -> str:
        response = requests.get(spread_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        asset_url: str = soup.find("input", id="assetUrl")
        if (
            not asset_url
            or not isinstance(asset_url, Tag)
            or not asset_url.get("value")
        ):
            raise RuntimeError("Failed to find content.opf URL in the spread page.")
        content_opf_url: str = str(asset_url["value"])
        self.logster.log(f"Found content.opf URL: {content_opf_url}")
        return content_opf_url
