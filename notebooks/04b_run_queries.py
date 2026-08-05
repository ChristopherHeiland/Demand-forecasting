"""Run sql queries and print results."""

from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

pd.set_option("display.width", 100)
conn = sqlite3.connect(DATA_DIR / "rossmann.db")

queries = {
    "Avg sales by store type": """
        SELECT st.StoreType, COUNT(*) AS n_days,
               ROUND(AVG(s.Sales), 0) AS avg_daily_sales,
               ROUND(SUM(s.Sales) / 1000.0, 0) AS total_sales_thousands
        FROM sales s JOIN stores st ON s.Store = st.Store
        GROUP BY st.StoreType ORDER BY avg_daily_sales DESC;
    """,
    "Promo effect on sales": """
        SELECT Promo, ROUND(AVG(Sales), 0) AS avg_sales,
               ROUND(AVG(Customers), 0) AS avg_customers
        FROM sales GROUP BY Promo;
    """,
    "Monthly sales trend (first 6 months)": """
        SELECT strftime('%Y-%m', Date) AS year_month,
               ROUND(SUM(Sales) / 1000.0, 0) AS total_sales_thousands
        FROM sales GROUP BY year_month ORDER BY year_month LIMIT 6;
    """,
    "Top 10 stores by total sales": """
        SELECT * FROM (
            SELECT Store, SUM(Sales) AS total_sales,
                   RANK() OVER (ORDER BY SUM(Sales) DESC) AS sales_rank
            FROM sales GROUP BY Store
        ) WHERE sales_rank <= 10;
    """,
    "Sales by competition proximity": """
        SELECT
            CASE WHEN st.CompetitionDistance < 1000 THEN '< 1km'
                 WHEN st.CompetitionDistance < 5000 THEN '1-5km'
                 ELSE '5km+' END AS competition_proximity,
            ROUND(AVG(s.Sales), 0) AS avg_daily_sales,
            COUNT(DISTINCT s.Store) AS n_stores
        FROM sales s JOIN stores st ON s.Store = st.Store
        GROUP BY competition_proximity ORDER BY avg_daily_sales DESC;
    """,
}

for label, query in queries.items():
    print(f"\n--- {label} ---")
    print(pd.read_sql(query, conn).to_string(index=False))

conn.close()
