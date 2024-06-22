import os
import shutil
import unittest
from unittest.mock import patch, Mock
from src.epub_file_downloader.epub_file_downloader import EpubFileDownloader
from src.file_manager.file_manager import OUTPUT_DIR


class TestEbookDownloader(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://example.com"
        self.downloader = EpubFileDownloader(self.base_url, 'test_ebook')
        self.file_path = "test_file.txt"
        self.longer_file_path = "subdir/test_file.txt"

        self.test_output_dir = os.path.join(OUTPUT_DIR, 'test_ebook')
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
        os.makedirs(self.test_output_dir, exist_ok=True)

    @patch('requests.get')
    def test_should_download_file_successfully_given_simple_filepath(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"Test file content"
        mock_get.return_value = mock_response

        result = self.downloader.download_file(self.file_path)

        self.assertTrue(result)
        local_path = os.path.join(self.test_output_dir, self.file_path)
        self.assertTrue(os.path.exists(local_path))

        with open(local_path, 'rb') as file:
            content = file.read()
            self.assertEqual(content, b"Test file content")

    @patch('requests.get')
    def test_should_not_create_file_when_file_not_found(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.content = None
        mock_get.return_value = mock_response

        result = self.downloader.download_file(self.file_path)

        self.assertFalse(result)
        local_path = os.path.join(self.test_output_dir, self.file_path)
        self.assertFalse(os.path.exists(local_path))

    @patch('requests.get')
    def test_should_create_directory_to_download_file_successfully_given_filepath(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"Test file content"
        mock_get.return_value = mock_response

        result = self.downloader.download_file(self.longer_file_path)

        self.assertTrue(result)
        local_path = os.path.join(self.test_output_dir, self.longer_file_path)
        self.assertTrue(os.path.exists(local_path))

        with open(local_path, 'rb') as file:
            content = file.read()
            self.assertEqual(content, b"Test file content")

    def test_should_successfully_extract_opf_path_from_xml(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(self.test_output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.test_output_dir, 'META-INF'), exist_ok=True)
        container_xml_path = os.path.join(self.test_output_dir, 'META-INF', 'container.xml')
        container_xml_content = '''
            <container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
            <rootfiles>
            <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
            </rootfiles>
            </container>
        '''
        with open(container_xml_path, 'w') as file:
            file.write(container_xml_content)

        result = self.downloader.extract_content_opf_path_from_xml(os.path.join("META-INF", "container.xml"))
        expected_path = "content.opf"
        self.assertEqual(expected_path, result)

    # def tearDown(self):
    #     if os.path.exists(OUTPUT_DIR):
    #         shutil.rmtree(OUTPUT_DIR)


if __name__ == '__main__':
    unittest.main()
