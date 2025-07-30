# docx2adoc

A powerful DOCX to AsciiDoc converter with advanced features, smart processing, and excellent automation support.

## Features

- Smart DOCX to AsciiDoc conversion
- Automatic section number removal (optional)
- Image extraction and management
- Table formatting with [INFO] tags for empty first columns
- Heading hierarchy normalization
- Recursive directory processing
- Color-coded output (can be disabled)
- Detailed logging support
- Dry-run mode for testing
- Quiet mode for automation

## Installation

```bash
pip install docx2adoc
```

### Prerequisites

- Python 3.7 or higher
- Pandoc must be installed on your system ([Install Pandoc](https://pandoc.org/installing.html))

## Usage

Basic conversion:
```bash
docx2adoc document.docx
```

Convert multiple files:
```bash
docx2adoc doc1.docx doc2.docx
```

Convert with logging:
```bash
docx2adoc document.docx --log-file conversion.log
```

Test run without making changes:
```bash
docx2adoc ./documents/ --dry-run
```

Quiet mode for automation:
```bash
docx2adoc document.docx --quiet
```

Convert recursively with image extraction:
```bash
docx2adoc ./documents/ -r -i ./images/ -g
```

## Command Line Options

### Main Options
- `input`: Input DOCX file(s) or directory to convert
- `-g, --generalize-headings`: Run heading generalization
- `-k, --keep-numbers`: Keep section numbers from original document

### Input/Output Options
- `-o, --output-dir DIR`: Output directory for converted files
- `-i, --image-dir DIR`: Directory to extract images to

### Processing Options
- `-r, --recursive`: Recursively process DOCX files in directories

### Display Options
- `--no-color`: Disable color output
- `-v, --verbose`: Enable verbose output
- `--quiet`: Suppress all output except errors
- `--dry-run`: Show what would be done without making changes

### Logging Options
- `--log-file FILE`: Write detailed logs to specified file

## Exit Codes
- 0 (SUCCESS): Successful completion
- 1 (FAILURE): One or more files failed to process
- 2 (CRITICAL): Critical error (e.g., missing dependencies)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 