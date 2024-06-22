import os
import zipfile

from logger.logger import Logger

OUTPUT_DIR = "downloaded_epubs"


class FileManager:
    def __init__(self, logger: Logger, ebook_name: str):
        self.logger = logger
        self.ebook_name = ebook_name
        self.output_directory = os.path.join(OUTPUT_DIR, self.ebook_name)
        self.setup_directories()

    def setup_directories(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(self.output_directory, exist_ok=True)

    def save_content_to_file(self, content, path: str):
        full_path = os.path.join(self.output_directory, path)
        directory = os.path.dirname(full_path)
        os.makedirs(directory, exist_ok=True)

        with open(full_path, "wb") as file:
            file.write(content)
        self.logger.log(f"Successfully saved: {full_path}")

    def get_local_file_path(self, path):
        parts = path.split('/')
        acc = self.output_directory
        for part in parts:
            acc = os.path.join(acc, part)
        return acc

    def create_epub_archive(self):
        epub_path = os.path.join(OUTPUT_DIR, f"{self.ebook_name}.epub")
        self.logger.log(f"Creating EPUB at: {epub_path}")
        with zipfile.ZipFile(epub_path, "w", allowZip64=True) as epub:
            epub.write(
                os.path.join(self.output_directory, "mimetype"),
                "mimetype",
                compress_type=zipfile.ZIP_STORED,
            )
            for foldername, _, filenames in os.walk(self.output_directory):
                for filename in filenames:
                    if filename == "mimetype":
                        continue
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, self.output_directory)
                    self.logger.log(f"Adding {file_path} as {arcname} to EPUB")
                    epub.write(file_path, arcname)
        self.logger.log(f"EPUB file created: {epub_path}", override_verbose=True)
