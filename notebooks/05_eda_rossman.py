"""Quick EDA on the cleaned Rossmann data - trend, distribution, weekday pattern."""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

df = pd.read_csv(DATA_DIR / "rossmann_clean.csv", parse_dates=["Date"])

plt.style.use("seaborn-v0_8-whitegrid")

weekly = df.set_index("Date").resample("W")["Sales"].sum()
fig, ax = plt.subplots(figsize=(11, 4))
weekly.plot(ax=ax, color="#2563eb")
ax.set_title("Total Weekly Sales - All Stores Combined")
ax.set_ylabel("Sales")
ax.set_xlabel("")
plt.tight_layout()
plt.savefig(OUTPUTS_DIR / "rossmann_weekly_trend.png", dpi=120)
plt.close()

fig, ax = plt.subplots(figsize=(8, 4))
df["Sales"].plot(kind="hist", bins=60, ax=ax, color="#059669", edgecolor="white")
ax.set_title("Distribution of Daily Sales (per store, per day)")
ax.set_xlabel("Sales")
plt.tight_layout()
plt.savefig(OUTPUTS_DIR / "rossmann_sales_distribution.png", dpi=120)
plt.close()

df["weekday"] = df["Date"].dt.day_name()
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
avg_by_weekday = df.groupby("weekday")["Sales"].mean().reindex(weekday_order)

fig, ax = plt.subplots(figsize=(8, 4))
avg_by_weekday.plot(kind="bar", ax=ax, color="#7c3aed")
ax.set_title("Average Sales by Day of Week")
ax.set_ylabel("Avg. sales")
ax.set_xlabel("")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(OUTPUTS_DIR / "rossmann_weekday_avg.png", dpi=120)
plt.close()

print(f"mean={df['Sales'].mean():.0f}  median={df['Sales'].median():.0f}  max={df['Sales'].max():.0f}")
print("Charts saved to outputs/")
