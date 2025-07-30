import argparse
import pandas as pd
from datasets import load_dataset, Dataset
from .google_auth import connect_gsheet, get_sheets_service
from tqdm import tqdm
import time
from huggingface_hub import HfApi, DatasetCard
import os
import sqlite3

# Google Sheets has a limit of 10 million cells per spreadsheet
GOOGLE_SHEETS_CELL_LIMIT = 10_000_000
# Google Sheets API has a limit of 500 requests per 100 seconds per project
GOOGLE_SHEETS_REQUESTS_PER_MINUTE = 300
# We'll use a batch size that allows us to stay within rate limits
# while also making progress on large datasets
BATCH_SIZE = 1000


def connect(service):
    if service == "gsheet":
        connect_gsheet()
        print(f"Successfully connected to Google Sheets. Credentials stored.")
    else:
        raise ValueError(f"Unsupported service: {service}")


def export_dataset(
    dataset_name,
    split=None,
    output_file=None,
    subset=None,
    export_format="csv",
    spreadsheet_id=None,
    sheetname=None,
    table_name=None,
):
    if not output_file:
        base_output_file = dataset_name.replace("/", "_")
    else:
        base_output_file = output_file

    try:
        # Load the dataset
        if subset:
            dataset = load_dataset(dataset_name, subset)
        else:
            dataset = load_dataset(dataset_name)

        # Determine splits to be saved
        splits_to_save = [split] if split else dataset.keys()

        for split_key in splits_to_save:
            # Convert to pandas DataFrame
            df = pd.DataFrame(dataset[split_key])

            subset_part = ""
            split_part = f"_{split_key}"
            base_output_file = base_output_file.rsplit(".", 1)[
                0
            ]  # Remove extension if present
            output_filename = (
                f"{base_output_file}{subset_part}{split_part}.{export_format}"
            )

            # Determine the output filename or use Google names
            if export_format == "gsheet":
                export_to_gsheet(
                    df,
                    dataset_name,
                    split_key=split_key,
                    spreadsheet_id=spreadsheet_id,
                    sheetname=sheetname,
                )
            elif export_format == "csv":
                df.to_csv(output_filename, index=False)
            elif export_format == "json":
                df.to_json(output_filename, orient="records", lines=False)
            elif export_format == "jsonl":
                df.to_json(output_filename, orient="records", lines=True)
            elif export_format == "tsv":
                df.to_csv(output_filename, index=False, sep="\t")
            elif export_format == "xlsx":
                df.to_excel(output_filename, index=False, engine="openpyxl")
            elif export_format == "parquet":
                df.to_parquet(output_filename, index=False)
            elif export_format == "sqlite":
                conn = sqlite3.connect(output_filename)
                table = table_name if table_name else f"{dataset_name}_{split_key}"
                df.to_sql(table, conn, if_exists="replace", index=False)
                conn.close()

            print(
                f"Dataset '{dataset_name}' (split: '{split_key}') saved to '{output_filename}' successfully."
            )

    except Exception as e:
        print(f"An error occurred: {e}")


