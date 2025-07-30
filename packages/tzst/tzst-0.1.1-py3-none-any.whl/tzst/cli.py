"""Command-line interface for tzst."""

import argparse
import sys
import time
from pathlib import Path
from typing import List, Optional

from . import __version__
from .core import create_archive, extract_archive, list_archive, test_archive
from .exceptions import TzstArchiveError, TzstDecompressionError


def format_size(size: int) -> str:
    """Format file size in human-readable format."""
    size_float = float(size)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_float < 1024.0:
            return f"{size_float:6.1f} {unit}"
        size_float /= 1024.0
    return f"{size_float:6.1f} PB"


def format_size_compact(size: int) -> str:
    """Format file size in compact format for 7z-style output."""
    if size < 1024:
        return f"{size} bytes"
    elif size < 1024 * 1024:
        return f"{size // 1024} KiB"
    elif size < 1024 * 1024 * 1024:
        return f"{size // (1024 * 1024)} MiB"
    else:
        return f"{size // (1024 * 1024 * 1024)} GiB"


def print_header():
    """Print copyright/version header similar to 7z."""
    print(f"tzst {__version__} : Copyright (c) 2025, tzst contributors")
    print()


def print_archive_info(archive_path: Path):
    """Display archive information similar to 7z."""
    print("--")
    print(f"Path = {archive_path}")
    print("Type = tzst")

    # Get file size
    size = archive_path.stat().st_size
    print(f"Physical Size = {size}")

    # Add compression method info
    print("Method = Zstandard")
    print()


def prompt_for_overwrite(existing_path: Path, archived_info: dict) -> str:
    """Prompt user for file overwrite decision, similar to 7z."""
    print("\nWould you like to replace the existing file:")
    print(f"  Path:     .\\{existing_path.name}")
    print(
        f"  Size:     {existing_path.stat().st_size} bytes ({format_size_compact(existing_path.stat().st_size)})"
    )
    print(
        f"  Modified: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(existing_path.stat().st_mtime))}"
    )
    print("with the file from archive:")
    print(f"  Path:     {archived_info['name']}")
    print(
        f"  Size:     {archived_info['size']} bytes ({format_size_compact(archived_info['size'])})"
    )
    mtime_str = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(archived_info.get("mtime", 0))
    )
    print(f"  Modified: {mtime_str}")

    while True:
        choice = input(
            "? (Y)es / (N)o / (A)lways / (S)kip all / A(u)to rename all / (Q)uit? "
        ).lower()
        if choice in ("y", "n", "a", "s", "u", "q"):
            return choice
        print("Please enter Y, N, A, S, U, or Q")


def cmd_add(args) -> int:
    """Add/create archive command."""
    try:
        archive_path = Path(args.archive)
        files: List[Path] = [Path(f) for f in args.files]

        # Check if files exist
        missing_files = [f for f in files if not f.exists()]
        if missing_files:
            print(
                f"Error: Files not found: {', '.join(map(str, missing_files))}",
                file=sys.stderr,
            )
            return 1

        print_header()

        print("Scanning the drive:")

        # Count folders and files to be added
        total_dirs = 0
        total_files = 0
        total_size = 0

        for file_path in files:
            if file_path.is_file():
                total_files += 1
                total_size += file_path.stat().st_size
            elif file_path.is_dir():
                total_dirs += 1
                # Count files in directory
                for f in file_path.rglob("*"):
                    if f.is_file():
                        total_files += 1
                        total_size += f.stat().st_size
                    elif f.is_dir():
                        total_dirs += 1

        print(
            f"{total_dirs} folders, {total_files} files, {total_size} bytes ({format_size_compact(total_size)})"
        )
        print()

        print(f"Creating archive: {archive_path}")
        print()
        print(
            f"Add new data to archive: {total_dirs} folders, {total_files} files, {total_size} bytes ({format_size_compact(total_size)})"
        )
        print()

        compression_level = getattr(args, "compression_level", 3)
        create_archive(archive_path, files, compression_level)

        # Calculate result statistics
        archive_size = archive_path.stat().st_size

        print()
        print(f"Files read from disk: {total_files}")
        print(
            f"Archive size: {archive_size} bytes ({format_size_compact(archive_size)})"
        )
        print("Everything is Ok")

        return 0

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: Invalid parameter - {e}", file=sys.stderr)
        return 1
    except TzstArchiveError as e:
        print(f"Error: Archive operation failed - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error creating archive: {e}", file=sys.stderr)
        return 1


