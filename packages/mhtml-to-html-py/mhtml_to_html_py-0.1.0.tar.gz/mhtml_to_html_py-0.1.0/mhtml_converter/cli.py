#!/usr/bin/env python3
"""
Command-line interface for mhtml-to-html Python package.
"""

import argparse
import sys
from pathlib import Path
from .converter import convert_mhtml


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert MHTML files to HTML with automatic encoding detection"
    )
    parser.add_argument(
        "mhtml_file",
        help="Input MHTML file (.mht or .mhtml)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output HTML file (default: print to stdout)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output (shows encoding detection)"
    )
    
    args = parser.parse_args()
    
    try:
        result = convert_mhtml(
            args.mhtml_file,
            verbose=args.verbose,
            output_file=args.output
        )
        
        if args.output:
            print(f"Converted MHTML to: {result}")
        else:
            # Print HTML to stdout
            print(result, end="")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 