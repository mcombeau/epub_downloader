import argparse
import sys
import os


def adjust_sys_path():
    script_path = os.path.realpath(__file__)
    base_dir = os.path.dirname(os.path.dirname(script_path))
    sys.path.append(base_dir)


adjust_sys_path()

from src.epub_file_downloader.epub_file_downloader import EpubFileDownloader
from src.epub_locator.epub_locator import EpubLocator
from src.logster.logster import Logster


def get_args():
    parser = argparse.ArgumentParser(
        description="Download an ebook from https://www.epub.pub/ and create an EPUB file."
    )
    parser.add_argument("book_url", help="The URL of the book on https://www.epub.pub/")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    return parser.parse_args()


def main():
    args = get_args()

    try:
        logger = Logster(args.verbose)
        locator = EpubLocator(logger, args.book_url)
        base_url = locator.get_epub_base_url()
        ebook_name = locator.get_ebook_name()
        downloader = EpubFileDownloader(logger, base_url, ebook_name)
        downloader.download_epub_files()
    except Exception as e:
        logger.log(f"Failed to create EPUB: {e}", override_verbose=True)


if __name__ == "__main__":
    main()
