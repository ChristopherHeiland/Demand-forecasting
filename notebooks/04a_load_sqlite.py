"""Load raw tables into SQLite for the SQL queries in sql/queries.sql."""

from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

sales = pd.read_csv(DATA_DIR / "train.csv", parse_dates=["Date"])
stores = pd.read_csv(DATA_DIR / "store.csv")
sales = sales[sales["Open"] == 1].copy()

db_path = DATA_DIR / "rossmann.db"
conn = sqlite3.connect(db_path)

sales.to_sql("sales", conn, if_exists="replace", index=False)
stores.to_sql("stores", conn, if_exists="replace", index=False)

n1 = pd.read_sql("SELECT COUNT(*) AS n FROM sales", conn)["n"][0]
n2 = pd.read_sql("SELECT COUNT(*) AS n FROM stores", conn)["n"][0]
print(f"sales: {n1:,} rows | stores: {n2:,} rows")

conn.close()
print(f"DB saved to {db_path}")
