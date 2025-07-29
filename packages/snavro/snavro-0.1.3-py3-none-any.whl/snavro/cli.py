"""
Command-line interface for Snavro.

This module provides the CLI functionality for reading and displaying
Parquet and Avro files from the command line.
"""

import sys

from .reader import FileReader, get_supported_files


def main() -> None:
    """Main CLI entry point."""
    reader = FileReader()

    if len(sys.argv) > 1:
        # File path provided as command line argument
        file_path = sys.argv[1]
        num_rows = int(sys.argv[2]) if len(sys.argv) > 2 else 5

        if not reader.is_supported_file(file_path):
            print("Error: Unsupported file format.")
            print(
                f"Supported formats: {reader.SUPPORTED_EXTENSIONS}, "
                f"{reader.SUPPORTED_PATTERNS}"
            )
            sys.exit(1)

        reader.display_file_info(file_path, num_rows)
    else:
        # Interactive mode - list available files and let user choose
        print("Snavro - Unified Parquet and Avro File Reader")
        print("=" * 45)
        print("Available files in current directory:")
        print("-" * 40)

        supported_files = get_supported_files()

        if not supported_files:
            print("No supported files found in current directory.")
            print(
                f"Supported formats: {reader.SUPPORTED_EXTENSIONS}, "
                f"{reader.SUPPORTED_PATTERNS}"
            )
            return

        for i, file in enumerate(supported_files, 1):
            print(f"  {i}. {file}")

        try:
            choice = input(
                "\nEnter file number " f"(1-{len(supported_files)}) or file path: "
            ).strip()

            if choice.isdigit():
                file_index = int(choice) - 1
                if 0 <= file_index < len(supported_files):
                    file_path = supported_files[file_index]
                else:
                    print("Invalid file number.")
                    return
            else:
                file_path = choice
                if not reader.is_supported_file(file_path):
                    print("Error: Unsupported file format.")
                    print(
                        f"Supported formats: {reader.SUPPORTED_EXTENSIONS}, "
                        f"{reader.SUPPORTED_PATTERNS}"
                    )
                    return

            num_rows_input = input("Number of rows to display (default 5): ").strip()
            num_rows = int(num_rows_input) if num_rows_input.isdigit() else 5

            print()
            reader.display_file_info(file_path, num_rows)

        except KeyboardInterrupt:
            print("\nExiting...")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
