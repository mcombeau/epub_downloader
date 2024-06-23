from src.epub_locator.epub_handler import EpubHandler


class DefaultHandler(EpubHandler):
    def get_epub_base_url(self) -> str:
        self.ebook_name = self.url.split("/")[-1].split(".")[0]
        return self.url