def cmd_extract_full(args) -> int:
    """Extract with full paths command."""
    try:
        archive_path = Path(args.archive)
        if not archive_path.exists():
            print(f"Error: Archive not found: {archive_path}", file=sys.stderr)
            return 1

        print_header()
        print("Scanning the drive for archives:")
        print(
            f"1 file, {archive_path.stat().st_size} bytes ({format_size_compact(archive_path.stat().st_size)})"
        )
        print()
        print(f"Extracting archive: {archive_path}")

        print_archive_info(archive_path)

        output_dir = Path(args.output) if args.output else Path.cwd()
        members = args.files if hasattr(args, "files") and args.files else None

        extract_archive(
            archive_path,
            output_dir,
            members,
            flatten=False,
            conflict_callback=prompt_for_overwrite,
        )

        print("Everything is Ok")

        # Add statistics like 7z
        contents = list_archive(archive_path)
        total_files = sum(1 for item in contents if item["is_file"])
        total_dirs = sum(1 for item in contents if item["is_dir"])
        total_size = sum(item["size"] for item in contents if item["is_file"])

        print()
        print(f"Folders: {total_dirs}")
        print(f"Files: {total_files}")
        print(f"Size:       {total_size}")
        print(f"Compressed: {archive_path.stat().st_size}")

        return 0

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        return 1
    except TzstDecompressionError as e:
        print(f"Error: Archive decompression failed - {e}", file=sys.stderr)
        return 1
    except TzstArchiveError as e:
        print(f"Error: Archive operation failed - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error extracting archive: {e}", file=sys.stderr)
        return 1


def cmd_extract_flat(args) -> int:
    """Extract without paths (flat) command."""
    try:
        archive_path = Path(args.archive)
        if not archive_path.exists():
            print(f"Error: Archive not found: {archive_path}", file=sys.stderr)
            return 1

        print_header()
        print("Scanning the drive for archives:")
        print(
            f"1 file, {archive_path.stat().st_size} bytes ({format_size_compact(archive_path.stat().st_size)})"
        )
        print()
        print(f"Extracting archive: {archive_path}")

        print_archive_info(archive_path)

        output_dir = Path(args.output) if args.output else Path.cwd()
        members = args.files if hasattr(args, "files") and args.files else None

        extract_archive(
            archive_path,
            output_dir,
            members,
            flatten=True,
            conflict_callback=prompt_for_overwrite,
        )

        print("Everything is Ok")

        # Add statistics like 7z
        contents = list_archive(archive_path)
        total_files = sum(1 for item in contents if item["is_file"])
        total_dirs = sum(1 for item in contents if item["is_dir"])
        total_size = sum(item["size"] for item in contents if item["is_file"])

        print()
        print(f"Folders: {total_dirs}")
        print(f"Files: {total_files}")
        print(f"Size:       {total_size}")
        print(f"Compressed: {archive_path.stat().st_size}")

        return 0

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        return 1
    except TzstDecompressionError as e:
        print(f"Error: Archive decompression failed - {e}", file=sys.stderr)
        return 1
    except TzstArchiveError as e:
        print(f"Error: Archive operation failed - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error extracting archive: {e}", file=sys.stderr)
        return 1


def cmd_list(args) -> int:
    """List archive contents command."""
    try:
        archive_path = Path(args.archive)
        if not archive_path.exists():
            print(f"Error: Archive not found: {archive_path}", file=sys.stderr)
            return 1

        print_header()
        print("Scanning the drive for archives:")
        print(
            f"1 file, {archive_path.stat().st_size} bytes ({format_size_compact(archive_path.stat().st_size)})"
        )
        print()
        print(f"Listing archive: {archive_path}")
        print()

        print_archive_info(archive_path)

        getattr(args, "verbose", False)
        contents = list_archive(archive_path, verbose=True)

        # Format similar to 7z listing
        print(
            f"{'Date':<10} {'Time':<8} {'Attr':<5} {'Size':>12} {'Compressed':>12}  {'Name'}"
        )
        print(f"{'-'*10} {'-'*8} {'-'*5} {'-'*12} {'-'*12}  {'-'*24}")

        total_files = 0
        total_dirs = 0
        total_size = 0

        for item in contents:
            # Format date and time
            mtime = item.get("mtime", 0)
            date_str = time.strftime("%Y-%m-%d", time.localtime(mtime))
            time_str = time.strftime("%H:%M:%S", time.localtime(mtime))

            # Attribute string
            attr = "D...." if item["is_dir"] else "....A"

            # Size formatting
            size_str = f"{item['size']:,}" if item["is_file"] else "0"
            comp_size = ""  # Would need to calculate compressed size per file

            print(
                f"{date_str} {time_str} {attr} {size_str:>12} {comp_size:>12}  {item['name']}"
            )

            if item["is_file"]:
                total_files += 1
                total_size += item["size"]
            elif item["is_dir"]:
                total_dirs += 1

        print(f"{'-'*10} {'-'*8} {'-'*5} {'-'*12} {'-'*12}  {'-'*24}")
        print(
            f"{' '*28} {total_size:>12} {archive_path.stat().st_size:>12}  {total_files} files, {total_dirs} folders"
        )

        return 0

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        return 1
    except TzstDecompressionError as e:
        print(f"Error: Archive decompression failed - {e}", file=sys.stderr)
        return 1
    except TzstArchiveError as e:
        print(f"Error: Archive operation failed - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error listing archive: {e}", file=sys.stderr)
        return 1


