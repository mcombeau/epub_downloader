import argparse

verbose = False


def log(message, override_verbose=False):
    if verbose or override_verbose:
        print(message)


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
    global verbose

    args = get_args()

    verbose = args.verbose

    try:
        # download_epub_files(args.book_url)
        # create_epub()
    except Exception as e:
        log(f"Failed to create EPUB: {e}", override_verbose=True)


if __name__ == "__main__":
    main()
