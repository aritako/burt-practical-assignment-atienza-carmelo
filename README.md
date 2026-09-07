# Daily Sales Reports

This project turns the daily exports from a point-of-sale system into two CSV reports:

- a transaction-level report for auditing and drill-downs
- a store-level summary for quickly comparing shop performance

The input files are kept in `data/`:

- `transactions.json` contains the day's sales records
- `stores.json` contains the shop registry used to resolve shop IDs into names and cities

The script uses only Python's standard library. The included virtual environment is ignored by Git and can be recreated locally.

## Requirements

- Python 3.12
- No third-party runtime dependencies

## Setup

From the repository root, create a virtual environment if one is not already available:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

There is no package installation step because the application uses the standard library only.

## Generate reports

To generate the reports for yesterday, run:

```bash
./.venv/bin/python sales_report.py
```

The command writes two files to `reports/`:

```text
YYYY-MM-DD_transaction_detail_report.csv
YYYY-MM-DD_summary_report.csv
```

`YYYY-MM-DD` is yesterday's date at the time the command runs.

The sample data is historical, so it can be run explicitly with a report date:

```bash
./.venv/bin/python sales_report.py --report-date 2024-03-01
```

The `--report-date` option is useful for rerunning a report, testing a particular export, or processing an older input file. It expects the format `YYYY-MM-DD`.

## Report contents

### Transaction detail

The detail report contains one row per transaction with these columns:

```text
date,country,channel,category,shop_name,shop_city,units_sold,revenue,transactions
```

### Store summary

The summary report groups the filtered transactions by shop and contains:

```text
shop_name,shop_city,total_units_sold,total_revenue,total_transactions
```

Transactions are filtered by date before either report is built, so the detail and summary reports always describe the same reporting day.

## Data handling

- Country codes are normalized to uppercase. Empty country values are written as `N/A`.
- Revenue values may be numeric or strings such as `$1,234.50`; currency symbols and thousands separators are removed before writing the CSV.
- A transaction whose `shop_id` is absent from `stores.json` is retained. Its `shop_name` and `shop_city` are written as `N/A` rather than dropping the sale.
- Missing transaction fields use the fallback values defined by the report generator.

## Tests

Run the complete test suite with the virtual environment's Python executable:

```bash
./.venv/bin/python -m unittest discover -v
```

The tests cover revenue normalization, date filtering, report filenames, store aggregation, missing transaction counts, missing countries, and unknown shops.

A compile check can be run separately:

```bash
./.venv/bin/python -m py_compile sales_report.py test_sales_report.py
```

## Project layout

```text
.
├── data/
│   ├── stores.json
│   └── transactions.json
├── reports/
├── sales_report.py
├── test_sales_report.py
└── README.md
```
