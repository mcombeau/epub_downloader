import os

OUTPUT_DIR = "downloaded_epubs"


class FileManager:
    def __init__(self, ebook_name: str):
        self.ebook_name = ebook_name
        self.output_directory = os.path.join(OUTPUT_DIR, self.ebook_name)

    def setup_directories(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(self.output_directory, exist_ok=True)

    def save_content_to_file(self, content, path: str):
        full_path = os.path.join(self.output_directory, path)
        with open(full_path, "wb") as file:
            file.write(content)
        # log(f"Successfully fetched and saved: {url} to {path}")

