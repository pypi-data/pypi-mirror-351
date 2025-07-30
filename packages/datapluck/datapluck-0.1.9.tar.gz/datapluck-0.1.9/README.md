# datapluck

<img src="logo.png" alt="Datapluck Logo" width="100"/>

<br />

`datapluck` is a command-line tool and Python library for exporting datasets from the Hugging Face Hub to various file formats and importing datasets back to the Hugging Face Hub. Supported formats include CSV, TSV, JSON, JSON Lines (jsonl), Microsoft Excel's XLSX, Parquet, SQLite, and Google Sheets.

Visit the project website [datapluck.org](https://datapluck.org) for more information and check out the [Visual Generator](https://datapluck.org/generator) to easily create your own datapluck recipes.

## Features

- Export datasets from the Hugging Face Hub
- Import datasets to the Hugging Face Hub
- Support multiple output formats: CSV, TSV, JSON, JSON Lines (jsonl), Microsoft Excel's XLSX, Parquet, SQLite, and Google Sheets
- Handle different dataset splits and subsets
- Connect to Google Sheets for import/export operations
- Filter columns during import
- Support for private datasets on Hugging Face

## Purposes

- Preview a dataset in the format of your choice
- Annotate a dataset in the editor of your choice (export, annotate, then import back)
- Simplify dataset management from the CLI and in CI/CD contexts
- Backup datasets as a one-off or on the regular

### Quick Example

#### Export a dataset to csv
```bash
datapluck export team/dataset --format csv --output_file data.csv`
```

#### Import data to your account
```bash
datapluck import username/new-or-existing-dataset --input_file data.csv --format csv --private
```


## Authentication

Before using `datapluck`, ensure you are logged in to the Hugging Face Hub. This is required for authentication when accessing private datasets or updating yours. You can log in using the Hugging Face CLI:

```bash
huggingface-cli login
```

This will prompt you to enter your Hugging Face access token. Once logged in, `datapluck` will use your credentials for operations that require authentication.


## Installation

Install `datapluck` from PyPI:

```bash
pip install datapluck
```

## Usage

### Command-line Interface

1. Connect to Google Sheets (required for Google Sheets operations):

```bash
datapluck connect gsheet
```

2. Export a dataset:

```bash
# Export the entire 'imdb' dataset as CSV
datapluck export imdb --format csv --output_file imdb.csv

# Export the entire 'imdb' dataset as a Microsoft Excel spreadsheet (XLSX)
datapluck export imdb --format xlsx --output_file imdb.xlsx

# Export a specific split of the 'imdb' dataset as JSON 
# (not recommended for large datasets, use jsonl instead)
datapluck export imdb --split test --format json --output_file imdb.json 

# Export to Google Sheets
datapluck export imdb --format gsheet --spreadsheet_id YOUR_SPREADSHEET_ID --sheetname Sheet1

# Export to SQLite
datapluck export imdb --format sqlite --table_name imdb_data --output_file imdb.sqlite 
```

3. Import a dataset:

```bash
# Import a CSV file to Hugging Face
datapluck import my_dataset --input_file data.csv --format csv

# Import from Google Sheets
datapluck import my_dataset --format gsheet --spreadsheet_id YOUR_SPREADSHEET_ID --sheetname Sheet1

# Import specific columns from a JSON file
datapluck import my_dataset --input_file data.json --format json --columns "col1,col2,col3"

# Import as a private dataset with a specific split
datapluck import my_dataset --input_file data.parquet --format parquet --private --split train
```

#### Commands

```
connect: Connect to a service (currently only supports Google Sheets).

export: Export a dataset from Hugging Face to a specified format.

import: Import a dataset from a file to Hugging Face.
```

#### Arguments

Common arguments:
```
dataset_name: The name of the dataset to export or import.
--format: The file format for export or import (default: csv).
          Choices: csv, tsv, json, jsonl, parquet, gsheet, sqlite.

--spreadsheet_id: The ID of the Google Sheet to export to or import from (used by gsheet format). If you are exporting from Huggingface to Google Sheet, you can omit this argument and a spreadsheet will automatically be created for you.

--sheetname: The name of the sheet in the Google Sheet (optional).

--subset: The subset of the dataset to export or import (if applicable).

--split: The dataset split to export or import (optional).
```

Export-specific arguments:
```
--output_file: The base name for the output file(s).

--table_name: The name of the table for SQLite export (optional).
```

Import-specific arguments:
```
--input_file: The input file to import.

--private: Make the dataset private on Hugging Face.

--columns: Comma-separated list of columns to include in the dataset.

--table_name: The name of the table for SQLite import (optional).
```

### Python Package

You can use `datapluck` as a Python package:

```python

from datapluck import export_dataset, import_dataset
# Export a dataset

export_dataset(
    dataset_name='imdb',
    split='train',
    output_file='imdb_train',
    export_format='csv'
)

# Import a dataset
import_dataset(
    input_file='data.csv',
    dataset_name='my_dataset',
    private=True,
    format='csv',
    columns='col1,col2,col3',
    split='test'
)
```

#### `export_dataset` function

```python
def export_dataset(
    dataset_name,
    split=None,
    output_file=None,
    subset=None,
    export_format="csv",
    spreadsheet_id=None,
    sheetname=None,
    table_name=None
):
"""
Export a dataset from Hugging Face Hub.

Args:
dataset_name (str): Name of the dataset on Hugging Face Hub.

split (str, optional): Dataset split to export.

output_file (str, optional): Base name for the output file(s).

subset (str, optional): Subset of the dataset to export.

export_format (str, optional): File format for export (default: "csv").

spreadsheet_id (str, optional): ID of the Google Sheet for export.

sheetname (str, optional): Name of the sheet in Google Sheet.

table_name (str, optional): Name of the table for SQLite export.
"""
```

#### `import_dataset` function

```python
def import_dataset(
    input_file,
    dataset_name,
    private=False,
    format="csv",
    spreadsheet_id=None,
    sheetname=None,
    columns=None,
    table_name=None,
    subset=None,
    split=None
):
"""
Import a dataset to Hugging Face Hub.

Args:
input_file (str): Path to the input file.

dataset_name (str): Name for the dataset on Hugging Face Hub.

private (bool, optional): Make the dataset private (default: False).
format (str, optional): File format of the input (default: "csv").

spreadsheet_id (str, optional): ID of the Google Sheet for import.

sheetname (str, optional): Name of the sheet in Google Sheet.

columns (str, optional): Comma-separated list of columns to include.

table_name (str, optional): Name of the table for SQLite import.

subset (str, optional): Subset name for the imported dataset.

split (str, optional): Split name for the imported dataset.
"""

```

## Contributing

Contributions will be welcome once `datapluck` reaches v1 feature-completeness from the author's standpoint.

## Website

Visit us at [datapluck.org](https://datapluck.org) for more informations and check out the [Visual Generator](https://datapluck.org/generator) to easily create your own datapluck recipes.

## License

This project's license is currently TBD. In its current version, it can be run without limitations for all lawful purposes, but distribution is restricted via the current PyPI package only.

## Authors

- Omar Kamali - Initial work (omar at datapluck.org)
