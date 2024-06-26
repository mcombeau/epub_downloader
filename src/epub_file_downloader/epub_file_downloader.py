import os.path
from http import HTTPStatus
from time import sleep
import requests
from bs4 import BeautifulSoup
from requests import HTTPError
from tqdm import tqdm

from src.file_manager.file_manager import FileManager
from src.logster.logster import Logster

MAX_RETRIES = 3
MAX_DELAY = 5


class EpubFileDownloader:
    def __init__(self, logster: Logster, base_url: str, ebook_name: str):
        self.logster: Logster = logster
        self.base_url: str = base_url
        self.ebook_name: str = ebook_name
        self.file_manager: str = FileManager(logster, ebook_name)
        self.retry_codes: list[int] = [
            HTTPStatus.TOO_MANY_REQUESTS,
            HTTPStatus.INTERNAL_SERVER_ERROR,
            HTTPStatus.BAD_GATEWAY,
            HTTPStatus.SERVICE_UNAVAILABLE,
            HTTPStatus.GATEWAY_TIMEOUT,
        ]

    def download_file(self, path) -> bool:
        url: str = f"{self.base_url}/{path}"
        for attempt in range(MAX_RETRIES):
            try:
                self.logster.log(
                    f"Fetching URL: {url} (Attempt {attempt + 1}/{MAX_RETRIES})"
                )
                response = requests.get(url)
                response.raise_for_status()
                if response.content is None:
                    return False
                self.file_manager.save_content_to_file(response.content, path)
                return True
            except HTTPError as e:
                self.logster.log(
                    f"Failed to fetch: {url}, Attempt {attempt + 1}/{MAX_RETRIES}, Error: {e}"
                )
                code = e.response.status_code
                if code in self.retry_codes:
                    sleep(MAX_DELAY)
                    continue
        self.logster.log(
            f"Giving up on fetching URL: {url} after {MAX_RETRIES} attempts."
        )
        return False

    def extract_content_opf_path_from_xml(self, container_xml_path: str) -> str:
        local_path: str = self.file_manager.get_local_file_path(container_xml_path)
        try:
            with open(local_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "xml")
                rootfile_element = soup.find("rootfile")

                if rootfile_element is None or not rootfile_element.get("full-path"):
                    raise RuntimeError(
                        "Failed to find the rootfile element in container.xml."
                    )

                content_opf_path: str = rootfile_element.get("full-path")

        except Exception as e:
            raise RuntimeError(f"Error reading container.xml: {e}")

        return content_opf_path

    def get_file_paths_from_content_opf(self, content_opf_path: str) -> list[str]:
        local_path: str = self.file_manager.get_local_file_path(content_opf_path)

        with open(local_path, "r") as file:
            soup = BeautifulSoup(file.read(), "xml")
        file_paths: list[str] = soup.find_all("item")

        subdirectory: str = os.path.dirname(content_opf_path)
        if subdirectory:
            file_paths = [f"{subdirectory}/{path['href']}" for path in file_paths]
        else:
            file_paths = [f"{path['href']}" for path in file_paths]

        self.logster.log(f"Found {len(file_paths)} file paths in content.opf")
        return file_paths

    def download_all_files(self, file_paths: list[str]) -> None:
        for path in tqdm(
            file_paths, desc="Fetching files", disable=self.logster.verbose
        ):
            self.download_file(path)

    def download_epub_files(self) -> None:
        self.logster.log("---- Creating mimetype file...")
        self.file_manager.save_content_to_file(b"application/epub+zip", "mimetype")

        self.logster.log("---- Downloading container.xml file...")
        container_xml_path = "META-INF/container.xml"
        self.download_file(container_xml_path)

        self.logster.log("---- Extracting content.opf path from container.xml...")
        content_opf_path = self.extract_content_opf_path_from_xml(container_xml_path)

        self.logster.log("---- Downloading content.opf file...")
        self.download_file(content_opf_path)

        self.logster.log("---- Getting file list from content.opf...")
        file_paths = self.get_file_paths_from_content_opf(content_opf_path)

        self.logster.log("---- Downloading files...")
        self.download_all_files(file_paths)

        self.logster.log("---- Creating EPUB archive...")
        self.file_manager.create_epub_archive()

        self.logster.log("---- Deleting temporary files...")
        self.file_manager.cleanup_epub_file_directory()
