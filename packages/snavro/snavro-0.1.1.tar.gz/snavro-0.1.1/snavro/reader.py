"""
Core file reading functionality for Snavro.

This module provides the main FileReader class and utility functions for reading
Parquet and Avro files with automatic format detection.
"""

import os
from pathlib import Path
from typing import Union, List, Dict, Any

import pandas as pd
import fastavro


class FileReader:
    """
    A unified file reader for Parquet and Avro files with automatic format detection.

    Supports:
    - .parquet files
    - .parquet.snappy files (compressed Parquet)
    - .avro files
    """

    SUPPORTED_EXTENSIONS = {".parquet", ".avro"}
    SUPPORTED_PATTERNS = {".parquet.snappy"}

    def __init__(self):
        """Initialize the FileReader."""
        pass

    def is_supported_file(self, file_path: Union[str, Path]) -> bool:
        """
        Check if a file is supported by this reader.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is supported, False otherwise
        """
        file_path = Path(file_path)
        file_extension = file_path.suffix.lower()
        file_name = file_path.name.lower()

        return file_extension in self.SUPPORTED_EXTENSIONS or any(
            file_name.endswith(pattern) for pattern in self.SUPPORTED_PATTERNS
        )

    def read_parquet(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Read a Parquet file (including .snappy compressed).

        Args:
            file_path: Path to the Parquet file

        Returns:
            pandas DataFrame containing the data

        Raises:
            FileNotFoundError: If the file doesn't exist
            Exception: If there's an error reading the file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' not found.")

        return pd.read_parquet(file_path, engine="pyarrow")

    def read_avro(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Read an Avro file.

        Args:
            file_path: Path to the Avro file

        Returns:
            List of records (dictionaries)

        Raises:
            FileNotFoundError: If the file doesn't exist
            Exception: If there's an error reading the file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' not found.")

        with open(file_path, "rb") as f:
            reader = fastavro.reader(f)
            return [record for record in reader]

    def read_file(
        self, file_path: Union[str, Path]
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Read a file with automatic format detection.

        Args:
            file_path: Path to the file to read

        Returns:
            pandas DataFrame for Parquet files, List of records for Avro files

        Raises:
            ValueError: If the file format is not supported
            FileNotFoundError: If the file doesn't exist
            Exception: If there's an error reading the file
        """
        file_path = Path(file_path)

        if not self.is_supported_file(file_path):
            raise ValueError(
                f"Unsupported file format. Supported formats: {self.SUPPORTED_EXTENSIONS}, {self.SUPPORTED_PATTERNS}"
            )

        file_extension = file_path.suffix.lower()
        file_name = file_path.name.lower()

        # Handle Parquet files (including .snappy compressed)
        if file_extension == ".parquet" or file_name.endswith(".parquet.snappy"):
            return self.read_parquet(file_path)

        # Handle Avro files
        elif file_extension == ".avro":
            return self.read_avro(file_path)

        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

    def display_file_info(self, file_path: Union[str, Path], num_rows: int = 5) -> None:
        """
        Read and display information about a file.

        Args:
            file_path: Path to the file
            num_rows: Number of rows/records to display (default: 5)
        """
        try:
            data = self.read_file(file_path)
            file_path = Path(file_path)
            file_extension = file_path.suffix.lower()
            file_name = file_path.name.lower()

            # Handle Parquet files
            if file_extension == ".parquet" or file_name.endswith(".parquet.snappy"):
                print(f"Reading Parquet file: {file_path}")
                print("-" * 50)

                print(f"Shape: {data.shape}")
                print(f"Columns ({len(data.columns)}):")
                
                # Display columns in a nice format, 4 per line
                cols = list(data.columns)
                for i in range(0, len(cols), 4):
                    row_cols = cols[i:i+4]
                    print("  " + " | ".join(f"{j+i+1:2d}. {col:<25}" for j, col in enumerate(row_cols)))
                
                print(f"\nFirst {num_rows} rows:")
                
                # For wide tables, show a transposed view for better readability
                if len(data.columns) > 10:
                    print("(Showing transposed view for better readability)")
                    sample_data = data.head(num_rows)
                    for i, (idx, row) in enumerate(sample_data.iterrows()):
                        print(f"\n--- Row {i+1} ---")
                        for col in data.columns:
                            value = row[col]
                            # Truncate long values
                            if pd.isna(value):
                                display_value = "NaN"
                            elif isinstance(value, str) and len(str(value)) > 50:
                                display_value = str(value)[:47] + "..."
                            else:
                                display_value = str(value)
                            print(f"  {col:<35}: {display_value}")
                else:
                    # For narrow tables, use normal display
                    with pd.option_context('display.max_columns', None,
                                         'display.width', None,
                                         'display.max_colwidth', 30):
                        print(data.head(num_rows).to_string())

                # If there's a 'msg' column, show its first value
                if "msg" in data.columns:
                    print(f"\nFirst 'msg' value:")
                    print(data["msg"].iloc[0])

            # Handle Avro files
            elif file_extension == ".avro":
                print(f"Reading Avro file: {file_path}")
                print("-" * 50)

                print(f"Total records: {len(data)}")
                print(f"\nFirst {min(num_rows, len(data))} records:")

                for i, record in enumerate(data[:num_rows]):
                    print(f"Record {i + 1}:")
                    print(record)
                    print()

        except Exception as e:
            print(f"Error reading file: {e}")


def read_and_display_file(file_path: Union[str, Path], num_rows: int = 5) -> None:
    """
    Convenience function to read and display a file.

    Args:
        file_path: Path to the file
        num_rows: Number of rows/records to display (default: 5)
    """
    reader = FileReader()
    reader.display_file_info(file_path, num_rows)


def get_supported_files(directory: Union[str, Path] = ".") -> List[str]:
    """
    Get a list of supported files in a directory.

    Args:
        directory: Directory to search (default: current directory)

    Returns:
        List of supported file paths
    """
    reader = FileReader()
    supported_files = []

    for file in os.listdir(directory):
        file_path = Path(directory) / file
        if file_path.is_file() and reader.is_supported_file(file_path):
            supported_files.append(file)

    return supported_files
