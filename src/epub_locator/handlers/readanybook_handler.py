import requests
from bs4 import BeautifulSoup
from src.epub_locator.epub_handler import EpubHandler


class ReadAnyBookHandler(EpubHandler):
    def get_epub_base_url(self) -> str:
        response = requests.get(self.url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        link_div: str = soup.find('div', class_='links-row')
        if not link_div or 'data-link' not in link_div.attrs:
            raise RuntimeError("Failed to find the EPUB source URL on the page.")

        epub_url: str = link_div['data-link'].rstrip('/')
        self.logster.log(f"Extracted EPUB URL: {epub_url}")

        self.ebook_name = epub_url.split('/')[-1].split('.')[0]

        return epub_url
