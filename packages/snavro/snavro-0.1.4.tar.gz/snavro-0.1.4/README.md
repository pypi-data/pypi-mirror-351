# Snavro

[![CI](https://github.com/SkinnyPigeon/snavro/actions/workflows/ci.yml/badge.svg)](https://github.com/SkinnyPigeon/snavro/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/snavro.svg)](https://badge.fury.io/py/snavro)
[![Python versions](https://img.shields.io/pypi/pyversions/snavro.svg)](https://pypi.org/project/snavro/)

A unified file reader for Parquet and Avro files with automatic format detection.

## Features

- 🚀 **Automatic format detection** - Just point to a file and Snavro figures out the format
- 📊 **Multiple format support** - Handles `.parquet`, `.parquet.snappy`, and `.avro` files
- 🖥️ **CLI and Python API** - Use from command line or import in your Python code
- 📈 **Smart data preview** - Shows file info, shape, columns, and sample data
- 🔧 **Type hints** - Full type annotation support for better IDE experience

## Supported Formats

- **Parquet files** (`.parquet`)
- **Snappy-compressed Parquet files** (`.parquet.snappy`)
- **Avro files** (`.avro`)

## Installation

### From PyPI (when published)

```bash
pip install snavro
```

### From source

```bash
git clone https://github.com/yourusername/snavro.git
cd snavro
pip install -e .
```

## Usage

### Command Line Interface

#### Interactive mode
```bash
snavro
```

This will show you all supported files in the current directory and let you choose which one to examine.

#### Direct file access
```bash
# Show first 5 rows (default)
snavro myfile.parquet

# Show first 10 rows
snavro myfile.avro 10

# Works with snappy-compressed files too
snavro data.parquet.snappy 3
```

### Python API

#### Basic usage

```python
import snavro

# Simple function to read and display file info
snavro.read_and_display_file("myfile.parquet", num_rows=5)
```

#### Using the FileReader class

```python
from snavro import FileReader

reader = FileReader()

# Check if a file is supported
if reader.is_supported_file("myfile.parquet"):
    # Read the file (returns pandas DataFrame for Parquet, list of dicts for Avro)
    data = reader.read_file("myfile.parquet")
    
    # Or display file info with preview
    reader.display_file_info("myfile.parquet", num_rows=10)
```

#### Working with the data

```python
from snavro import FileReader

reader = FileReader()

# For Parquet files - returns pandas DataFrame
df = reader.read_parquet("data.parquet")
print(f"Shape: {df.shape}")
print(df.head())

# For Avro files - returns list of dictionaries
records = reader.read_avro("data.avro")
print(f"Number of records: {len(records)}")
print(records[0])  # First record
```

#### Utility functions

```python
from snavro import get_supported_files

# Get all supported files in current directory
files = get_supported_files()
print(files)

# Get supported files in specific directory
files = get_supported_files("/path/to/data")
```

## Example Output

### Parquet File
```
Reading Parquet file: sales_data.parquet
--------------------------------------------------
Shape: (1000, 5)
Columns: ['date', 'product', 'sales', 'region', 'msg']

First few rows:
        date product  sales region                    msg
0 2023-01-01   Widget    100   North  {"status": "active"}
1 2023-01-02   Gadget    150   South  {"status": "pending"}
2 2023-01-03   Widget     75    East  {"status": "active"}

First 'msg' value:
{"status": "active"}
```

### Avro File
```
Reading Avro file: events.avro
--------------------------------------------------
Total records: 500

First 3 records:
Record 1:
{'timestamp': '2023-01-01T10:00:00Z', 'event': 'login', 'user_id': 12345}

Record 2:
{'timestamp': '2023-01-01T10:05:00Z', 'event': 'page_view', 'user_id': 12345}

Record 3:
{'timestamp': '2023-01-01T10:10:00Z', 'event': 'logout', 'user_id': 12345}
```

## Development

### Setup development environment

```bash
git clone https://github.com/yourusername/snavro.git
cd snavro
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Code formatting

```bash
black snavro/
```

### Type checking

```bash
mypy snavro/
```

## Dependencies

- **pandas** >= 2.0.0 - For Parquet file handling
- **pyarrow** >= 10.0.0 - Parquet engine with compression support
- **fastavro** >= 1.8.0 - Fast Avro file reading

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
git clone https://github.com/SkinnyPigeon/snavro.git
cd snavro
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
black snavro/ tests/
flake8 snavro/ tests/
mypy snavro/
```

### Releases

This project uses automated releases via GitHub Actions. See [RELEASE.md](RELEASE.md) for details.

## Changelog

### 0.1.0
- Initial release
- Support for Parquet and Avro files
- CLI and Python API
- Automatic format detection 