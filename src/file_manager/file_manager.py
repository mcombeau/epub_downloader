import os
import shutil
import zipfile

from src.logster.logster import Logster

OUTPUT_DIR = "downloaded_epubs"


class FileManager:
    def __init__(self, logster: Logster, ebook_name: str):
        self.logster: Logster = logster
        self.ebook_name: str = ebook_name
        self.output_directory: str = os.path.join(OUTPUT_DIR, self.ebook_name)
        self.setup_directories()

    def setup_directories(self) -> None:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(self.output_directory, exist_ok=True)

    def save_content_to_file(self, content, path: str) -> None:
        full_path: str = os.path.join(self.output_directory, path)
        directory: str = os.path.dirname(full_path)
        os.makedirs(directory, exist_ok=True)

        with open(full_path, "wb") as file:
            file.write(content)
        self.logster.log(f"Successfully saved: {full_path}")

    def get_local_file_path(self, path: str) -> str:
        parts: list[str] = path.split("/")
        acc: str = self.output_directory

        for part in parts:
            acc = os.path.join(acc, part)
        return acc

    def create_epub_archive(self) -> None:
        epub_path: str = os.path.join(OUTPUT_DIR, f"{self.ebook_name}.epub")

        self.logster.log(f"Creating EPUB at: {epub_path}")
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
                    self.logster.log(f"Adding {file_path} as {arcname} to EPUB")
                    epub.write(file_path, arcname)
        self.logster.log(f"EPUB file created: {epub_path}", override_verbose=True)

    def cleanup_epub_file_directory(self) -> None:
        if os.path.exists(self.output_directory):
            shutil.rmtree(self.output_directory)
