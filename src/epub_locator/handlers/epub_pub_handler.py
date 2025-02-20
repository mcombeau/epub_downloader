from urllib.parse import urlparse
import re
import requests
from bs4 import BeautifulSoup, Tag

from src.epub_locator.epub_handler import EpubHandler


class EpubPubHandler(EpubHandler):
    def get_epub_base_url(self) -> str:
        domain = urlparse(self.url).netloc
        if domain == "spread.epub.pub" or domain == "continuous.epub.pub":
            content_opf_url: str = self._get_epub_pub_ebook_content_opf_url(self.url)
            epub_base_url: str = self._get_epub_base_url_from_specific_url(
                content_opf_url
            )
        elif domain == "asset.epub.pub":
            epub_base_url: str = self._get_epub_base_url_from_specific_url(self.url)
        else:
            spread_url: str = self._get_epub_pub_read_online_url()
            content_opf_url: str = self._get_epub_pub_ebook_content_opf_url(spread_url)
            epub_base_url: str = self._get_epub_base_url_from_specific_url(
                content_opf_url
            )
        self.logster.log(f"Determined EPUB base URL: {epub_base_url}")
        return epub_base_url

    def _get_epub_base_url_from_specific_url(self, url) -> str:
        self.logster.log(f"Parsing base url from url {url}")
        parts: list[str] = url.split("/")
        epub_base_url_parts: list[str] = []

        for part in parts:
            epub_base_url_parts.append(part)
            if part.endswith(".epub"):
                self.ebook_name = part.split(".")[0]
                break

        return "/".join(epub_base_url_parts)

    def _get_epub_pub_read_online_url(self) -> str:
        self.logster.log(f"Fetching read online link from url {self.url}")
        response = requests.get(self.url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        read_online_button: str = soup.find("a", class_="btn-read")
        if not read_online_button or not isinstance(read_online_button, Tag):
            raise RuntimeError("Failed to find the 'Read Online' link.")

        domain: str = read_online_button.get("data-domain", "")
        read_id: str = read_online_button.get("data-readid", "")
        read_online_url: str = f"{domain}/epub/{read_id}"

        return read_online_url

    def _get_epub_pub_ebook_content_opf_url(self, read_online_url: str) -> str:
        self.logster.log(f"Fetching content.opf from url {read_online_url}")
        response = requests.get(read_online_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        for script in soup.findAll("script"):
            potential_url = re.search(r'https?://\S+', str(script))
            if potential_url:
                if ".opf" in potential_url.group(0):
                    asset_url: str = potential_url.group(0).split('.opf')[0]+'.opf'
        if (
                not asset_url
        ):
            raise RuntimeError("Failed to find content.opf URL in the spread page.")

        return asset_url
