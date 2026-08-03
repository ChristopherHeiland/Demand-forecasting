"""
Sales forecasting model.

RandomForestRegressor - handles non-linear patterns without much tuning,
no scaling needed, and feature_importances_ gives an interpretable read
on what actually drives sales.
"""

from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

df = pd.read_csv(DATA_DIR / "rossmann_clean.csv", parse_dates=["Date"])

# A handful of rows are marked Open=1 but have Sales=0 - looks like a
# recording glitch rather than real behaviour, and it wrecks MAPE
# (division by ~0), so drop them.
n_before = len(df)
df = df[df["Sales"] > 0].copy()
print(f"Dropped {n_before - len(df)} zero-sales-while-open rows")

df["year"] = df["Date"].dt.year
df["month"] = df["Date"].dt.month
df["day"] = df["Date"].dt.day
df["day_of_week"] = df["Date"].dt.dayofweek

df = pd.get_dummies(df, columns=["StoreType", "Assortment"], drop_first=True)

feature_cols = [
    "Store", "day_of_week", "month", "day", "Promo", "SchoolHoliday",
    "is_holiday", "CompetitionDistance",
] + [c for c in df.columns if c.startswith("StoreType_") or c.startswith("Assortment_")]

X = df[feature_cols]
y = df["Sales"]

# Chronological split - train on the past, test on the future. A random
# split would let the model see "future" rows during training.
df_sorted = df.sort_values("Date")
split_date = df_sorted["Date"].quantile(0.8, interpolation="nearest")
train_mask = df["Date"] <= split_date
X_train, X_test = X[train_mask], X[~train_mask]
y_train, y_test = y[train_mask], y[~train_mask]

print(f"Train: up to {split_date.date()} ({len(X_train):,} rows)")
print(f"Test:  after {split_date.date()} ({len(X_test):,} rows)")

model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)
mape = mean_absolute_percentage_error(y_test, preds) * 100

print(f"\nMAE:  {mae:,.0f} kr")
print(f"MAPE: {mape:.1f}%")
print(f"Avg actual sales (test): {y_test.mean():,.0f} kr")

importance = pd.Series(model.feature_importances_, index=feature_cols).sort_values(ascending=False)
print("\nTop features:")
print(importance.head(5).round(3))

fig, ax = plt.subplots(figsize=(8, 5))
importance.head(10).sort_values().plot(kind="barh", ax=ax, color="#ea580c")
ax.set_title("What Drives Sales Predictions? (Top 10 Features)")
ax.set_xlabel("Importance")
plt.tight_layout()
plt.savefig(OUTPUTS_DIR / "feature_importance.png", dpi=120)
plt.close()

sample_store = 1
mask = (df["Store"] == sample_store) & (~train_mask)
compare = pd.DataFrame({
    "Date": df.loc[mask, "Date"],
    "Actual": y[mask],
    "Predicted": model.predict(X[mask]),
}).sort_values("Date")

fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(compare["Date"], compare["Actual"], label="Actual", color="#111827")
ax.plot(compare["Date"], compare["Predicted"], label="Predicted", color="#dc2626", linestyle="--")
ax.set_title(f"Actual vs. Predicted Sales - Store {sample_store} (test period)")
ax.legend()
plt.tight_layout()
plt.savefig(OUTPUTS_DIR / "actual_vs_predicted.png", dpi=120)
plt.close()

export = df.loc[~train_mask, ["Date", "Store", "Sales"]].copy()
export["Predicted_Sales"] = preds
export.to_csv(OUTPUTS_DIR / "predictions_for_powerbi.csv", index=False)
print("\nSaved charts and predictions_for_powerbi.csv")
