import os
import shutil
import unittest

from src.file_manager.file_manager import FileManager, OUTPUT_DIR


class TestFileManager(unittest.TestCase):
    def setUp(self):
        self.ebook_name = 'test_ebook'
        self.test_output_dir = OUTPUT_DIR
        self.file_manager = FileManager(self.ebook_name)

        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)

    def test_should_create_output_and_ebook_directories(self):
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)

        self.file_manager.setup_directories()

        self.assertTrue(os.path.isdir(self.test_output_dir), f"{self.test_output_dir} should be a directory.")
        self.assertTrue(os.path.isdir(os.path.join(self.test_output_dir, self.ebook_name)),
                        f"{os.path.join(self.test_output_dir, self.ebook_name)} should be a directory.")

    def test_should_create_file_with_given_contents(self):
        self.file_manager.setup_directories()

        path = "toc.ncx"
        content = '''
        <?xml version='1.0' encoding='utf-8'?>
        <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="en">
          <head>
            <meta content="e141d23d-add6-4018-b8bb-7fa5984f9a4b" name="dtb:uid"/>
            <meta content="2" name="dtb:depth"/>
            <meta content="calibre (0.7.44)" name="dtb:generator"/>
            <meta content="0" name="dtb:totalPageCount"/>
            <meta content="0" name="dtb:maxPageNumber"/>
          </head>
          <docTitle>
            <text>It</text>
          </docTitle>
          <navMap>
            <navPoint id="df4d1e16-0408-431b-9c4f-677f91496bd8" playOrder="1">
              <navLabel>
                <text>Start</text>
              </navLabel>
              <content src="titlepage.xhtml"/>
            </navPoint>
          </navMap>
        </ncx>
        '''

        byte_content = content.encode('utf-8')

        expected_path = os.path.join(self.test_output_dir, self.ebook_name, path)
        if os.path.exists(expected_path):
            os.remove(expected_path)

        self.file_manager.save_content_to_file(byte_content, path)

        self.assertTrue(os.path.exists(expected_path), f"File {expected_path} should exist.")
        self.assertTrue(os.path.isfile(expected_path), f"{expected_path} should be a file.")

        with open(expected_path, 'rb') as file:
            file_content = file.read()
            self.assertEqual(file_content, byte_content, "File content does not match the expected content.")

    def tearDown(self):
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)


if __name__ == '__main__':
    unittest.main()