def export_to_gsheet(df, dataset_name, split_key, spreadsheet_id=None, sheetname=None):
    service = get_sheets_service()

    # Create a new spreadsheet if no spreadsheet_id is provided
    if not spreadsheet_id:
        spreadsheet = (
            service.spreadsheets()
            .create(
                body={
                    "properties": {"title": f"{dataset_name}"},
                    "sheets": [
                        {"properties": {"title": sheetname if sheetname else "Sheet1"}}
                    ],
                }
            )
            .execute()
        )
        spreadsheet_id = spreadsheet["spreadsheetId"]
        print(f"Created new Google Sheet with ID: {spreadsheet_id}")

    spreadsheet_metadata = (
        service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    )

    # If no sheet is specified, use the first sheet
    sheets = spreadsheet_metadata["sheets"]

    # Check if sheet with sheetname exists, if not create it
    sheet_exists = any(sheet["properties"]["title"] == sheetname for sheet in sheets)
    if not sheet_exists:
        request_body = {
            "requests": [{"addSheet": {"properties": {"title": sheetname}}}]
        }
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=request_body
        ).execute()
        print(f"Created new sheet '{sheetname}' in the spreadsheet.")
        # Refresh the spreadsheet metadata
        spreadsheet_metadata = (
            service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        )
        sheets = spreadsheet_metadata["sheets"]

    if not sheetname:
        sheetname = sheets[0]["properties"]["title"]

    for sheet in sheets:
        if sheet["properties"]["title"] == sheetname:
            sheet = sheet["properties"]["sheetId"]

            if not sheet:
                raise (
                    f"Sheet with name {sheetname} not found in the spreadsheet {spreadsheet_id}."
                )

    # Clear the existing content
    range_name = f"{sheetname}!A1:ZZ"
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id, range=range_name
    ).execute()

    # Prepare the data
    headers = df.columns.tolist()
    values = [headers] + df.values.tolist()

    # Check if the dataset exceeds Google Sheets cell limit
    total_cells = len(values) * len(headers)
    if total_cells > GOOGLE_SHEETS_CELL_LIMIT:
        raise ValueError(
            f"Dataset too large for Google Sheets. Total cells: {total_cells}, Limit: {GOOGLE_SHEETS_CELL_LIMIT}"
        )

    print(f"Total cells {total_cells}")
    print(f"Sheet {sheet}")

    if isinstance(sheet, dict):
        sheet = sheet["properties"]["sheetId"]

    service.spreadsheets().batchUpdate(
        body={
            "requests": [
                {
                    "appendDimension": {
                        "sheetId": sheet,
                        "dimension": "ROWS",
                        "length": len(values) + 1,
                    }
                }
            ]
        },
        spreadsheetId=spreadsheet_id,
    ).execute()

    # Batch update the sheet
    total_rows = len(values)
    with tqdm(total=total_rows, desc="Exporting to Google Sheets", unit="rows") as pbar:
        for i in range(0, total_rows, BATCH_SIZE):
            end = min(i + BATCH_SIZE, total_rows)
            batch = values[i:end]
            body = {"values": batch}
            range_name = f"{sheetname}!A{i+1}:ZZ{end}"

            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body,
            ).execute()

            pbar.update(len(batch))

            # Respect rate limits
            time.sleep(60 / GOOGLE_SHEETS_REQUESTS_PER_MINUTE)

    return spreadsheet_id, sheetname


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
    split=None,
):
    try:
        # Read the input file based on the format
        if format == "csv":
            df = pd.read_csv(input_file)
        elif format == "tsv":
            df = pd.read_csv(input_file, sep="\t")
        elif format == "json":
            df = pd.read_json(input_file)
        elif format == "parquet":
            df = pd.read_parquet(input_file, engine="pyarrow")
        elif format == "jsonl":
            df = pd.read_json(input_file, lines=True)
        elif format == "xlsx":
            df = pd.read_excel(input_file, engine="openpyxl")
        elif format == "gsheet":
            if not spreadsheet_id:
                raise ValueError("spreadsheet_id is required for gsheet format")
            df = read_from_gsheet(spreadsheet_id, sheetname)
        elif format == "sqlite":
            conn = sqlite3.connect(input_file)
            table = table_name if table_name else dataset_name
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            conn.close()
        else:
            raise ValueError(f"Unsupported format: {format}")

        # Filter columns if specified
        if columns:
            print(f"Columns specified: {columns}")
            column_list = [col.strip() for col in columns.split(",")]
            available_columns = set(df.columns)
            valid_columns = [col for col in column_list if col in available_columns]
            if len(valid_columns) != len(column_list):
                missing_columns = set(column_list) - set(valid_columns)
                print(
                    f"Warning: The following columns were not found in the data: {', '.join(missing_columns)}"
                )
            df = df[valid_columns]

        print(f"DataFrame shape after column filtering: {df.shape}")
        print(f"Final columns: {df.columns.tolist()}")

        # Convert DataFrame to Dataset
        dataset = Dataset.from_pandas(df)

        # Push to Hugging Face
        if subset:
            dataset.push_to_hub(dataset_name, subset, private=private, split=split)
        else:
            dataset.push_to_hub(dataset_name, private=private, split=split)

        print(f"Dataset '{dataset_name}' successfully pushed to Hugging Face.")

        # # Create and push dataset card
        # card = DatasetCard(
        #     dataset_summary=f"Dataset imported using datapluck from a {format} source.",
        # )
        # card.push_to_hub(dataset_name)

    except Exception as e:
        print(f"An error occurred: {e}")
        raise


