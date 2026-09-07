import json
import csv
import datetime
import argparse
from pathlib import Path

INPUT_DIR = "data"
OUTPUT_DIR = "reports"

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
  with file_path.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

  return payload

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
    return 0.0

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

    summary_report[shop_id]["total_units_sold"] += transaction.get("units_sold", 0)
    summary_report[shop_id]["total_revenue"] += clean_revenue(transaction.get("revenue", 0.0))
    summary_report[shop_id]["total_transactions"] += transaction.get("transactions", 0)

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
  report_date = args.report_date.isoformat()
  transactions = list(filter(lambda txn: txn.get("date") == report_date, raw_transactions))

  detail_report = generate_transaction_detail_report(transactions, stores)
  summary_report = generate_store_summary_report(transactions, stores)
  write_csv_report(output_root, f"{report_date}_transaction_detail_report.csv", DETAIL_COLUMNS, detail_report)
  write_csv_report(output_root, f"{report_date}_summary_report.csv", SUMMARY_COLUMNS, summary_report)


if __name__ == "__main__":
  main()

