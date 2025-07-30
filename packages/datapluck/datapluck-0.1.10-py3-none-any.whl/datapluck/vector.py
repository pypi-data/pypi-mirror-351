import argparse
import numpy as np
from google_auth import get_sheets_service
from sentence_transformers import SentenceTransformer
import os.path
import ast
import time
from tqdm import tqdm

# Google Sheets has a limit of 10 million cells per spreadsheet
GOOGLE_SHEETS_CELL_LIMIT = 10_000_000
# Google Sheets API has a limit of 500 requests per 100 seconds per project
GOOGLE_SHEETS_REQUESTS_PER_MINUTE = 60
# We'll use a batch size that allows us to stay within rate limits
# while also making progress on large datasets
BATCH_SIZE = 100


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def batch_update(service, spreadsheet_id, range_name, values):
    request = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            body={"values": values},
        )
    )
    return request.execute()


def rate_limited_batch_update(service, spreadsheet_id, range_name, values):
    batches = [values[i : i + BATCH_SIZE] for i in range(0, len(values), BATCH_SIZE)]
    for i, batch in enumerate(batches):
        start_time = time.time()
        batch_update(service, spreadsheet_id, f"{range_name}{i*BATCH_SIZE+1}", batch)
        elapsed_time = time.time() - start_time
        if elapsed_time < 60 / GOOGLE_SHEETS_REQUESTS_PER_MINUTE:
            time.sleep((60 / GOOGLE_SHEETS_REQUESTS_PER_MINUTE) - elapsed_time)
        print(f"Processed batch {i+1}/{len(batches)}")


def embed_command(args):
    model = SentenceTransformer(args.model)
    service = get_sheets_service()
    sheet = service.spreadsheets()

    # Get total number of rows
    result = (
        sheet.values()
        .get(
            spreadsheetId=args.spreadsheet_id,
            range=f"{args.sheetname}!{args.source}:{args.source}",
        )
        .execute()
    )
    values = result.get("values", [])
    total_rows = len(values)

    for start_row in tqdm(range(1, total_rows + 1, BATCH_SIZE)):
        end_row = min(start_row + BATCH_SIZE - 1, total_rows)
        batch_range = (
            f"{args.sheetname}!{args.source}{start_row}:{args.source}{end_row}"
        )

        result = (
            sheet.values()
            .get(spreadsheetId=args.spreadsheet_id, range=batch_range)
            .execute()
        )
        batch_values = result.get("values", [])

        if not batch_values:
            print(f"No data found in range {batch_range}.")
            continue

        # Embed the values
        embeddings = model.encode([row[0] for row in batch_values])

        # Prepare the data for updating the sheet
        update_data = [[str(embedding.tolist())] for embedding in embeddings]

        # Update the sheet with embeddings
        target_range = (
            f"{args.sheetname}!{args.target}{start_row}:{args.target}{end_row}"
        )
        rate_limited_batch_update(
            service, args.spreadsheet_id, target_range, update_data
        )

        print(f"Processed rows {start_row} to {end_row}")

    print(f"All embeddings have been calculated and stored in column {args.target}.")


def cosine_command(args):
    service = get_sheets_service()
    sheet = service.spreadsheets()

    # Get total number of rows
    result = (
        sheet.values()
        .get(
            spreadsheetId=args.spreadsheet_id,
            range=f"{args.sheetname}!{args.v1}:{args.v1}",
        )
        .execute()
    )
    total_rows = len(result.get("values", []))

    for start_row in tqdm(range(1, total_rows + 1, BATCH_SIZE)):
        end_row = min(start_row + BATCH_SIZE - 1, total_rows)
        batch_range1 = f"{args.sheetname}!{args.v1}{start_row}:{args.v1}{end_row}"
        batch_range2 = f"{args.sheetname}!{args.v2}{start_row}:{args.v2}{end_row}"

        result1 = (
            sheet.values()
            .get(spreadsheetId=args.spreadsheet_id, range=batch_range1)
            .execute()
        )
        result2 = (
            sheet.values()
            .get(spreadsheetId=args.spreadsheet_id, range=batch_range2)
            .execute()
        )

        values1 = result1.get("values", [])
        values2 = result2.get("values", [])

        if not values1 or not values2:
            print(
                f"No data found in one or both columns for range {start_row} to {end_row}."
            )
            continue

        # Convert string representations of lists back to numpy arrays
        vectors1 = [np.array(ast.literal_eval(row[0])) for row in values1]
        vectors2 = [np.array(ast.literal_eval(row[0])) for row in values2]

        # Calculate cosine similarities
        similarities = [
            [str(cosine_similarity(v1, v2))] for v1, v2 in zip(vectors1, vectors2)
        ]

        # Update the sheet with similarities
        target_range = (
            f"{args.sheetname}!{args.target}{start_row}:{args.target}{end_row}"
        )
        rate_limited_batch_update(
            service, args.spreadsheet_id, target_range, similarities
        )

        print(f"Processed rows {start_row} to {end_row}")

    print(
        f"All cosine similarities have been calculated and stored in column {args.target}."
    )


def main():
    parser = argparse.ArgumentParser(
        description="Embed text and calculate cosine similarities in Google Sheets."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Embed command
    embed_parser = subparsers.add_parser(
        "embed", help="Embed text from a source column"
    )
    embed_parser.add_argument("--spreadsheet_id", help="Google Sheets spreadsheet ID")
    embed_parser.add_argument("--sheetname", help="Name of the sheet")
    embed_parser.add_argument(
        "--model", help="Path or Hugging Face name of the model to use"
    )
    embed_parser.add_argument("--source", help="Source column containing text to embed")
    embed_parser.add_argument("--target", help="Target column to write the vectors")

    # Cosine command
    cosine_parser = subparsers.add_parser(
        "cosine", help="Calculate cosine similarity between two vector columns"
    )
    cosine_parser.add_argument("--spreadsheet_id", help="Google Sheets spreadsheet ID")
    cosine_parser.add_argument("--sheetname", help="Name of the sheet")
    cosine_parser.add_argument("--v1", help="First vector column")
    cosine_parser.add_argument("--v2", help="Second vector column")
    cosine_parser.add_argument(
        "--target", help="Target column to write the cosine similarities"
    )

    args = parser.parse_args()

    if args.command == "embed":
        embed_command(args)
    elif args.command == "cosine":
        cosine_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
