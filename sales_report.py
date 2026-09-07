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

  print(f"Loaded {len(payload)} records from {file_path}")
  return payload

def main():
  data_root = Path(INPUT_DIR)
  output_root = Path(OUTPUT_DIR)

  transactions = load(data_root / "transactions.json")
  stores = load(data_root / "stores.json")

if __name__ == "__main__":
  main()

