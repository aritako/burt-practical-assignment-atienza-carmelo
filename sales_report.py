import json
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

def build_transaction_row(transaction, store_map):
  return {
    "date": transaction.get("date", ""),
    "country": transaction.get("country", ""),
    "channel": transaction.get("channel", ""),
    "category": transaction.get("category", ""),
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

def main():
  data_root = Path(INPUT_DIR)
  output_root = Path(OUTPUT_DIR)

  output_root.mkdir(parents=True, exist_ok=True)

  transactions = load(data_root / "transactions.json")
  stores = load(data_root / "stores.json")

  detail_report = generate_transaction_detail_report(transactions, stores)


if __name__ == "__main__":
  main()

