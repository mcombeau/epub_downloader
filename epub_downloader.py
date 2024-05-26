"""
epub_downloader.py

This script downloads an ebook from https://www.epub.pub/ and creates an EPUB file.
It extracts the necessary content from the specified book URL and compiles it into a single EPUB file.

Usage:
    python epub_downloader.py <book_url> [-v]

Arguments:
    book_url  The URL of the book on https://www.epub.pub/
    -v, --verbose  Enable verbose output

Dependencies:
    - argparse
    - os
    - requests
    - shutil
    - zipfile
    - BeautifulSoup (from bs4)
    - tqdm
    - xml.etree.ElementTree

Note:
    If you enjoy an ebook you read using this script, please consider supporting the author by purchasing the book from a reputable retailer.

Repository:
    https://github.com/mcombeau/epub_downloader
"""

import argparse
import os
import requests
import shutil
import zipfile
from bs4 import BeautifulSoup, Tag
from requests.exceptions import RequestException
from time import sleep
from tqdm import tqdm
from xml.etree import ElementTree as ET


# Class Definitions
class EpubContext:
    def __init__(self, base_url, output_dir, epub_filename):
        self.base_url = base_url
        self.output_dir = output_dir
        self.epub_filename = epub_filename
        self.content_opf_path = ""
        self.base_file_url = ""
        self.base_file_local = ""

    def __repr__(self):
        return (
            f"EpubContext(\n"
            f"  base_url={self.base_url},\n"
            f"  output_dir={self.output_dir},\n"
            f"  epub_filename={self.epub_filename}\n"
            f"  content_opf_path={self.content_opf_path}\n"
            f"  base_file_url={self.base_file_url}\n"
            f"  base_file_local={self.base_file_local}\n"
            f")"
        )


# Global Variables
verbose = False


# Utility Functions
def log(message, override_verbose=False):
    if verbose or override_verbose:
        print(message)


def fetch_and_save(url, path, retries=3, delay=5):
    for attempt in range(retries):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            log(f"Fetching URL: {url} (Attempt {attempt + 1}/{retries})")
            response = requests.get(url)
            response.raise_for_status()
            with open(path, "wb") as file:
                file.write(response.content)
            log(f"Successfully fetched and saved: {url} to {path}")
            return True
        except RequestException as e:
            log(f"Failed to fetch: {url}, Attempt {attempt + 1}/{retries}, Error: {e}")
            sleep(delay)
    log(f"Giving up on fetching URL: {url} after {retries} attempts.")
    return False


def get_args():
    parser = argparse.ArgumentParser(
        description="Download an ebook from https://www.epub.pub/ and create an EPUB file."
    )
    parser.add_argument("book_url", help="The URL of the book on https://www.epub.pub/")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    return parser.parse_args()


# EPUB Download and Creation Functions
def get_container_xml(context):
    container_xml_url = os.path.join(context.base_url, "META-INF/container.xml")
    container_xml_path = os.path.join(context.output_dir, "META-INF/container.xml")

    if not fetch_and_save(container_xml_url, container_xml_path):
        raise RuntimeError(f"Failed to fetch container.xml from {container_xml_url}")


def get_content_opf_path(context):
    container_xml_path = os.path.join(context.output_dir, "META-INF/container.xml")

    try:
        with open(container_xml_path, "r") as file:
            tree = ET.ElementTree(ET.fromstring(file.read()))
            root = tree.getroot()
            namespace = {"n": "urn:oasis:names:tc:opendocument:xmlns:container"}
            rootfile_element = root.find("n:rootfiles/n:rootfile", namespace)
            if rootfile_element is None or not rootfile_element.get("full-path"):
                raise RuntimeError(
                    "Failed to find the rootfile element in container.xml."
                )
            content_opf_path = str(rootfile_element.get("full-path"))
            log(f"Found content.opf at: {content_opf_path}")
    except Exception as e:
        log(f"Error reading container.xml: {e}")
        raise

    return content_opf_path


def create_mimetype_file(output_dir):
    mimetype_path = os.path.join(output_dir, "mimetype")
    log(f"Creating mimetype file at: {mimetype_path}")
    with open(mimetype_path, "w") as file:
        file.write("application/epub+zip")
    log(f"Created mimetype file at: {mimetype_path}")


def parse_content_opf(content_opf_path):
    with open(content_opf_path, "r") as file:
        soup = BeautifulSoup(file.read(), "xml")
    items = soup.find_all("item")
    log(f"Found {len(items)} items in content.opf")
    return items


def fetch_all_files(context, output_dir, items):
    for item in tqdm(items, desc="Fetching files", disable=verbose):
        href = item["href"]
        item_path = os.path.join(output_dir, href)
        full_url = os.path.join(context.base_file_url, href)
        if not fetch_and_save(full_url, item_path):
            raise RuntimeError(f"Failed to fetch {href} from {context.base_file_url}")


