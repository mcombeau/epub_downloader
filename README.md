# EPUB Downloader

This script downloads an ebook from [epub.pub](https://www.epub.pub/) and creates an EPUB file.

## Description

The script fetches the content of an ebook from a given URL on [epub.pub](https://www.epub.pub/), parses the necessary files, and compiles them into a single EPUB file. It supports verbose output to help track the progress and identify issues during the download and creation process.

## Prerequisites

- Python 3.6 or higher
- Required Python packages:
  - `requests`
  - `beautifulsoup4`
  - `tqdm`

## Installation

1. Clone the repository or download the script file.

2. Install the required Python packages using pip:

```bash
pip install requests beautifulsoup4 tqdm
```

# Usage

To run the script, use the following command:

```bash
Copy code
python fetch_epub.py [book_url] [-v]
```

- `book_url`: The URL of the book on epub.pub
- `-v`, `--verbose`: Enable verbose output (optional)

## Example

```bash
python fetch_epub.py https://www.epub.pub/book/it-by-stephen-king -v
```

# Notes

- Ensure that the provided book URL is from the https://www.epub.pub/ domain.
- The script will create a temporary directory to store downloaded files, which will be cleaned up after the EPUB is created.
- **Support Authors: If you enjoy a book you downloaded using this script, please consider supporting the author by purchasing the book from a legitimate retailer.**
