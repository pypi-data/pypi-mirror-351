# Markdown Image Downloader

A Python package that automatically downloads and manages images referenced in markdown files, storing them locally in an `_attachments` folder. This script is particularly useful for maintaining local copies of images in markdown documentation and ensuring consistent image availability.

Or just for Obsidian's Readwise export, which I made this for.

Previously hosted on [GitHub Gist](https://gist.github.com/mufidu/f7b795f844f1ee4dc78e55123d5a398b). Moved here to allow for easier maintenance and contributions, if any. Also published to [PyPI](https://pypi.org/project/markdown-image-downloader) for convenience.

## Requirements

```
Python 3.9+
```

## Installation

Install directly from PyPI using pip:

```bash
pip install markdown-image-downloader
```

## Usage

Run the package from the command line, providing the folder containing your markdown files as an argument:

```bash
markdown-image-downloader <folder_name>
```

### Example

```bash
markdown-image-downloader ../Readwise/Articles
```

This will:

1. Scan all markdown files in the `../Readwise/Articles` folder
2. Download any images referenced in the markdown files
3. Store them in `../Readwise/Articles/_attachments`
4. Update the markdown files to reference the local copies

## Features

- Uses custom HTTP headers to avoid download blocks
- Downloads images from URLs referenced in markdown files
- Creates local copies of images in an `_attachments` directory
- Automatically updates links in the markdown files with new local image paths
- Compresses large images to reduce storage space
- Supports multithreaded concurrent downloads
- Uses rate limit to prevent server overload and download blocks
- Progress bar for tracking download status
- Maintains detailed logging of error operations
- Sanitizes filenames for cross-platform compatibility
- Supports for rerunning the script without re-downloading images

## How It Works

1. **Scanning**: The script scans all `.md` files in the specified folder for image references.
2. **Downloading**: For each image URL found:
   - Downloads the image if it's not already in `_attachments`
   - Compresses images larger than 500KB while maintaining quality
   - Generates unique filenames based on content hash
3. **Organization**: Creates an `_attachments` folder to store all images
4. **Updating**: Updates markdown files to reference the local copies in `_attachments`

## Features in Detail

### Image Compression

- Automatically compresses large images
- Maintains reasonable quality through progressive compression
- Converts RGBA images to RGB with white background

### Filename Handling

- Preserves original filenames
- Sanitizes filenames for cross-platform compatibility

### Concurrent Processing

- Uses ThreadPoolExecutor for parallel downloads
- Includes progress bar for tracking downloads
- Implements rate limiting to prevent server overload

### Error Handling

- Comprehensive logging of all operations
- Graceful handling of download failures
- Skips already processed images

## Logging

The script creates detailed logs in a `logs` directory:

- Location: `./logs/image_downloader.log`
- Includes timestamps, operation details, and error messages
- New log file created for each run

## Limitations

- Only processes image links in markdown format: `![alt](url)`
- Requires internet connection for downloading external images
- May be rate-limited or just straight denied by some servers
- SVG files are downloaded but not compressed

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is available under the MIT License.
