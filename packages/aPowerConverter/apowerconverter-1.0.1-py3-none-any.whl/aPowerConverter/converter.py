import sys
import re
import argparse
import os
import shutil
import subprocess
import glob
import unicodedata
from time import sleep, time
import random
import logging
from datetime import datetime

# Version information
__version__ = '1.0.0'

# Exit codes
EXIT_SUCCESS = 0      # Successful completion
EXIT_FAILURE = 1      # One or more files failed to process
EXIT_CRITICAL = 2     # Critical error (e.g., missing dependencies, invalid args)

# Constants for user interface
# ANSI color codes that work on modern terminals
ANSI_COLORS = {
    'GREEN': '\033[92m',
    'RED': '\033[91m',
    'BLUE': '\033[94m',
    'YELLOW': '\033[93m',
    'RESET': '\033[0m',
    'BOLD': '\033[1m'
}

class ColorManager:
    """Manages color output based on terminal capabilities and user preferences."""
    
    def __init__(self):
        self.force_no_color = False
    
    def set_color_mode(self, no_color):
        """Set whether to force no color output."""
        self.force_no_color = no_color
    
    def should_use_color(self):
        """Determine if color should be used based on environment and settings."""
        if self.force_no_color:
            return False
        if 'NO_COLOR' in os.environ:  # Respect NO_COLOR environment variable
            return False
        return sys.stdout.isatty()
    
    def color_text(self, text, color_name):
        """
        Safely wrap text in color codes if colors are enabled.
        Falls back to plain text if colors are disabled or not supported.
        """
        if not self.should_use_color():
            return text
        color = ANSI_COLORS.get(color_name, '')
        return f"{color}{text}{ANSI_COLORS['RESET']}"

# Global color manager instance
color_manager = ColorManager()

# Get a random banner that won't be reused
def get_unique_banner(banner_list):
    """Get and remove a random banner from the list."""
    if not banner_list:  # If list is empty, return a default message
        return "🚀 Processing..."
    return banner_list.pop(random.randrange(len(banner_list)))

CONVERSION_BANNERS = [
    "🚀 Initiating DOCX-to-AsciiDoc conversion sequence...",
    "🌀 Spinning up the DOCX warp drive...",
    "📚 Transforming docx into pure, book-ready AsciiDoc magic...",
    "🤖 Parsing your documents... Resistance is futile.",
    "⚡ DOCX → .adoc: Hold on to your hats! It's about to get lively",
]

GENERALIZE_BANNERS = [
    "\n🎩 Time to tidy up those hats—normalizing all your AsciiDoc headings...",
    "\n🧹 Sweeping up rogue heading levels—let's get everything starting from ==",
    "\n🔧 Adjusting heading hierarchy: OCD mode [ON].",
    "\n🕶️ Headings are about to get a fresh new look.",
    "\n🪄 Wave of the wand—flattening all those wild headings to civilized ==.",
    "\n📏 Bringing order to chaos—standardizing heading levels...",
    "\n🎯 Target acquired: Converting all headings to start from level 2",
    "\n🎨 Time for some heading artistry—making your docs look pro!",
]

CELEBRATION_MESSAGES = [
    "\n🎉 Mission accomplished! Your documents are now AsciiDoc masterpieces with perfectly aligned headings!",
    "\n🌟 Double victory! Both conversion and heading normalization completed successfully!",
    "\n🏆 Achievement unlocked: Master of Document Transformation!",
    "\n🎨 Your documents are now works of art—both in content and structure!",
    "\n🚀 From DOCX chaos to AsciiDoc excellence—mission complete!",
]

