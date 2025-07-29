#!/usr/bin/env python3
"""
Command-line interface for Sanitizr URL Cleaner.

This module provides a CLI for cleaning URLs using the Sanitizr core engine.
"""

import argparse
import sys
from typing import List, Optional, TextIO

from ..core.cleaner import URLCleaner
from ..config.config import ConfigManager


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="cleanurl",
        description="Clean URLs by removing tracking parameters and decoding redirects.",
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Input file path (one URL per line). If not specified, stdin is used."
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path. If not specified, stdout is used."
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to configuration file (JSON or YAML)."
    )
    
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Show what would be done without actually cleaning."
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output (before and after URLs)."
    )
    
    parser.add_argument(
        "--url", "-u",
        type=str,
        help="Clean a single URL directly from the command line."
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
        help="Show program's version number and exit."
    )
    
    return parser.parse_args()


def process_urls(
    cleaner: URLCleaner,
    input_stream: TextIO,
    output_stream: TextIO,
    dry_run: bool = False,
    verbose: bool = False,
) -> None:
    """
    Process URLs from input stream and write cleaned URLs to output stream.
    
    Args:
        cleaner: URLCleaner instance
        input_stream: Input stream to read URLs from
        output_stream: Output stream to write cleaned URLs to
        dry_run: If True, don't actually clean URLs, just show what would be done
        verbose: If True, show both original and cleaned URLs
    """
    for line in input_stream:
        line = line.strip()
        if not line:
            continue
            
        # Skip comments
        if line.startswith("#"):
            if not dry_run:
                output_stream.write(f"{line}\n")
            continue
            
        # Clean the URL
        cleaned_url = line if dry_run else cleaner.clean_url(line)
        
        # Output according to options
        if verbose:
            if cleaned_url != line:
                output_stream.write(f"Original: {line}\n")
                output_stream.write(f"Cleaned:  {cleaned_url}\n\n")
            else:
                output_stream.write(f"Unchanged: {line}\n\n")
        else:
            output_stream.write(f"{cleaned_url}\n")


def main() -> int:
    """Main entry point for the CLI."""
    args = parse_args()
    
    # Load configuration
    try:
        config_manager = ConfigManager(args.config)
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        return 1
        
    # Create the URL cleaner
    cleaner = URLCleaner(
        custom_tracking_params=config_manager.get_tracking_params(),
        custom_redirect_params=config_manager.get_redirect_params(),
        whitelist_params=config_manager.get_whitelist_params(),
        blacklist_params=config_manager.get_blacklist_params(),
    )
    
    # Handle single URL case
    if args.url:
        cleaned_url = args.url if args.dry_run else cleaner.clean_url(args.url)
        if args.verbose:
            print(f"Original: {args.url}")
            print(f"Cleaned:  {cleaned_url}")
        else:
            print(cleaned_url)
        return 0
        
    # Set up input stream
    try:
        if args.input:
            input_stream = open(args.input, "r", encoding="utf-8")
        else:
            input_stream = sys.stdin
    except Exception as e:
        print(f"Error opening input file: {e}", file=sys.stderr)
        return 1
        
    # Set up output stream
    try:
        if args.output:
            output_stream = open(args.output, "w", encoding="utf-8")
        else:
            output_stream = sys.stdout
    except Exception as e:
        print(f"Error opening output file: {e}", file=sys.stderr)
        if args.input and input_stream != sys.stdin:
            input_stream.close()
        return 1
        
    # Process the URLs
    try:
        process_urls(
            cleaner,
            input_stream,
            output_stream,
            dry_run=args.dry_run,
            verbose=args.verbose
        )
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 130  # Standard exit code for SIGINT
    except Exception as e:
        print(f"Error processing URLs: {e}", file=sys.stderr)
        return 1
    finally:
        # Clean up resources
        if args.input and input_stream != sys.stdin:
            input_stream.close()
        if args.output and output_stream != sys.stdout:
            output_stream.close()
            
    return 0


if __name__ == "__main__":
    sys.exit(main())