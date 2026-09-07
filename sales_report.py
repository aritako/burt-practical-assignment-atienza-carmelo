import json
import csv
import datetime
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
INPUT_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "reports"

DETAIL_COLUMNS = [
  "date",
  "country",
  "channel",
  "category",
  "shop_name",
  "shop_city",
  "units_sold",
  "revenue",
  "transactions",
]

SUMMARY_COLUMNS = [
  "shop_name",
  "shop_city",
  "total_units_sold",
  "total_revenue",
  "total_transactions",
]

def load(file_path: str):
  try:
    with file_path.open("r", encoding="utf-8") as handle:
      payload = json.load(handle)
  except FileNotFoundError as error:
    raise ValueError(f"Input file not found: {file_path}") from error
  except json.JSONDecodeError as error:
    raise ValueError(f"Invalid JSON in input file: {file_path}") from error

  return payload

def validate_records(records, record_type, file_path):
  if not isinstance(records, list):
    raise ValueError(f"Expected {record_type} data in {file_path} to be a list")

  if not all(isinstance(record, dict) for record in records):
    raise ValueError(f"Expected every {record_type} record in {file_path} to be an object")

def validate_stores(stores, file_path):
  validate_records(stores, "store", file_path)
  if not all(store.get("shop_id") for store in stores):
    raise ValueError(f"Every store in {file_path} must have a shop_id")

def clean_revenue(revenue):
  if isinstance(revenue, str):
    revenue = revenue.replace("$", "").replace(",", "")
    try:
      return float(revenue)
    except ValueError:
      return 0.0
  elif isinstance(revenue, (int, float)):
    return float(revenue)
  else:
    return "N/A"

def clean_country(country):
  if not country or not isinstance(country, str):
    return "N/A"
  return country.strip().upper()

def build_transaction_row(transaction, store_map):
  return {
    "date": transaction.get("date", "N/A"),
    "country": clean_country(transaction.get("country", "N/A")),
    "channel": transaction.get("channel", "N/A"),
    "category": transaction.get("category", "N/A"),
    "shop_name": store_map.get(transaction.get("shop_id"), {}).get("name", "N/A"),
    "shop_city": store_map.get(transaction.get("shop_id"), {}).get("city", "N/A"),
    "units_sold": transaction.get("units_sold", 0),
    "revenue": clean_revenue(transaction.get("revenue", 0.0)),
    "transactions": transaction.get("transactions", "N/A"),
  }

def generate_transaction_detail_report(transactions, stores):
  store_map = {store["shop_id"]: store for store in stores}

  normalized_transactions = []

  for transaction in transactions:
    transaction_row = build_transaction_row(transaction, store_map)
    normalized_transactions.append(transaction_row)

  return normalized_transactions

def generate_store_summary_report(transactions, stores):
  store_map = {store["shop_id"]: store for store in stores}
  summary_report = {}

  for transaction in transactions:
    shop_id = transaction.get("shop_id")
    if shop_id not in summary_report:
      summary_report[shop_id] = {
        "shop_name": store_map.get(shop_id, {}).get("name", "N/A"),
        "shop_city": store_map.get(shop_id, {}).get("city", "N/A"),
        "total_units_sold": 0,
        "total_revenue": 0.0,
        "total_transactions": 0,
      }

    units_sold = transaction.get("units_sold", 0)
    if isinstance(units_sold, (int, float)) and not isinstance(units_sold, bool):
      summary_report[shop_id]["total_units_sold"] += units_sold

    revenue = clean_revenue(transaction.get("revenue", 0.0))
    if isinstance(revenue, (int, float)) and not isinstance(revenue, bool):
      summary_report[shop_id]["total_revenue"] += revenue

    transaction_count = transaction.get("transactions", 0)
    if isinstance(transaction_count, (int, float)) and not isinstance(transaction_count, bool):
      summary_report[shop_id]["total_transactions"] += transaction_count

  return list(summary_report.values())

def write_csv_report(output_root, filename, columns, data):
  path = output_root / filename

  with path.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=columns)
    writer.writeheader()
    writer.writerows(data)

def parse_args():
  parser = argparse.ArgumentParser(description="Generate daily sales reports.")
  parser.add_argument(
    "--report-date",
    type=datetime.date.fromisoformat,
    default=datetime.date.today() - datetime.timedelta(days=1),
    help="Date to report in YYYY-MM-DD format (defaults to yesterday).",
  )
  return parser.parse_args()

def main():
  args = parse_args()
  data_root = Path(INPUT_DIR)
  output_root = Path(OUTPUT_DIR)

  output_root.mkdir(parents=True, exist_ok=True)

  raw_transactions = load(data_root / "transactions.json")
  stores = load(data_root / "stores.json")
  validate_records(raw_transactions, "transaction", data_root / "transactions.json")
  validate_stores(stores, data_root / "stores.json")
  report_date = args.report_date.isoformat()
  transactions = list(filter(lambda txn: txn.get("date") == report_date, raw_transactions))

  if not transactions:
    raise ValueError(f"No transactions found for report date {report_date}")

  detail_report = generate_transaction_detail_report(transactions, stores)
  summary_report = generate_store_summary_report(transactions, stores)
  write_csv_report(output_root, f"{report_date}_transaction_detail_report.csv", DETAIL_COLUMNS, detail_report)
  write_csv_report(output_root, f"{report_date}_summary_report.csv", SUMMARY_COLUMNS, summary_report)


if __name__ == "__main__":
  main()

