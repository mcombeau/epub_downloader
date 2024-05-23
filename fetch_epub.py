import os
import sys
import requests
import zipfile
import argparse
import shutil
from requests.exceptions import RequestException
from time import sleep
from bs4 import BeautifulSoup, Tag
from tqdm import tqdm
from xml.etree import ElementTree as ET


def log(message, verbose):
    if verbose:
        print(message)


def fetch_and_save(url, path, retries=3, delay=5, verbose=False):
    for attempt in range(retries):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            log(f"Fetching URL: {url} (Attempt {attempt + 1}/{retries})", verbose)
            response = requests.get(url)
            response.raise_for_status()
            with open(path, "wb") as file:
                file.write(response.content)
            log(f"Successfully fetched and saved: {url} to {path}", verbose)
            return True
        except RequestException as e:
            log(
                f"Failed to fetch: {url}, Attempt {attempt + 1}/{retries}, Error: {e}",
                verbose,
            )
            sleep(delay)
    log(f"Giving up on fetching URL: {url} after {retries} attempts.", verbose)
    return False


def get_content_opf_path(base_url, output_dir, verbose=False):
    container_xml_url = f"{base_url}/META-INF/container.xml"
    container_xml_path = os.path.join(output_dir, "temp_container.xml")

    if not fetch_and_save(container_xml_url, container_xml_path, verbose=verbose):
        raise RuntimeError(f"Failed to fetch container.xml from {container_xml_url}")

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
            log(f"Found content.opf at: {content_opf_path}", verbose)
    except Exception as e:
        log(f"Error reading container.xml: {e}", verbose)
        raise
    finally:
        os.remove(container_xml_path)

    return content_opf_path


def create_mimetype_file(output_dir, verbose=False):
    mimetype_path = os.path.join(output_dir, "mimetype")
    log(f"Creating mimetype file at: {mimetype_path}", verbose)
    with open(mimetype_path, "w") as file:
        file.write("application/epub+zip")
    log(f"Created mimetype file at: {mimetype_path}", verbose)


def create_container_xml(output_dir, content_opf_relative_path, verbose=False):
    meta_inf_path = os.path.join(output_dir, "META-INF")
    os.makedirs(meta_inf_path, exist_ok=True)
    container_xml_path = os.path.join(meta_inf_path, "container.xml")
    with open(container_xml_path, "w") as file:
        file.write(
            f"""<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="{content_opf_relative_path}" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""
        )
    log(f"Created container.xml at: {container_xml_path}", verbose)


def parse_content_opf(content_opf_path, verbose=False):
    with open(content_opf_path, "r") as file:
        soup = BeautifulSoup(file.read(), "xml")
    items = soup.find_all("item")
    log(f"Found {len(items)} items in content.opf", verbose)
    return items


def fetch_all_files(base_url, output_dir, items, verbose=False):
    for item in tqdm(items, desc="Fetching files", disable=verbose):
        href = item["href"]
        item_path = os.path.join(output_dir, href)
        if not fetch_and_save(f"{base_url}/{href}", item_path, verbose=verbose):
            raise RuntimeError(f"Failed to fetch {href} from {base_url}")


def create_epub_archive(output_dir, epub_filename, verbose=False):
    epub_path = os.path.join(os.path.dirname(output_dir), epub_filename)
    log(f"Creating EPUB at: {epub_path}", verbose)
    with zipfile.ZipFile(epub_path, "w", allowZip64=True) as epub:
        epub.write(
            os.path.join(output_dir, "mimetype"),
            "mimetype",
            compress_type=zipfile.ZIP_STORED,
        )
        for foldername, _, filenames in os.walk(output_dir):
            for filename in filenames:
                if filename != "mimetype":
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, output_dir)
                    log(f"Adding {file_path} as {arcname} to EPUB", verbose)
                    epub.write(file_path, arcname)
    log(f"EPUB file created: {epub_path}", True)


def create_epub(base_url, output_dir, epub_filename, verbose=False):
    try:
        os.makedirs(output_dir, exist_ok=True)
        content_opf_path = get_content_opf_path(base_url, output_dir, verbose=verbose)
        content_opf_full_path = os.path.join(output_dir, content_opf_path)
        content_opf_dir = os.path.dirname(content_opf_full_path)
        os.makedirs(content_opf_dir, exist_ok=True)

        if not fetch_and_save(
            f"{base_url}/{content_opf_path}", content_opf_full_path, verbose=verbose
        ):
            raise RuntimeError(f"Failed to fetch content.opf from {base_url}")

        base_file_url = f"{base_url}/OEBPS" if "OEBPS" in content_opf_path else base_url

        toc_ncx_url = f"{base_file_url}/toc.ncx"
        toc_ncx_path = os.path.join(content_opf_dir, "toc.ncx")
        if not fetch_and_save(toc_ncx_url, toc_ncx_path, verbose=verbose):
            raise RuntimeError(f"Failed to fetch toc.ncx from {toc_ncx_url}")

        create_mimetype_file(output_dir, verbose=verbose)
        create_container_xml(output_dir, content_opf_path, verbose=verbose)

        items = parse_content_opf(content_opf_full_path, verbose=verbose)
        fetch_all_files(
            base_file_url,
            os.path.dirname(content_opf_full_path),
            items,
            verbose=verbose,
        )

        create_epub_archive(output_dir, epub_filename, verbose=verbose)
    except Exception as e:
        log(f"An error occurred: {e}", verbose)
        log(f"Cleaning up temporary directory: {output_dir}", verbose)
        shutil.rmtree(output_dir)
        raise e

    shutil.rmtree(output_dir)
    log(f"Cleaned up temporary directory: {output_dir}", verbose)


def get_content_opf_url(spread_url, verbose=False):
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
    log(f"Found content.opf URL: {content_opf_url}", verbose)
    return content_opf_url


def get_epub_base_url(book_url, verbose=False):
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
    log(f"Fetching Read Online URL: {read_online_url}", verbose)
    content_opf_url = get_content_opf_url(read_online_url, verbose=verbose)
    epub_base_url = content_opf_url.rsplit("/", 1)[0]
    return epub_base_url, content_opf_url


def main():
    parser = argparse.ArgumentParser(description="Fetch and create an EPUB file.")
    parser.add_argument("book_url", help="The URL of the book on epub.pub")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    args = parser.parse_args()
    book_url = args.book_url
    verbose = args.verbose

    if not book_url.startswith("https://www.epub.pub/"):
        print("Error: The provided URL is not from 'https://www.epub.pub/'.")
        sys.exit(1)

    try:
        epub_base_url, content_opf_url = get_epub_base_url(book_url, verbose=verbose)
        epub_filename = content_opf_url.split("/")[-2] + ".epub"
        output_base_dir = "downloaded_epubs"
        epub_dir = os.path.join(
            output_base_dir, epub_filename.rsplit(".", 1)[0] + "_temp"
        )
        create_epub(epub_base_url, epub_dir, epub_filename, verbose=verbose)
    except Exception as e:
        print(f"Failed to create EPUB: {e}")


if __name__ == "__main__":
    main()
