# Practical Assignment

You are tasked to work on the following project. Assume that your code should be production-ready.

# Daily Sales Report

A shop owner’s point of sale system produces two export files daily, which you will find in the data/ directory:

`transactions.json` — the day’s sales transactions

`stores.json` — the store registry

The shop owner has asked us for help. Every morning they want two CSV reports generated automatically from the previous day’s exports.

**Report 1 — Transaction Detail**

A full breakdown of every transaction, with these columns:

 - `date`
 - `country`
 - `channel`
 - `category`
 - `shop_name`
 - `shop_city`
 - `units_sold`
 - `revenue`
 - `transactions`

**Report 2 — Store Summary**

A rolled-up view of how each shop performed, with these columns:

 - `shop_name`
 - `shop_city`
 - `total_units_sold`
 - `total_revenue`
 - `total_transactions`

Right now, the shop owner is piecing these together by hand and it’s painful, so they’d like them produced automatically each day from the raw exports.

If there are missing or unexpected fields, use N/A as the value.

## Submission

We require the following files:

1. Source code
2. A `README.md` file containing the following:
  - Walkthrough of code
  - Instructions to run
3. Submit your code as a public GitHub repository link with the following naming convention:

```
burt-practical-assignment-<surname>-<first_name>
```


## Technical Requirements

For frictionless checking of your submission, we also require the following:

 - The assignment must be written in either **Ruby 3.4** or **Python 3.12**.
 - Only use the **standard library (with the exception of unit testing libraries)**. Given that, we also expect that there be only core dependencies in your submission. 
 - Make sure that **virtual environments** are configured in your submission.
