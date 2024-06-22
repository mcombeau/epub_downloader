import unittest
from unittest.mock import patch, Mock

from src.epub_locator.epub_locator import EpubLocator


class TestEpubLocator(unittest.TestCase):

    def setUp(self):
        self.non_epub_pub_url = "https://www.readanybook.com/ebook/it-book-565296"
        self.epub_pub_url = "https://www.epub.pub/book/it-by-stephen-king"
        self.spread_url = "https://spread.epub.pub/epub/5a5827247412f4000781f18e"
        self.content_opf_url = "https://asset.epub.pub/epub/it-by-stephen-king-1.epub/content.opf"
        self.base_epub_pub_url = "https://asset.epub.pub/epub/it-by-stephen-king-1.epub"

        self.initial_response_html = '''
            <html> <body> <a class="btn btn-primary btn-read text-truncate" 
            data-domain="https://spread.epub.pub" data-readid="5a5827247412f4000781f18e" target="_blank" title="Read 
            Online(Swipe version)">Read Online(Swipe version)</a> </body> </html>
            '''
        self.spread_response_html = '''
            <html> <body> 
            <input type="hidden" name="assetUrl" id="assetUrl" value="https://asset.epub.pub/epub/it-by-stephen-king-1.epub/content.opf">
            </body> </html>
            '''

    def mock_requests_get(self, url):
        if url == self.epub_pub_url:
            return self._create_mock_response(self.initial_response_html)
        elif url == self.spread_url:
            return self._create_mock_response(self.spread_response_html)
        else:
            raise RuntimeError(f"Unexpected URL: {url}")

    def _create_mock_response(self, html_content):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode('utf-8')
        return mock_response

    @patch('src.epub_locator.epub_locator.requests.get')
    def test_should_return_url_given_non_epub_pub_url(self, mock_get):
        locator = EpubLocator(self.non_epub_pub_url)
        result = locator.get_epub_base_url()

        mock_get.assert_not_called()

        expected_url = self.non_epub_pub_url

        self.assertEqual(expected_url, result)

    @patch('src.epub_locator.epub_locator.requests.get')
    def test_should_return_read_online_spread_url_given_epub_pub_url(self, mock_get):
        mock_get.return_value = self._create_mock_response(self.initial_response_html)

        locator = EpubLocator(self.epub_pub_url)
        result = locator._get_epub_pub_spread_url()

        mock_get.assert_called_once_with(self.epub_pub_url)

        expected_url = self.spread_url
        self.assertEqual(expected_url, result)

    @patch('src.epub_locator.epub_locator.requests.get')
    def test_should_return_ebook_opf_url_given_epub_pub_spread_url(self, mock_get):
        mock_get.return_value = self._create_mock_response(self.spread_response_html)

        locator = EpubLocator(self.spread_url)
        result = locator._get_epub_pub_ebook_content_opf_url(self.spread_url)

        mock_get.assert_called_once_with(self.spread_url)

        expected_url = self.content_opf_url
        self.assertEqual(expected_url, result)

    @patch('src.epub_locator.epub_locator.requests.get')
    def test_should_return_epub_pub_content_opf_url_given_epub_pub_url(self, mock_get):
        mock_get.side_effect = self.mock_requests_get

        locator = EpubLocator(self.epub_pub_url)
        result = locator.get_epub_base_url()

        expected_url = self.base_epub_pub_url
        self.assertEqual(expected_url, result)

        calls = [
            unittest.mock.call(self.epub_pub_url),
            unittest.mock.call(self.spread_url)
        ]
        mock_get.assert_has_calls(calls, any_order=False)


if __name__ == '__main__':
    unittest.main()