def create_epub_archive(output_dir, epub_filename):
    epub_path = os.path.join(os.path.dirname(output_dir), epub_filename)
    log(f"Creating EPUB at: {epub_path}")
    with zipfile.ZipFile(epub_path, "w", allowZip64=True) as epub:
        epub.write(
            os.path.join(output_dir, "mimetype"),
            "mimetype",
            compress_type=zipfile.ZIP_STORED,
        )
        for foldername, _, filenames in os.walk(output_dir):
            for filename in filenames:
                if filename == "mimetype":
                    continue
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, output_dir)
                log(f"Adding {file_path} as {arcname} to EPUB")
                epub.write(file_path, arcname)
    log(f"EPUB file created: {epub_path}", override_verbose=True)


def create_directory_structure(context):
    os.makedirs(context.output_dir, exist_ok=True)
    file_dir = os.path.dirname(get_content_opf_path(context))
    context.base_file_url = os.path.join(context.base_url, file_dir)
    context.base_file_local = os.path.join(context.output_dir, file_dir)
    os.makedirs(context.base_file_local, exist_ok=True)


def setup_epub_files(context):
    if not fetch_and_save(
        os.path.join(context.base_file_url, "content.opf"),
        os.path.join(context.base_file_local, "content.opf"),
    ):
        raise RuntimeError(f"Failed to fetch content.opf from {context.base_url}")

    toc_ncx_url = os.path.join(context.base_file_url, "toc.ncx")
    toc_ncx_path = os.path.join(context.base_file_local, "toc.ncx")
    if not fetch_and_save(toc_ncx_url, toc_ncx_path):
        raise RuntimeError(f"Failed to fetch toc.ncx from {toc_ncx_url}")

    create_mimetype_file(context.output_dir)


def download_epub_content(context):
    items = parse_content_opf(os.path.join(context.base_file_local, "content.opf"))
    fetch_all_files(
        context,
        context.base_file_local,
        items,
    )


def create_epub(context):
    try:
        get_container_xml(context)
        create_directory_structure(context)
        setup_epub_files(context)
        download_epub_content(context)
        create_epub_archive(context.output_dir, context.epub_filename)
    except Exception as e:
        log(f"An error occurred: {e}")
        log(f"Cleaning up temporary directory: {context.output_dir}")
        shutil.rmtree(context.output_dir)
        raise e

    shutil.rmtree(context.output_dir)
    log(f"Cleaned up temporary directory: {context.output_dir}")


# URL Parsing Functions
def get_content_opf_url(spread_url):
    response = requests.get(spread_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    content_opf_input = soup.find("input", id="assetUrl")
    if (
        not content_opf_input
        or not isinstance(content_opf_input, Tag)
        or not content_opf_input.get("value")
    ):
        raise RuntimeError("Failed to find the content.opf URL in the spread page.")
    content_opf_url = str(content_opf_input["value"])
    log(f"Found content.opf URL: {content_opf_url}")
    return content_opf_url


def get_epub_base_url(book_url):
    response = requests.get(book_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    read_online_link = soup.find("a", class_="btn-read")
    if not read_online_link or not isinstance(read_online_link, Tag):
        raise RuntimeError("Failed to find the 'Read Online' link.")
    read_online_url = (
        str(read_online_link.get("data-domain", ""))
        + "/epub/"
        + str(read_online_link.get("data-readid", ""))
    )
    log(f"Fetching Read Online URL: {read_online_url}")
    content_opf_url = get_content_opf_url(read_online_url)

    parts = content_opf_url.split("/")
    epub_base_url_parts = []
    for part in parts:
        epub_base_url_parts.append(part)
        if part.endswith(".epub"):
            break
    epub_base_url = "/".join(epub_base_url_parts)

    log(f"Determined EPUB base URL: {epub_base_url}")
    return epub_base_url


def create_epub_context(book_url):
    if book_url.startswith("https://www.epub.pub/"):
        epub_base_url = get_epub_base_url(book_url)
    else:
        epub_base_url = book_url

    epub_filename = book_url.split("/")[-1] + ".epub"
    output_base_dir = "downloaded_epubs"
    epub_dir = os.path.join(output_base_dir, epub_filename.rsplit(".", 1)[0] + "_temp")
    return EpubContext(epub_base_url, epub_dir, epub_filename)


# Main Function
def main():
    global verbose

    args = get_args()
    book_url = args.book_url
    verbose = args.verbose

    try:
        context = create_epub_context(book_url)
        create_epub(context)
    except Exception as e:
        log(f"Failed to create EPUB: {e}", override_verbose=True)


if __name__ == "__main__":
    main()