def setup_logging(log_file=None, verbose=False):
    """
    Set up logging configuration.
    
    Args:
        log_file (str, optional): Path to log file. If None, only console logging is set up.
        verbose (bool): If True, set logging level to DEBUG
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create formatters
    console_formatter = logging.Formatter('%(message)s')  # Simple format for console
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers
    root_logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # File handler (if requested)
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        root_logger.addHandler(file_handler)
        logging.info(f"Logging to file: {log_file}")

def check_dependencies():
    """
    Check if all required dependencies are available.
    Exits with status code 2 if critical dependencies are missing.
    """
    logging.debug("Checking dependencies...")
    # Check for pandoc
    if shutil.which('pandoc') is None:
        logging.error("❌ Error: Pandoc is not installed or not in PATH")
        logging.error("Please install Pandoc from https://pandoc.org/installing.html")
        sys.exit(2)
    logging.debug("✓ Pandoc found")

def abspath_or_none(path):
    """
    Convert path to absolute path if it exists, otherwise return None.
    
    Args:
        path (str): Path to convert
    
    Returns:
        str or None: Absolute path if path exists, None otherwise
    """
    return os.path.abspath(path) if path else None

def remove_section_numbers(content):
    """
    Remove various section numbering styles from AsciiDoc headings.
    Examples of numbering styles handled:
    - Decimal: 1., 1.2., 1.2.3.
    - Roman numerals: IV., III)
    - Letters: A., B), a., b)
    - Mixed: 1a., 2b., 1.a)
    """
    pattern = (
        r'^(=+)\s+'
        r'((?:\d+[\.\)])+|(?:[IVXLCivxlc]+[\.\)])+|(?:[A-Za-z][\.\)])+|(?:\d+[A-Za-z][\.\)])+)\s+'
    )
    return '\n'.join(
        re.sub(pattern, r'\1 ', line)
        for line in content.splitlines()
    )

def format_tables(content):
    """
    Format tables in AsciiDoc content.
    If the first column in the first data row is empty, mark the table as [INFO].
    
    Args:
        content (str): AsciiDoc content to process
    
    Returns:
        str: Processed content with formatted tables
    """
    lines = content.splitlines()
    result = []
    in_table = False
    table_lines = []
    has_empty_first_column = False
    
    for line in lines:
        if line.startswith('|==='):
            if not in_table:  # Start of table
                in_table = True
                table_lines = [line]
                has_empty_first_column = False
            else:  # End of table
                table_lines.append(line)
                if has_empty_first_column:
                    result.append('[INFO]')
                result.extend(table_lines)
                in_table = False
                table_lines = []
        elif in_table:
            table_lines.append(line)
            # Check only the first data row (right after header)
            if line.startswith('|') and len(table_lines) == 3:  # First data row after header
                # Split the line by | and check the first column
                cells = [cell.strip() for cell in line.split('|')]
                # Check if the first actual cell (index 1) is empty
                # cells[0] is empty because the line starts with |
                if len(cells) > 1 and not cells[1]:
                    has_empty_first_column = True
        else:
            result.append(line)
    
    return '\n'.join(result)

def normalize_punctuation(text):
    """
    Normalize only punctuation characters while preserving letters with diacritics.
    Converts all types of smart quotes, dashes, etc. to their simple forms but keeps non-ASCII letters.
    
    Args:
        text (str): Text to normalize
    
    Returns:
        str: Text with normalized punctuation but preserved letters
    """
    # Map of Unicode quotes, dashes and other punctuation to ASCII equivalents
    char_map = {
        '\u2018': "'", '\u2019': "'", '\u201a': "'", '\u201b': "'",  # single quotes
        '\u201c': '"', '\u201d': '"', '\u201e': '"', '\u201f': '"',  # double quotes
        '\u2032': "'", '\u2033': '"', '\u2034': '"""', '\u2035': "'", '\u2036': '"', '\u2037': '"""',  # primes
        '\u2013': '-', '\u2014': '-', '\u2010': '-', '\u2011': '-', '\u2212': '-',  # dashes and hyphens
        '\u2026': '...',  # ellipsis
    }
    
    # First pass: replace known special characters
    for old, new in char_map.items():
        text = text.replace(old, new)
    
    # Second pass: handle any remaining punctuation
    normalized = []
    for char in text:
        category = unicodedata.category(char)
        if category.startswith('P'):  # If it's a punctuation character
            # Normalize only punctuation
            norm_char = unicodedata.normalize('NFKD', char)
            if norm_char.isascii():
                normalized.append(norm_char)
            else:
                normalized.append(char)
        else:
            # Keep all other characters (including letters with diacritics) as is
            normalized.append(char)
    
    return ''.join(normalized)

def generalize_headings(content):
    """
    Generalize AsciiDoc headings by:
    1. Ensuring all headings start at level 2 (==)
    2. Maintaining proper heading hierarchy
    3. Removing any remaining section numbers
    4. Normalizing punctuation while preserving non-ASCII letters
    
    Args:
        content (str): The content of the AsciiDoc file
    
    Returns:
        str: The processed content with generalized headings
    """
    # Split content into lines for processing
    lines = content.splitlines()
    processed_lines = []
    
    # Regular expressions for heading detection and cleaning
    heading_pattern = r'^(=+)\s+(.+)$'
    number_pattern = r'''(?x)                    # Enable verbose mode for readability
        ^                                        # Start of string
        (?:                                      # Non-capturing group for alternatives
            \d+(?:\.\d+)*\s*[\.\)]\s*           # Decimal numbers: 1., 1.2., 1.2.3., 1), etc.
            |                                    # OR
            [IVXLCivxlc]+\s*[\.\)]\s*           # Roman numerals: IV., xi), etc.
            |                                    # OR
            [A-Za-z]\s*[\.\)]\s*                # Single letters: A., b), etc.
        )
    '''  # Matches section numbers like 1.2.3., IV., A), etc.
    
    # Track the first heading we find to determine level adjustment
    first_heading_level = None
    level_adjustment = 0
    
    # First pass: find the first heading level
    for line in lines:
        heading_match = re.match(heading_pattern, line)
        if heading_match and first_heading_level is None:
            first_heading_level = len(heading_match.group(1))
            # Calculate adjustment needed to make first heading level 2 (==)
            level_adjustment = 2 - first_heading_level
            break
    
    # If no headings found, just return the original content
    if first_heading_level is None:
        return content
    
    # Second pass: process all lines with adjusted heading levels
    for line in lines:
        heading_match = re.match(heading_pattern, line)
        if heading_match:
            level_markers, heading_text = heading_match.groups()
            current_level = len(level_markers)
            
            # Adjust the heading level
            new_level = current_level + level_adjustment
            new_level = max(2, new_level)  # Ensure minimum level is 2
            
            # Remove any remaining section numbers
            heading_text = re.sub(number_pattern, '', heading_text.strip())
            
            # Normalize punctuation while preserving non-ASCII letters
            heading_text = normalize_punctuation(heading_text.strip())
            
            # Reconstruct the heading with adjusted level
            processed_lines.append(f"{'=' * new_level} {heading_text}")
        else:
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)

def process_adoc_file(input_file, output_file=None):
    """
    Process a single AsciiDoc file to generalize its headings.
    
    Args:
        input_file (str): Path to the input AsciiDoc file
        output_file (str, optional): Path to the output file. If not provided,
                                   will modify the input file in place
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the input file
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Process the content
        processed_content = generalize_headings(content)
        
        # Determine output location
        output_path = output_file if output_file else input_file
        
        # Write the processed content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        
        return True
    
    except Exception as e:
        print(f"Error processing file {input_file}: {str(e)}")
        return False

