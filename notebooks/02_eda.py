"""EDA on the synthetic grocery dataset."""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

df = pd.read_csv(DATA_DIR / "grocery_sales.csv", parse_dates=["date"])

print(f"Rows: {df.shape[0]:,}  Columns: {df.shape[1]}")
print(df.dtypes)
print("\nMissing values:")
print(df.isna().sum())

print("\nTotal sales by store:")
sales_by_store = df.groupby("store")["units_sold"].sum().sort_values(ascending=False)
print(sales_by_store)

print("\nTotal sales by category:")
sales_by_category = df.groupby("category")["units_sold"].sum().sort_values(ascending=False)
print(sales_by_category)

print("\nWaste rate by product (perishables only):")
perishables = df[df["is_perishable"]]
waste_by_product = perishables.groupby("product").agg(
    total_sold=("units_sold", "sum"),
    total_wasted=("units_wasted", "sum"),
)
waste_by_product["waste_rate_pct"] = (
    waste_by_product["total_wasted"]
    / (waste_by_product["total_sold"] + waste_by_product["total_wasted"])
    * 100
).round(1)
print(waste_by_product.sort_values("waste_rate_pct", ascending=False))

print("\nAvg units sold by weekday:")
df["weekday"] = df["date"].dt.day_name()
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
weekday_avg = df.groupby("weekday")["units_sold"].mean()
print(weekday_avg.reindex(weekday_order).round(1))

plt.style.use("seaborn-v0_8-whitegrid")

monthly = df.set_index("date").resample("M")["units_sold"].sum()
fig, ax = plt.subplots(figsize=(10, 4))
monthly.plot(ax=ax, marker="o", color="#2563eb")
ax.set_title("Total Units Sold per Month (all stores, all products)")
ax.set_ylabel("Units sold")
ax.set_xlabel("")
plt.tight_layout()
plt.savefig(OUTPUTS_DIR / "monthly_trend.png", dpi=120)
plt.close()

fig, ax = plt.subplots(figsize=(8, 4))
waste_by_product["waste_rate_pct"].sort_values().plot(kind="barh", ax=ax, color="#dc2626")
ax.set_title("Waste Rate by Perishable Product (%)")
ax.set_xlabel("Waste rate (%)")
plt.tight_layout()
plt.savefig(OUTPUTS_DIR / "waste_rate.png", dpi=120)
plt.close()

print("\nCharts saved to output folder"
"/")
