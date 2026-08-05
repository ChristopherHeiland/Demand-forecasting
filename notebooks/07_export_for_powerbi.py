"""Export cleaned + predicted data for Power BI."""

from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

df = pd.read_csv(DATA_DIR / "rossmann_clean.csv", parse_dates=["Date"])
df = df[df["Sales"] > 0].copy()

df["DayOfWeekName"] = df["Date"].dt.day_name()
df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)
df["is_holiday"] = df["is_holiday"].astype(bool)

df["year"] = df["Date"].dt.year
df["month"] = df["Date"].dt.month
df["day"] = df["Date"].dt.day
df["day_of_week"] = df["Date"].dt.dayofweek

df_enc = pd.get_dummies(df, columns=["StoreType", "Assortment"], drop_first=True)
feature_cols = [
    "Store", "day_of_week", "month", "day", "Promo", "SchoolHoliday",
    "is_holiday", "CompetitionDistance",
] + [c for c in df_enc.columns if c.startswith("StoreType_") or c.startswith("Assortment_")]
X = df_enc[feature_cols]
y = df_enc["Sales"]

split_date = df_enc.sort_values("Date")["Date"].quantile(0.8, interpolation="nearest")
train_mask = df_enc["Date"] <= split_date

model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
model.fit(X[train_mask], y[train_mask])

df["Predicted_Sales"] = model.predict(X).round(0)
df["Prediction_Error"] = df["Predicted_Sales"] - df["Sales"]
df["Is_Test_Period"] = ~train_mask.values

daily_cols = [
    "Date", "Store", "StoreType", "Assortment", "DayOfWeekName", "YearMonth",
    "Sales", "Predicted_Sales", "Prediction_Error", "Customers", "Promo",
    "is_holiday", "SchoolHoliday", "CompetitionDistance", "Is_Test_Period",
]
daily = df[daily_cols].rename(columns={"is_holiday": "IsHoliday"})
daily.to_csv(OUTPUTS_DIR / "daily_sales.csv", index=False)
print(f"daily_sales.csv: {daily.shape}")

store_summary = df.groupby(["Store", "StoreType", "Assortment", "CompetitionDistance"]).agg(
    Total_Sales=("Sales", "sum"),
    Avg_Daily_Sales=("Sales", "mean"),
    Avg_Customers=("Customers", "mean"),
    Days_With_Promo=("Promo", "sum"),
    N_Days=("Sales", "count"),
).reset_index()
store_summary["Avg_Daily_Sales"] = store_summary["Avg_Daily_Sales"].round(0)
store_summary["Avg_Customers"] = store_summary["Avg_Customers"].round(0)
store_summary.to_csv(OUTPUTS_DIR / "store_summary.csv", index=False)
print(f"store_summary.csv: {store_summary.shape}")
