"""
Tests for the snavro.reader module.
"""

import pytest
import tempfile
from pathlib import Path

from snavro.reader import FileReader, get_supported_files


class TestFileReader:
    """Test cases for the FileReader class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.reader = FileReader()

    def test_is_supported_file_parquet(self):
        """Test that .parquet files are recognized as supported."""
        assert self.reader.is_supported_file("test.parquet")
        assert self.reader.is_supported_file("data/test.parquet")
        assert self.reader.is_supported_file(Path("test.parquet"))

    def test_is_supported_file_parquet_snappy(self):
        """Test that .parquet.snappy files are recognized as supported."""
        assert self.reader.is_supported_file("test.parquet.snappy")
        assert self.reader.is_supported_file("data/test.parquet.snappy")
        assert self.reader.is_supported_file(Path("test.parquet.snappy"))

    def test_is_supported_file_avro(self):
        """Test that .avro files are recognized as supported."""
        assert self.reader.is_supported_file("test.avro")
        assert self.reader.is_supported_file("data/test.avro")
        assert self.reader.is_supported_file(Path("test.avro"))

    def test_is_supported_file_unsupported(self):
        """Test that unsupported file types are not recognized."""
        assert not self.reader.is_supported_file("test.csv")
        assert not self.reader.is_supported_file("test.json")
        assert not self.reader.is_supported_file("test.txt")
        assert not self.reader.is_supported_file("test.xlsx")

    def test_read_nonexistent_file(self):
        """Test that reading a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            self.reader.read_parquet("nonexistent.parquet")

        with pytest.raises(FileNotFoundError):
            self.reader.read_avro("nonexistent.avro")

    def test_read_file_unsupported_format(self):
        """Test that reading an unsupported file format raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported file format"):
            self.reader.read_file("test.csv")


class TestUtilityFunctions:
    """Test cases for utility functions."""

    def test_get_supported_files_empty_directory(self):
        """Test get_supported_files with an empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            files = get_supported_files(temp_dir)
            assert files == []

    def test_get_supported_files_with_supported_files(self):
        """Test get_supported_files with a directory containing supported files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            test_files = [
                "test1.parquet",
                "test2.avro",
                "test3.parquet.snappy",
                "test4.csv",  # unsupported
                "test5.json",  # unsupported
            ]

            for file in test_files:
                Path(temp_dir, file).touch()

            supported_files = get_supported_files(temp_dir)

            # Should only include the supported files
            expected = ["test1.parquet", "test2.avro", "test3.parquet.snappy"]
            assert set(supported_files) == set(expected)
            assert len(supported_files) == 3


if __name__ == "__main__":
    pytest.main([__file__])
