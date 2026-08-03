"""
Generate synthetic grocery sales data.

Simulated daily sales/waste across 5 stores and 10 products over two years, with
weekly and yearly seasonality plus noise.
"""

from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

np.random.seed(42)

stores = ["Oslo Vest", "Oslo Øst", "Bergen", "Trondheim", "Stavanger"]

# (name, category, is_perishable, base_daily_demand)
products = [
    ("Melk 1L",          "Meieri",      True,  120),
    ("Brød",             "Bakervarer",  True,  90),
    ("Bananer",          "Frukt",       True,  70),
    ("Yoghurt",          "Meieri",      True,  60),
    ("Pasta",            "Tørrvarer",   False, 40),
    ("Hermetiske bønner","Tørrvarer",   False, 25),
    ("Frossenpizza",     "Frossenmat",  False, 35),
    ("Iskrem",           "Frossenmat",  False, 30),
    ("Toalettpapir",     "Husholdning", False, 20),
    ("Kaffe",            "Tørrvarer",   False, 45),
]

date_range = pd.date_range(start="2024-01-01", end="2025-12-31", freq="D")

rows = []

for store in stores:
    store_multiplier = np.random.uniform(0.7, 1.4)

    for product_name, category, is_perishable, base_demand in products:
        for date in date_range:
            weekday = date.weekday()
            weekend_boost = 1.3 if weekday in [4, 5] else 1.0

            day_of_year = date.dayofyear
            if product_name == "Iskrem":
                # peaks mid-July
                seasonal = 1 + 0.9 * np.cos((day_of_year - 200) / 365 * 2 * np.pi)
            else:
                seasonal = 1 + 0.15 * np.cos((day_of_year - 15) / 365 * 2 * np.pi)

            noise = np.random.normal(1, 0.15)
            demand = base_demand * store_multiplier * weekend_boost * seasonal * noise
            units_sold = max(0, int(round(demand)))

            if is_perishable:
                buffer = np.random.uniform(0.05, 0.25)
                units_ordered = int(round(units_sold * (1 + buffer)))
                units_wasted = max(0, units_ordered - units_sold)
            else:
                units_ordered = units_sold
                units_wasted = 0

            rows.append({
                "date": date,
                "store": store,
                "product": product_name,
                "category": category,
                "is_perishable": is_perishable,
                "units_sold": units_sold,
                "units_ordered": units_ordered,
                "units_wasted": units_wasted,
            })

df = pd.DataFrame(rows)

output_path = DATA_DIR / "grocery_sales.csv"
df.to_csv(output_path, index=False)

print(f"{len(df):,} rows generated, {df['date'].min().date()} to {df['date'].max().date()}")
print(df.head())
