import os
import requests
import zipfile
import argparse
import shutil
from requests.exceptions import RequestException
from time import sleep
from bs4 import BeautifulSoup
from tqdm import tqdm


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


def create_mimetype_file(output_dir, verbose=False):
    mimetype_path = os.path.join(output_dir, "mimetype")
    with open(mimetype_path, "w") as file:
        file.write("application/epub+zip")
    log(f"Created mimetype file at: {mimetype_path}", verbose)


def create_container_xml(output_dir, verbose=False):
    meta_inf_path = os.path.join(output_dir, "META-INF")
    os.makedirs(meta_inf_path, exist_ok=True)
    container_xml_path = os.path.join(meta_inf_path, "container.xml")
    with open(container_xml_path, "w") as file:
        file.write(
            """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""
        )
    log(f"Created container.xml at: {container_xml_path}", verbose)


def parse_content_opf(content_opf_path):
    with open(content_opf_path, "r") as file:
        content_opf = file.read()
    soup = BeautifulSoup(content_opf, "xml")
    items = soup.find_all("item")
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
        for foldername, _, filenames in os.walk(output_dir):
            for filename in filenames:
                if filename == "mimetype":
                    continue
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, output_dir)
                log(f"Adding {file_path} as {arcname} to EPUB", verbose)
                epub.write(file_path, arcname)
    log(f"EPUB file created: {epub_path}", True)


def create_epub(base_url, output_dir, epub_filename, verbose=False):
    try:
        os.makedirs(output_dir, exist_ok=True)
        log(f"Output directory created: {output_dir}", verbose)

        content_opf_path = os.path.join(output_dir, "content.opf")
        toc_ncx_path = os.path.join(output_dir, "toc.ncx")

        if not fetch_and_save(
            f"{base_url}/content.opf", content_opf_path, verbose=verbose
        ):
            raise RuntimeError(f"Failed to fetch content.opf from {base_url}")
        if not fetch_and_save(f"{base_url}/toc.ncx", toc_ncx_path, verbose=verbose):
            raise RuntimeError(f"Failed to fetch toc.ncx from {base_url}")

        create_mimetype_file(output_dir, verbose=verbose)
        create_container_xml(output_dir, verbose=verbose)

        items = parse_content_opf(content_opf_path)
        fetch_all_files(base_url, output_dir, items, verbose=verbose)

        create_epub_archive(output_dir, epub_filename, verbose=verbose)

    except Exception as e:
        log(f"An error occurred: {e}", verbose)
        log(f"Cleaning up temporary directory: {output_dir}", verbose)
        shutil.rmtree(output_dir)
        raise e

    shutil.rmtree(output_dir)
    log(f"Cleaned up temporary directory: {output_dir}", verbose)


def main():
    parser = argparse.ArgumentParser(description="Fetch and create an EPUB file.")
    parser.add_argument("epub_filename", help="The name of the EPUB file to create")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()
    epub_filename = args.epub_filename
    verbose = args.verbose

    base_url = "https://asset.epub.pub/epub"
    output_base_dir = "downloaded_epubs"
    epub_dir = os.path.join(
        output_base_dir, os.path.splitext(epub_filename)[0] + "_temp"
    )

    try:
        create_epub(
            base_url + "/" + epub_filename, epub_dir, epub_filename, verbose=verbose
        )
    except Exception as e:
        print(f"Failed to create EPUB: {e}")


if __name__ == "__main__":
    main()
