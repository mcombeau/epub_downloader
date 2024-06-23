# EPUB Downloader

This script downloads an ebook from [epub.pub](https://www.epub.pub/) and creates an EPUB file.

## Description

The script fetches the content of an ebook from a given URL on [epub.pub](https://www.epub.pub/), parses the necessary files, and compiles them into a single EPUB file. It supports verbose output to help track the progress and identify issues during the download and creation process.

## Prerequisites

- Python 3.6 or higher
- Dependencies:
    - `bs4`
    - `lxml`
    - `tqdm`
    - `urllib3`

## Installation

1. Clone the repository or download the script file.

2. Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

## Usage

To run the script, use the following command:

```bash
Copy code
python epub_downloader [book_url] [-v]
```

- `book_url`: The URL of the book on epub.pub
- `-v`, `--verbose`: Enable verbose output (optional)

### Example

The script handles downloading directly from the book page:
```bash
python epub_downloader https://www.epub.pub/book/it-by-stephen-king -v
```

Or you can download from the spread page (after clicking on the Read Online button):
```bash
python epub_downloader https://spread.epub.pub/epub/5a5827247412f4000781f18e -v
```

Or if you're into digging for the URL manually, you can download directly from an asset page:
```bash
python epub_downloader https://asset.epub.pub/epub/it-by-stephen-king-1.epub -v
```

Note that `epub_downloader` is only a symbolic link to `src/main.py`.


## Notes

- Ensure that the provided book URL is from the https://www.epub.pub/ domain. Theoretically if you get the URL to another ebook reader source file such as `content.opf` or `container.xml`, this script will also work, but there are no guarantees.
- The script will create a temporary directory to store downloaded files, which will be cleaned up after the EPUB is created.
- **Support Authors: If you enjoy an ebook you downloaded using this script, please consider supporting the author by purchasing the book from a legitimate retailer.**
