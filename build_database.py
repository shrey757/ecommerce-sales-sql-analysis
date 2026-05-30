"""
build_database.py  |  Create ecommerce.db (SQLite) from the CSV files.

Steps:
  1. Create a fresh SQLite database file.
  2. Run schema.sql to create the tables.
  3. Load each CSV into its table.

Run:  python build_database.py
"""

import csv
import sqlite3
import os

DB_FILE = "ecommerce.db"
SCHEMA_FILE = "sql/schema.sql"

# (csv path, table name, columns in insert order)
TABLES = [
    ("data/customers.csv", "customers",
     ["customer_id", "customer_name", "city", "province", "signup_date"]),
    ("data/products.csv", "products",
     ["product_id", "product_name", "category", "price"]),
    ("data/orders.csv", "orders",
     ["order_id", "customer_id", "order_date", "status"]),
    ("data/order_items.csv", "order_items",
     ["order_item_id", "order_id", "product_id", "quantity", "unit_price"]),
]


def main():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")

    # 1 + 2: create tables from schema.sql
    with open(SCHEMA_FILE) as f:
        conn.executescript(f.read())

    # 3: load the CSVs
    for csv_path, table, columns in TABLES:
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            rows = [tuple(row[c] for c in columns) for row in reader]
        placeholders = ", ".join(["?"] * len(columns))
        conn.executemany(
            f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
            rows,
        )
        print(f"Loaded {len(rows):>5} rows into {table}")

    conn.commit()
    conn.close()
    print(f"\nDatabase built: {DB_FILE}")


if __name__ == "__main__":
    main()
