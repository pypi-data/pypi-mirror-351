#!/usr/bin/env python3
"""
Command Line Interface for README to Word Converter

This module provides a CLI for converting README files to Word documents.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

from . import __description__, __version__
from .converter import ReadmeToWordConverter


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="readme2word",
        description=__description__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  readme2word README.md                    # Convert README.md to README.docx
  readme2word README.md -o report.docx     # Convert with custom output name
  readme2word README.md --debug            # Enable debug mode
  readme2word README.md --theme dark       # Use dark theme for diagrams
  readme2word --web                        # Launch web interface

For more information, visit: https://github.com/vishalm/readme2readall
        """,
    )

    parser.add_argument("input_file", nargs="?", help="Input README.md file to convert")

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output Word document filename (default: input_name.docx)",
    )

    parser.add_argument(
        "--theme",
        choices=["default", "neutral", "dark", "forest"],
        default="default",
        help="Mermaid diagram theme (default: default)",
    )

    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode with verbose logging"
    )

    parser.add_argument(
        "--no-toc", action="store_true", help="Disable table of contents generation"
    )

    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch web interface instead of CLI conversion",
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    return parser


def validate_input_file(file_path: str) -> Path:
    """Validate that the input file exists and is readable."""
    path = Path(file_path)

    if not path.exists():
        print(f"Error: Input file '{file_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if not path.is_file():
        print(f"Error: '{file_path}' is not a file.", file=sys.stderr)
        sys.exit(1)

    if not path.suffix.lower() in [".md", ".markdown"]:
        print(f"Warning: '{file_path}' does not have a .md or .markdown extension.")

    try:
        with open(path, "r", encoding="utf-8") as f:
            f.read(1)  # Try to read one character
    except (IOError, UnicodeDecodeError) as e:
        print(f"Error: Cannot read input file '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)

    return path


def generate_output_filename(input_path: Path, output: Optional[str]) -> str:
    """Generate the output filename."""
    if output:
        return output

    # Replace extension with .docx
    return str(input_path.with_suffix(".docx"))


def convert_file(
    input_path: Path, output_filename: str, theme: str, debug: bool, include_toc: bool
) -> bool:
    """Convert a single file and return success status."""
    try:
        # Read input file
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Initialize converter
        converter = ReadmeToWordConverter()
        if debug:
            converter.set_debug_mode(True)

        # Perform conversion
        print(f"Converting '{input_path}' to '{output_filename}'...")

        actual_output_path = converter.convert(
            readme_content=content,
            output_filename=output_filename,
            include_toc=include_toc,
            diagram_style=theme,
        )

        if actual_output_path:
            print(f"✅ Conversion completed successfully!")
            print(f"📄 Output file: {actual_output_path}")

            # Show statistics if available
            stats = getattr(converter, "conversion_stats", None)
            if stats:
                print(f"\n📊 Conversion Statistics:")
                for key, value in stats.items():
                    print(f"   {key}: {value}")

            return True
        else:
            print(f"❌ Conversion failed. Check the logs for details.", file=sys.stderr)
            return False

    except Exception as e:
        print(f"❌ Error during conversion: {e}", file=sys.stderr)
        if debug:
            import traceback

            traceback.print_exc()
        return False


def launch_web_interface() -> None:
    """Launch the web interface."""
    try:
        from .web import main as web_main

        print("🚀 Launching web interface...")
        print("📱 Open your browser to the URL shown below:")
        web_main()
    except ImportError:
        print("❌ Web interface dependencies not available.", file=sys.stderr)
        print("💡 Install with: pip install readme2word[web]", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error launching web interface: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle web interface
    if args.web:
        launch_web_interface()
        return

    # Validate input file is provided
    if not args.input_file:
        print(
            "Error: Input file is required (or use --web for web interface)",
            file=sys.stderr,
        )
        parser.print_help()
        sys.exit(1)

    # Validate input file
    input_path = validate_input_file(args.input_file)

    # Generate output filename
    output_filename = generate_output_filename(input_path, args.output)

    # Check if output file already exists
    if os.path.exists(output_filename):
        response = input(
            f"Output file '{output_filename}' already exists. Overwrite? (y/N): "
        )
        if response.lower() not in ["y", "yes"]:
            print("Conversion cancelled.")
            sys.exit(0)

    # Perform conversion
    include_toc = not args.no_toc
    success = convert_file(
        input_path, output_filename, args.theme, args.debug, include_toc
    )

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
