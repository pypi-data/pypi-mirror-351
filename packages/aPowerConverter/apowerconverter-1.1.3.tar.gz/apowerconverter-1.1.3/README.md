# aPowerConverter

A powerful bidirectional converter between DOCX and AsciiDoc formats with advanced features.

## Features

- Bidirectional conversion:
  - DOCX → AsciiDoc
  - AsciiDoc → DOCX (new!)
- Smart document processing:
  - Automatic document ID insertion (`[[filename]]`)
  - Table formatting with [INFO] tags
  - Heading hierarchy normalization (DOCX → AsciiDoc)
  - Section number removal (optional, DOCX → AsciiDoc)
- Image handling:
  - Automatic image extraction and organization
  - Relative path handling for portability
  - Optional image directory specification
- Batch processing:
  - Multiple file conversion
  - Directory scanning
  - Recursive subdirectory support
- User-friendly interface:
  - Progress tracking
  - Color-coded output
  - Detailed logging
  - Dry-run mode

## Requirements

### Core Dependencies
- Python 3.7 or higher
- Pandoc (for all conversions)
- Asciidoctor (for AsciiDoc → DOCX conversion)

### Installation Steps

1. Install Python dependencies:
```bash
pip install aPowerConverter
```

2. Install Pandoc:
- Windows: Download from [pandoc.org/installing.html](https://pandoc.org/installing.html)
- Linux: `sudo apt-get install pandoc` or equivalent
- macOS: `brew install pandoc`

3. Install Asciidoctor (required for AsciiDoc → DOCX conversion):
- Install Ruby first if not present
- Then run: `gem install asciidoctor`

## Usage

### Basic Conversion

Convert DOCX to AsciiDoc:
```bash
apowerconverter document.docx
```

Convert AsciiDoc to DOCX:
```bash
apowerconverter document.adoc
```

### Advanced Options

With image extraction:
```bash
apowerconverter document.docx -i ./images/
```

Keep section numbers (DOCX → AsciiDoc):
```bash
apowerconverter document.docx -k
```

Generalize headings (DOCX → AsciiDoc):
```bash
apowerconverter document.docx -g
```

Convert multiple files:
```bash
apowerconverter doc1.docx doc2.adoc doc3.docx
```

Process directory recursively:
```bash
apowerconverter ./documents/ -r
```

Specify output directory:
```bash
apowerconverter document.docx -o ./output/
```

### Additional Options

- `--dry-run`: Show what would be done without making changes
- `--quiet`: Suppress all output except errors
- `--no-color`: Disable color output
- `--log-file FILE`: Write detailed logs to specified file
- `--verbose`: Enable verbose output

## Exit Codes

- 0: Success - All files processed successfully
- 1: Failure - One or more files failed to process
- 2: Critical - Missing dependencies or invalid arguments

## Examples

Convert a single DOCX file:
```bash
apowerconverter mydoc.docx
```

Convert an AsciiDoc file with images:
```bash
apowerconverter mydoc.adoc -i ./images/
```

Convert all documents in a directory:
```bash
apowerconverter ./docs/ -r -i ./images/ -o ./converted/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 