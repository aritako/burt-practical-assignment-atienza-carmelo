import datetime
import unittest
from pathlib import Path
from unittest.mock import patch

import sales_report


PROJECT_ROOT = Path(__file__).parent
DATA_ROOT = PROJECT_ROOT / "data"


class SalesReportTests(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.transactions = sales_report.load(DATA_ROOT / "transactions.json")
    cls.stores = sales_report.load(DATA_ROOT / "stores.json")

  def test_clean_revenue_supports_currency_formats(self):
    self.assertEqual(sales_report.clean_revenue("$1,234.50"), 1234.5)
    self.assertEqual(sales_report.clean_revenue(12), 12.0)
    self.assertEqual(sales_report.clean_revenue(None), 0.0)
    self.assertEqual(sales_report.clean_revenue("invalid"), 0.0)

  def test_detail_report_preserves_unknown_shop_and_missing_country(self):
    transaction = dict(next(
      transaction
      for transaction in self.transactions
      if transaction.get("shop_id") == "S999"
    ))
    transaction["country"] = ""

    row = sales_report.generate_transaction_detail_report(
      [transaction],
      self.stores,
    )[0]

    self.assertEqual(row["shop_name"], "N/A")
    self.assertEqual(row["shop_city"], "N/A")
    self.assertEqual(row["country"], "N/A")

  def test_summary_report_uses_only_selected_date(self):
    report_date = "2024-03-01"
    transactions = list(filter(lambda txn: txn.get("date") == report_date, self.transactions))

    summary = sales_report.generate_store_summary_report(
      transactions,
      self.stores,
    )

    downtown = next(
      row for row in summary if row["shop_name"] == "Downtown Flagship"
    )
    unknown = next(row for row in summary if row["shop_name"] == "N/A")

    self.assertEqual(downtown["total_units_sold"], 645)
    self.assertEqual(downtown["total_revenue"], 522.0)
    self.assertEqual(downtown["total_transactions"], 337)
    self.assertEqual(unknown["total_units_sold"], 10)

  def test_summary_ignores_missing_transaction_count(self):
    transactions = [
      transaction
      for transaction in self.transactions
      if transaction.get("date") == "2024-03-02"
    ]

    summary = sales_report.generate_store_summary_report(
      transactions,
      self.stores,
    )

    self.assertEqual(summary[0]["total_transactions"], 90)

  @patch("sales_report.write_csv_report")
  @patch("sales_report.load")
  @patch("sales_report.parse_args")
  def test_main_filters_transactions_and_names_reports_by_date(
    self,
    mock_parse_args,
    mock_load,
    mock_write_csv_report,
  ):
    mock_parse_args.return_value.report_date = datetime.date(2024, 3, 1)
    mock_load.side_effect = [self.transactions, self.stores]

    sales_report.main()

    detail_call = mock_write_csv_report.call_args_list[0]
    summary_call = mock_write_csv_report.call_args_list[1]
    detail_rows = detail_call.args[3]
    summary_rows = summary_call.args[3]

    self.assertEqual(detail_call.args[1], "2024-03-01_transaction_detail_report.csv")
    self.assertEqual(summary_call.args[1], "2024-03-01_summary_report.csv")
    self.assertTrue(detail_rows)
    self.assertTrue(all(row["date"] == "2024-03-01" for row in detail_rows))
    self.assertEqual(len(detail_rows), 12)
    self.assertEqual(len(summary_rows), 5)


if __name__ == "__main__":
  unittest.main()