def convert_docx_to_adoc(input_file, output_file=None, keep_numbers=False, image_dir=None, dry_run=False):
    """
    Convert a DOCX file to AsciiDoc format.
    
    Uses pandoc directly through subprocess for better control over the conversion process.
    
    Args:
        input_file (str): Path to the input DOCX file
        output_file (str, optional): Path to the output AsciiDoc file. 
                                   If not provided, will use input filename with .adoc extension
        keep_numbers (bool): If True, preserve section numbers from the original document
        image_dir (str, optional): Base directory for images. If provided, images will be
                                 extracted to a subdirectory named after the input file
        dry_run (bool): If True, show what would be done without making any changes
    """
    if dry_run:
        logging.info(f"[DRY RUN] Would convert: {input_file}")
        if output_file:
            logging.info(f"[DRY RUN] Would write to: {output_file}")
        if image_dir:
            logging.info(f"[DRY RUN] Would extract images to: {image_dir}")
        return True
    
    if not output_file:
        output_file = input_file.rsplit('.', 1)[0] + '.adoc'
    
    try:
        # Handle image directory
        current_image_dir = None
        if image_dir:
            # Create a subdirectory based on the input file name
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            current_image_dir = os.path.join(image_dir, base_name)
            
            # Ensure clean image directory
            if os.path.exists(current_image_dir):
                shutil.rmtree(current_image_dir)
            os.makedirs(current_image_dir)

        # Prepare pandoc command
        pandoc_cmd = [
            'pandoc',
            '--wrap=none',  # Prevent line wrapping
            '-f', 'docx',
            '-t', 'asciidoc',
            '-o', output_file,
            input_file
        ]
        
        # Add image extraction if image directory is specified
        if current_image_dir:
            pandoc_cmd.insert(1, f'--extract-media={current_image_dir}')
        
        # Run pandoc command
        result = subprocess.run(pandoc_cmd, capture_output=True, text=True)
        
        # Check for errors
        if result.returncode != 0:
            raise Exception(f"Pandoc conversion failed: {result.stderr}")
        
        # Read the converted file
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Format tables
        content = format_tables(content)
        
        if not keep_numbers:
            # Remove section numbers
            content = remove_section_numbers(content)
        
        # Write back the modified content
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Successfully converted {input_file} to {output_file}")
        if not keep_numbers:
            print("Section numbers were removed")
        if current_image_dir and os.path.exists(current_image_dir) and os.listdir(current_image_dir):
            print(f"Images extracted to {current_image_dir}")
        return True
    except Exception as e:
        print(f"Error converting file {input_file}: {str(e)}")
        # Clean up image directory if it was created and is empty
        if current_image_dir and os.path.exists(current_image_dir) and not os.listdir(current_image_dir):
            try:
                os.rmdir(current_image_dir)
            except OSError:
                pass  # Ignore errors when cleaning up
        return False

