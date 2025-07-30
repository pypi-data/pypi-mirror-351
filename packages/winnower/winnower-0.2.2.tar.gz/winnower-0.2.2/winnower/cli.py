#!/usr/bin/env python3
"""Command-line interface for The Winnower."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .core import WinnowerProcessor
from .config import load_config, setup_user_env, check_api_keys


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="winnower",
        description="Extract core technical details from research papers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  winnower setup                              # Set up configuration
  winnower paper.pdf
  winnower https://arxiv.org/abs/2501.00089
  winnower 2501.00089
  winnower /path/to/papers/ --recursive
        """,
    )

    # Add main processing arguments
    _add_main_arguments(parser)

    return parser


def _add_main_arguments(parser: argparse.ArgumentParser) -> None:
    """Add main processing arguments to parser."""

    parser.add_argument(
        "input",
        nargs="?",
        help="Paper input: file path, directory, URL, or arXiv ID",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output directory (default: ./winnower_output)",
        default=Path.cwd() / "winnower_output",
    )

    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Process directory recursively",
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Configuration file path",
    )

    parser.add_argument(
        "--model",
        choices=["openai", "anthropic"],
        default="openai",
        help="AI model provider (default: openai)",
    )

    parser.add_argument(
        "--prompt-file",
        type=Path,
        help="Custom extraction prompt file",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--no-markdown",
        action="store_true",
        help="Disable PDF to markdown conversion (use legacy text extraction)",
    )

    parser.add_argument(
        "--length",
        type=int,
        help="Target length for technical summary in words (default: 200)",
        metavar="WORDS",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__import__('winnower').__version__}",
    )

    return parser


def setup_command(args) -> int:
    """Handle setup command."""
    print("Setting up The Winnower...")

    # Set up user environment
    env_path = setup_user_env()
    print(f"Created configuration directory: {env_path.parent}")
    print(f"Created environment template: {env_path}")

    # Check current API key status
    api_status = check_api_keys()
    print("\nAPI Key Status:")
    print(
        f"  OpenAI: {'✓ Found' if api_status['openai'] else '✗ Not found'}"
    )
    print(
        f"  Anthropic: "
        f"{'✓ Found' if api_status['anthropic'] else '✗ Not found'}"
    )

    if not any(api_status.values()):
        print(
            f"\n⚠️  No API keys found. Please edit {env_path} "
            f"and add your API key."
        )
        print("   You need either OPENAI_API_KEY or ANTHROPIC_API_KEY.")
    else:
        print("\n✓ API keys found. You're ready to use The Winnower!")

    return 0


def main(argv: Optional[list] = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)

    # Handle setup command as special case
    if args.input == "setup":
        return setup_command(args)

    # Handle main processing (default behavior)
    if not args.input:
        parser.print_help()
        return 1

    try:
        config = load_config(getattr(args, "config", None))

        # Override config with CLI arguments
        if hasattr(args, "prompt_file") and args.prompt_file:
            config["prompt_file"] = str(args.prompt_file)

        if hasattr(args, "no_markdown") and args.no_markdown:
            config["pdf_to_markdown"] = False

        if hasattr(args, "length") and args.length:
            config["summary_length"] = args.length

        processor = WinnowerProcessor(
            config,
            getattr(args, "model", "openai"),
            getattr(args, "verbose", False),
        )

        processor.process(
            input_source=args.input,
            output_dir=getattr(args, "output", Path.cwd()),
            recursive=getattr(args, "recursive", False),
        )

        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