def cmd_test(args) -> int:
    """Test archive integrity command."""
    try:
        archive_path = Path(args.archive)
        if not archive_path.exists():
            print(f"Error: Archive not found: {archive_path}", file=sys.stderr)
            return 1

        print_header()
        print("Scanning the drive for archives:")
        print(
            f"1 file, {archive_path.stat().st_size} bytes ({format_size_compact(archive_path.stat().st_size)})"
        )
        print()
        print(f"Testing archive: {archive_path}")

        print_archive_info(archive_path)

        if test_archive(archive_path):
            print("Everything is Ok")

            # Add statistics like 7z
            contents = list_archive(archive_path)
            total_files = sum(1 for item in contents if item["is_file"])
            total_dirs = sum(1 for item in contents if item["is_dir"])
            total_size = sum(item["size"] for item in contents if item["is_file"])

            print()
            print(f"Folders: {total_dirs}")
            print(f"Files: {total_files}")
            print(f"Size:       {total_size}")
            print(f"Compressed: {archive_path.stat().st_size}")

            return 0
        else:
            print("Archive test failed - errors detected", file=sys.stderr)
            return 1

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        return 1
    except TzstDecompressionError as e:
        print(f"Error: Archive decompression failed - {e}", file=sys.stderr)
        return 1
    except TzstArchiveError as e:
        print(f"Error: Archive operation failed - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error testing archive: {e}", file=sys.stderr)
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="tzst",
        description="Create and manipulate .tzst/.tar.zst archives",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage: tzst <command> [<switches>...] <archive_name> [<file_names>...]

<Commands>
  a : Add files to archive
  e : Extract files from archive (without using directory names)
  l : List contents of archive
  t : Test integrity of archive
  x : eXtract files with full paths

Examples:
  tzst a archive.tzst file1.txt file2.txt dir/     # Create archive
  tzst x archive.tzst                              # Extract with paths
  tzst e archive.tzst -o output/                   # Extract flat to output/
  tzst l archive.tzst                              # List contents
  tzst l archive.tzst -v                           # List with details
  tzst t archive.tzst                              # Test integrity
        """,
    )

    parser.add_argument("--version", action="version", version=f"tzst {__version__}")

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", metavar="COMMAND"
    )

    # Add/Create command
    parser_add = subparsers.add_parser(
        "a", aliases=["add", "create"], help="Create archive or add files to archive"
    )
    parser_add.add_argument("archive", help="Archive file path")
    parser_add.add_argument("files", nargs="+", help="Files/directories to add")
    parser_add.add_argument(
        "-l",
        "--level",
        dest="compression_level",
        type=int,
        default=3,
        choices=range(1, 23),
        metavar="LEVEL",
        help="Compression level (1-22, default: 3)",
    )
    parser_add.set_defaults(func=cmd_add)

    # Extract with full paths command
    parser_extract = subparsers.add_parser(
        "x", aliases=["extract"], help="Extract files with full paths"
    )
    parser_extract.add_argument("archive", help="Archive file path")
    parser_extract.add_argument("files", nargs="*", help="Specific files to extract")
    parser_extract.add_argument(
        "-o", "--output", help="Output directory (default: current directory)"
    )
    parser_extract.set_defaults(func=cmd_extract_full)

    # Extract flat command
    parser_extract_flat = subparsers.add_parser(
        "e",
        aliases=["extract-flat"],
        help="Extract files without paths (flat structure)",
    )
    parser_extract_flat.add_argument("archive", help="Archive file path")
    parser_extract_flat.add_argument(
        "files", nargs="*", help="Specific files to extract"
    )
    parser_extract_flat.add_argument(
        "-o", "--output", help="Output directory (default: current directory)"
    )
    parser_extract_flat.set_defaults(func=cmd_extract_flat)

    # List command
    parser_list = subparsers.add_parser(
        "l", aliases=["list"], help="List archive contents"
    )
    parser_list.add_argument("archive", help="Archive file path")
    parser_list.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed information"
    )
    parser_list.set_defaults(func=cmd_list)

    # Test command
    parser_test = subparsers.add_parser(
        "t", aliases=["test"], help="Test archive integrity"
    )
    parser_test.add_argument("archive", help="Archive file path")
    parser_test.set_defaults(func=cmd_test)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