def read_from_gsheet(spreadsheet_id, sheetname=None):
    service = get_sheets_service()

    if not sheetname:
        sheet_metadata = (
            service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        )
        sheetname = sheet_metadata["sheets"][0]["properties"]["title"]

    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=f"{sheetname}")
        .execute()
    )

    values = result.get("values", [])
    if not values:
        raise ValueError("No data found in the Google Sheet.")

    headers = values[0]
    data = values[1:]

    print(f"Raw headers: {headers}")
    print(f"Number of raw headers: {len(headers)}")
    print(f"Number of data rows: {len(data)}")
    if data:
        print(f"Number of columns in first data row: {len(data[0])}")

    # Remove empty columns
    non_empty_cols = [i for i, col in enumerate(headers) if col.strip()]
    headers = [headers[i] for i in non_empty_cols]
    data = [[row[i] for i in non_empty_cols if i < len(row)] for row in data]

    print(f"Cleaned headers: {headers}")
    print(f"Number of cleaned headers: {len(headers)}")
    if data:
        print(f"Number of columns in first cleaned data row: {len(data[0])}")

    # Ensure all data rows have the same number of columns as headers
    max_cols = len(headers)
    data = [row + [""] * (max_cols - len(row)) for row in data]

    df = pd.DataFrame(data, columns=headers)

    print(f"DataFrame columns: {df.columns.tolist()}")
    print(f"DataFrame shape: {df.shape}")

    return df


def main():
    parser = argparse.ArgumentParser(
        description="Datapluck: Connect to services, export and import Hugging Face datasets"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Connect command
    connect_parser = subparsers.add_parser("connect", help="Connect to a service")
    connect_parser.add_argument(
        "service", choices=["gsheet"], help="Service to connect to"
    )

    # Export command
    export_parser = subparsers.add_parser("export", help="Export a dataset")
    export_parser.add_argument(
        "dataset_name", type=str, help="The name of the dataset to export"
    )
    export_parser.add_argument(
        "--split", type=str, default=None, help="The dataset split to export"
    )
    export_parser.add_argument(
        "--output_file",
        type=str,
        default=None,
        help="The base name for the output file (defaults to the escaped dataset name with the proper extension)",
    )
    export_parser.add_argument(
        "--subset",
        type=str,
        default=None,
        help="The subset of the dataset to export (if applicable)",
    )
    export_parser.add_argument(
        "--format",
        type=str,
        default="csv",
        choices=["csv", "tsv", "json", "jsonl", "xlsx", "parquet", "gsheet", "sqlite"],
        help="The file format for the export",
    )
    export_parser.add_argument(
        "--spreadsheet_id",
        type=str,
        help="The ID of the Google Sheet to export to (required for gsheet format)",
    )
    export_parser.add_argument(
        "--sheetname",
        type=str,
        help="The name of the sheet in the Google Sheet (optional)",
    )
    export_parser.add_argument(
        "--table_name",
        type=str,
        help="The name of the table for SQLite export (optional)",
    )

    # Import command
    import_parser = subparsers.add_parser(
        "import", help="Import a dataset to Hugging Face"
    )
    import_parser.add_argument(
        "dataset_name", type=str, help="The name of the dataset on Hugging Face"
    )
    import_parser.add_argument(
        "--input_file", type=str, help="The input file to import"
    )
    import_parser.add_argument(
        "--private",
        action="store_true",
        help="Make the dataset private on Hugging Face",
    )
    import_parser.add_argument(
        "--format",
        type=str,
        default="csv",
        choices=["csv", "tsv", "json", "jsonl", "xlsx", "parquet", "gsheet", "sqlite"],
        help="The file format of the input",
    )
    import_parser.add_argument(
        "--spreadsheet_id",
        type=str,
        help="The ID of the Google Sheet to import from (required for gsheet format)",
    )
    import_parser.add_argument(
        "--sheetname",
        type=str,
        help="The name of the sheet in the Google Sheet (optional)",
    )
    import_parser.add_argument(
        "--columns",
        type=str,
        help="Comma-separated list of columns to include in the dataset",
    )
    import_parser.add_argument(
        "--table_name",
        type=str,
        help="The name of the table for SQLite import (optional)",
    )
    import_parser.add_argument(
        "--subset",
        type=str,
        default=None,
        help="The subset of the dataset to import (if applicable)",
    )
    import_parser.add_argument(
        "--split",
        type=str,
        default=None,
        help="The split of the dataset to import (if applicable)",
    )

    args = parser.parse_args()

    if args.command == "connect":
        connect(args.service)
    elif args.command == "export":
        export_dataset(
            dataset_name=args.dataset_name,
            split=args.split,
            output_file=args.output_file,
            subset=args.subset,
            export_format=args.format,
            spreadsheet_id=args.spreadsheet_id,
            sheetname=args.sheetname,
            table_name=args.table_name,
        )
    elif args.command == "import":
        import_dataset(
            input_file=args.input_file,
            dataset_name=args.dataset_name,
            private=args.private,
            format=args.format,
            spreadsheet_id=args.spreadsheet_id,
            sheetname=args.sheetname,
            columns=args.columns,
            table_name=args.table_name,
            subset=args.subset,
            split=args.split,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
