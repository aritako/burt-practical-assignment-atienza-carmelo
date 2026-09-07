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

def join_by_stores(transactions, stores):
  store_map = {store["shop_id"]: store for store in stores}

  for transaction in transactions:
    shop_id = transaction["shop_id"]
    store = store_map.get(shop_id, {})
    transaction["shop_name"] = store.get("name", "")
    transaction["shop_city"] = store.get("city", "")
    transaction.pop("shop_id", None)

  return transactions

def generate_transaction_detail_report(transactions, stores):
  joined_transactions = join_by_stores(transactions, stores)
  print(joined_transactions[:5])

def main():
  data_root = Path(INPUT_DIR)
  output_root = Path(OUTPUT_DIR)

  output_root.mkdir(parents=True, exist_ok=True)

  transactions = load(data_root / "transactions.json")
  stores = load(data_root / "stores.json")

  generate_transaction_detail_report(transactions, stores)

if __name__ == "__main__":
  main()

