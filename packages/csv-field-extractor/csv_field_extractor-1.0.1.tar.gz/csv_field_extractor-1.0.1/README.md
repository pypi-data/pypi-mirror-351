# CSV Field Extractor

![GitHub release](https://img.shields.io/github/v/release/hackjustin/csv-field-extractor)
![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![GitHub issues](https://img.shields.io/github/issues/hackjustin/csv-field-extractor)
![GitHub stars](https://img.shields.io/github/stars/hackjustin/csv-field-extractor)
![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-blue)
![Dependencies](https://img.shields.io/badge/dependencies-pandas-green)

A simple Python utility to extract specific fields/columns from CSV files.

## Features

- Extract any field by name from a CSV file
- Optional alphabetical sorting of results
- Automatic filtering of empty/null values
- Field validation with helpful error messages
- Clean, stripped values (removes whitespace)

## Requirements

- Python 3.x
- pandas library

Install pandas if you don't have it:
```bash
pip install pandas
```

## Usage

### Command Line Interface (Recommended for local use)

```bash
# Basic usage - extract and print field values line by line
python csv_field_extractor.py Results.csv Symbol

# Sort alphabetically
python csv_field_extractor.py Results.csv Symbol --sort

# Different output formats
python csv_field_extractor.py Results.csv Symbol --sort --output comma
python csv_field_extractor.py Results.csv Description --output space

# Get help
python csv_field_extractor.py --help
```

### As a Python Library

```python
from csv_field_extractor import extract_field_from_csv

# Extract symbols from a CSV file
symbols = extract_field_from_csv('Results.csv', 'Symbol')
print(symbols)
```

### Library Usage Examples

```python
# Extract and sort alphabetically
symbols = extract_field_from_csv('Results.csv', 'Symbol', sort_alphabetically=True)
for symbol in symbols:
    print(symbol)
```

```python
# Extract descriptions
descriptions = extract_field_from_csv('Results.csv', 'Description')

# Extract expense ratios
expense_ratios = extract_field_from_csv('Results.csv', 'Net Expense Ratio')

# Extract any field
morningstar_ratings = extract_field_from_csv('Results.csv', 'Morningstar Overall')
```

## Command Line Options

- `csv_file`: Path to your CSV file (required)
- `field_name`: Name of the column/field to extract (required)  
- `--sort, -s`: Sort results alphabetically
- `--output, -o`: Output format - `lines` (default), `comma`, or `space`

## Examples

```bash
# Extract symbols, sorted, comma-separated (perfect for copy-paste)
python csv_field_extractor.py Results.csv Symbol --sort --output comma

# Extract descriptions as separate lines
python csv_field_extractor.py Results.csv Description

# Quick field validation (see available fields if you mistype)
python csv_field_extractor.py Results.csv WrongFieldName
```

## Function Parameters

- **csv_file_path** (str): Path to your CSV file
- **field_name** (str): Name of the column/field to extract
- **sort_alphabetically** (bool, optional): Sort results alphabetically (default: False)

## Return Value

Returns a list of strings containing the field values, with empty/null values filtered out.

## Error Handling

If the specified field name doesn't exist in the CSV, the function will raise a `ValueError` with a list of available field names to help you identify the correct field name.

## Example Output

```python
symbols = extract_field_from_csv('Results.csv', 'Symbol', sort_alphabetically=True)
# Returns: ['ARKF', 'ARKG', 'ARKK', 'ARKQ', 'ARKW', 'ARKX', 'IZRL', 'PRNT']
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/csv-field-extractor.git
cd csv-field-extractor

# Create virtual environment and install dependencies
make setup

# Or manually:
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running Tests

```bash
# Run tests using make
make test

# Or run directly
python -m unittest test_csv_field_extractor.py -v

# Run specific test class
python -m unittest test_csv_field_extractor.TestCSVFieldExtractor -v
```

### Installing as Package

```bash
# Install in development mode (changes reflected immediately)
pip install -e .

# Now you can use the command anywhere
csv-extract /path/to/data.csv Symbol --sort
```

### Other Make Commands

```bash
make setup    # Set up virtual environment
make test     # Run tests
make clean    # Remove build artifacts and cache files
make lint     # Check code style (requires: pip install flake8)
make build    # Build distribution packages
make help     # Show all available commands
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Make your changes and add tests
4. Run tests (`make test`)
5. Commit your changes (`git commit -am 'Add feature'`)
6. Push to the branch (`git push origin feature-name`)
7. Create a Pull Request