def process_files(input_files, output_dir=None, keep_numbers=False, image_dir=None, dry_run=False, quiet=False):
    """Process multiple input files."""
    # Create base image directory if specified and not in dry-run mode
    if image_dir and not os.path.exists(image_dir) and not dry_run:
        os.makedirs(image_dir)
        logging.debug(f"Created image directory: {image_dir}")
    
    # Display unique banner (unless in quiet mode)
    if not quiet:
        banner = get_unique_banner(CONVERSION_BANNERS)
        print('\n' + color_manager.color_text(banner, 'BLUE'))
    logging.info(f"Starting conversion process with {len(input_files)} files")
    
    successful = 0
    failed = 0
    converted_files = []
    
    for idx, input_file in enumerate(input_files, 1):
        if not os.path.exists(input_file):
            logging.error(f"Input file not found: {input_file}")
            failed += 1
            continue
        
        logging.info(f"Processing file {idx}/{len(input_files)}: {input_file}")
        if not quiet:
            print(f"  [{idx}/{len(input_files)}] 📄 Processing: {os.path.basename(input_file)} ... ", end='', flush=True)
            sleep(0.2)
        
        if output_dir:
            output_file = os.path.join(output_dir, 
                                     os.path.splitext(os.path.basename(input_file))[0] + '.adoc')
        else:
            output_file = None
        
        try:
            if convert_docx_to_adoc(input_file, output_file, keep_numbers, image_dir, dry_run):
                successful += 1
                if not quiet:
                    print(color_manager.color_text("✅ Success!", 'GREEN'))
                logging.info(f"Successfully processed: {input_file}")
                if output_file:
                    converted_files.append(output_file)
                else:
                    converted_files.append(input_file.rsplit('.', 1)[0] + '.adoc')
            else:
                failed += 1
                if not quiet:
                    print(color_manager.color_text("❌ Failure.", 'RED'))
                logging.error(f"Failed to process: {input_file}")
        except Exception as e:
            failed += 1
            if not quiet:
                print(color_manager.color_text("❌ Failure.", 'RED'))
            logging.exception(f"Error processing {input_file}")
    
    if not quiet:
        status = color_manager.color_text("Zero failures! Too easy", 'GREEN') if failed == 0 else color_manager.color_text("Review above for any issues.", 'YELLOW')
        print(f"\n✨ Conversion complete! {successful} succeeded, {failed} failed. {status}")
        
        if image_dir:
            print(color_manager.color_text(f"🖼️  Images sent to: {image_dir}", 'BLUE'))
    
    logging.info(f"Conversion complete: {successful} succeeded, {failed} failed")
    if image_dir:
        logging.info(f"Images extracted to: {image_dir}")
    
    return converted_files, failed == 0

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='''
DOCX to AsciiDoc Converter with Enhanced Features
----------------------------------------------
A powerful tool to convert DOCX files to AsciiDoc format with smart processing
and formatting options. Handles multiple files, directories, and provides
detailed feedback during conversion.

Features:
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

Exit Codes:
  0 (SUCCESS) - Successful completion
  1 (FAILURE) - One or more files failed to process
  2 (CRITICAL) - Critical error (e.g., Pandoc not installed)

Examples:
  # Convert a single file
  python a_converter_final.py document.docx

  # Convert multiple files with verbose logging
  python a_converter_final.py doc1.docx doc2.docx --verbose

  # Convert with logging to file
  python a_converter_final.py document.docx --log-file conversion.log

  # Test run without making changes
  python a_converter_final.py ./documents/ --dry-run

  # Quiet mode for automation
  python a_converter_final.py document.docx --quiet

  # Convert all DOCX files in a directory
  python a_converter_final.py ./documents/

  # Convert recursively with image extraction and heading generalization
  python a_converter_final.py ./documents/ -r -i ./images/ -g

  # Convert and save to specific output directory
  python a_converter_final.py document.docx -o ./output/

  # Convert without color output (useful for logging and scripts)
  python a_converter_final.py document.docx --no-color

  # Keep section numbers during conversion
  python a_converter_final.py document.docx -k
''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Version information
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    # Main arguments (always visible)
    parser.add_argument(
        'input',
        nargs='+',
        help='Input DOCX file(s) or directory to convert. Can specify multiple files or directories.'
    )
    parser.add_argument(
        '-g', '--generalize-headings',
        action='store_true',
        help='Run heading generalization after conversion (ensures proper heading hierarchy starting at level 2)'
    )
    parser.add_argument(
        '-k', '--keep-numbers',
        action='store_true',
        help='Keep section numbers from the original document (default: False)'
    )
    
    input_group = parser.add_argument_group('Input/Output Options')
    input_group.add_argument(
        '-o', '--output-dir',
        help='Output directory for converted files. If not specified, files will be created alongside the input files.',
        metavar='DIR'
    )
    input_group.add_argument(
        '-i', '--image-dir',
        help='Directory to extract images to. Each document\'s images will be placed in a subdirectory named after the document.',
        metavar='DIR'
    )
    
    processing_group = parser.add_argument_group('Processing Options')
    processing_group.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Recursively process DOCX files when input is a directory'
    )
    
    display_group = parser.add_argument_group('Display Options')
    display_group.add_argument(
        '--no-color',
        action='store_true',
        help='Disable color output. Colors can also be disabled by setting the NO_COLOR environment variable.'
    )
    
    logging_group = parser.add_argument_group('Logging Options')
    logging_group.add_argument(
        '--log-file',
        help='Write detailed logs to specified file',
        metavar='FILE'
    )
    logging_group.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    automation_group = parser.add_argument_group('Automation Options')
    automation_group.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress all output except errors (useful for automation)'
    )
    automation_group.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making any changes'
    )
    
    args = parser.parse_args()
    
    # Configure color manager based on arguments
    color_manager.set_color_mode(args.no_color)
    
    return args

def format_time(seconds):
    """Format time duration in a human-readable way."""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    minutes = int(seconds // 60)
    seconds = seconds % 60
    if minutes < 60:
        return f"{minutes}m {seconds:.1f}s"
    hours = int(minutes // 60)
    minutes = minutes % 60
    return f"{hours}h {minutes}m {seconds:.1f}s"

def main():
    """Main entry point for the script."""
    start_time = time()
    
    try:
        # Parse arguments first to get logging options
        args = parse_arguments()
        
        # Set up logging with appropriate quietness level
        if args.log_file:
            log_name, log_ext = os.path.splitext(args.log_file)
            if not any(c.isdigit() for c in log_name):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                args.log_file = f"{log_name}_{timestamp}{log_ext}"
        
        setup_logging(args.log_file, args.verbose and not args.quiet)
        logging.info("Starting DOCX to AsciiDoc converter")
        logging.info(f"Version: {__version__}")
        logging.info(f"Command line: {' '.join(sys.argv)}")
        
        if args.dry_run:
            logging.info("Running in DRY RUN mode - no files will be modified")
        
        # Check dependencies before proceeding
        check_dependencies()
        
        # Normalize paths to absolute
        args.output_dir = abspath_or_none(args.output_dir)
        args.image_dir = abspath_or_none(args.image_dir)
        logging.debug(f"Output directory: {args.output_dir}")
        logging.debug(f"Image directory: {args.image_dir}")
        
        # Validate output and image directories
        for dirpath in [args.output_dir, args.image_dir]:
            if dirpath and os.path.exists(dirpath) and not os.path.isdir(dirpath):
                raise Exception(f"{dirpath} exists and is not a directory!")
        
        # Create directories if needed (unless in dry-run mode)
        if not args.dry_run:
            if args.output_dir and not os.path.exists(args.output_dir):
                os.makedirs(args.output_dir)
                logging.debug(f"Created output directory: {args.output_dir}")
            if args.image_dir and not os.path.exists(args.image_dir):
                os.makedirs(args.image_dir)
                logging.debug(f"Created image directory: {args.image_dir}")
        
        # Collect all input files
        input_files = []
        for input_path in args.input:
            if os.path.isdir(input_path):
                # If input is a directory, find all DOCX files
                pattern = '**/*.docx' if args.recursive else '*.docx'
                docx_files = glob.glob(os.path.join(input_path, pattern), recursive=args.recursive)
                input_files.extend(docx_files)
            else:
                # If input is a file, add it directly
                input_files.append(input_path)
        
        if not input_files:
            logging.error("No DOCX files found to process")
            return EXIT_FAILURE
        
        # Convert all paths to absolute
        input_files = [os.path.abspath(f) for f in input_files]
        
        # Process all files
        converted_files, all_successful = process_files(
            input_files, 
            args.output_dir, 
            args.keep_numbers, 
            args.image_dir,
            args.dry_run,
            args.quiet
        )
        
        # Exit with appropriate code and message
        runtime = format_time(time() - start_time)
        if all_successful:
            if not args.quiet:
                print(color_manager.color_text("\n😎 Smooth sailing! Everything worked perfectly. Time to grab a ☕", 'GREEN'))
                print(color_manager.color_text(f"⏱️  Total runtime: {runtime}", 'BLUE'))
                print(color_manager.color_text("🏁 Exit status: 0 (Success)", 'GREEN'))
            logging.info(f"Completed successfully in {runtime}")
            return EXIT_SUCCESS
        else:
            if not args.quiet:
                print(color_manager.color_text("\n😅 Well, that was... interesting. Check the logs above for what went sideways!", 'YELLOW'))
                print(color_manager.color_text(f"⏱️  Total runtime: {runtime}", 'BLUE'))
                print(color_manager.color_text("🚨 Exit status: 1 (Errors occurred)", 'RED'))
            logging.error(f"Completed with errors in {runtime}")
            return EXIT_FAILURE
            
    except Exception as e:
        try:
            logging.exception("Unexpected error occurred")
        except Exception:
            print("Unexpected error occurred:", e, file=sys.stderr)
        if not args.quiet:
            print(color_manager.color_text("\n💥 Whoops! Something unexpected happened.", 'RED'))
            print(color_manager.color_text(
                f"Check the logs for details: {args.log_file if hasattr(args, 'log_file') and args.log_file else 'No log file specified'}", 
                'YELLOW'
            ))
        return EXIT_CRITICAL

if __name__ == "__main__":
    sys.exit(main()) 