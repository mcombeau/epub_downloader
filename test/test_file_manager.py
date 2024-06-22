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

        path = "test_file"
        content = "test content for file saving"

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

    def test_should_create_subdir_and_file_with_given_contents(self):
        self.file_manager.setup_directories()

        path = "subdir/test_file"
        content = "test content for file saving"

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

    def test_should_return_full_output_dir_path_to_file_given_file_path(self):
        subdir1 = "subdir1"
        subdir2 = "subdir2"
        subdir3 = "subdir3"
        file = "file.txt"
        path = f"{subdir1}/{subdir2}/{subdir3}/{file}"

        result = self.file_manager.get_local_file_path(path)
        expected_path = os.path.join(self.test_output_dir, self.ebook_name, subdir1, subdir2, subdir3, file)
        self.assertEqual(expected_path, result)

    def tearDown(self):
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)


if __name__ == '__main__':
    unittest.main()
