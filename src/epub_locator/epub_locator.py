from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup, Tag


class EpubLocator:
    def __init__(self, url: str):
        self.url: str = url

    def get_epub_base_url(self) -> str:
        parse_result = urlparse(self.url)
        if parse_result.netloc == "www.epub.pub":
            spread_url = self._get_epub_pub_spread_url()
            content_opf_url = self._get_epub_pub_ebook_content_opf_url(spread_url)
            parts = content_opf_url.split("/")
            epub_base_url_parts = []
            for part in parts:
                epub_base_url_parts.append(part)
                if part.endswith(".epub"):
                    break
            epub_base_url = "/".join(epub_base_url_parts)
            return epub_base_url
        else:
            return self.url

    def _get_epub_pub_spread_url(self):
        response = requests.get(self.url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        read_online_button = soup.find("a", class_="btn-read")
        if not read_online_button or not isinstance(read_online_button, Tag):
            raise RuntimeError("Failed to find the 'Read Online' link.")

        domain = read_online_button.get("data-domain", "")
        directory = "epub"
        spread_id = read_online_button.get("data-readid", "")
        read_online_url = f"{domain}/{directory}/{spread_id}"

        return read_online_url

    def _get_epub_pub_ebook_content_opf_url(self, spread_url):
        response = requests.get(spread_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        asset_url = soup.find("input", id="assetUrl")
        if (
            not asset_url
            or not isinstance(asset_url, Tag)
            or not asset_url.get("value")
        ):
            raise RuntimeError("Failed to find content.opf URL in the spread page.")
        content_opf_url = str(asset_url["value"])
        # log(f"Found content.opf URL: {content_opf_url}")
        return content_opf_url



