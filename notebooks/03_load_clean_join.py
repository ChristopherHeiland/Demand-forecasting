"""Load, clean, and join the Rossmann sales and store tables."""

from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
sales = pd.read_csv(DATA_DIR / "train.csv", parse_dates=["Date"])
stores = pd.read_csv(DATA_DIR / "store.csv")

print(f"sales:  {sales.shape}")
print(f"stores: {stores.shape}")

print("\nMissing values in stores.csv:")
print(stores.isna().sum())

# CompetitionOpenSince* and Promo2* are missing for a real reason (no
# competitor on record / store never joined Promo2) - not filled.
# CompetitionDistance has 3 genuine gaps, filled with the median.
median_dist = stores["CompetitionDistance"].median()
stores["CompetitionDistance"] = stores["CompetitionDistance"].fillna(median_dist)

df = sales.merge(stores, on="Store", how="left")
print(f"\nJoined shape: {df.shape}")

print("\nOpen vs closed:")
print(df["Open"].value_counts())

# Closed days always have Sales == 0 - not useful for a forecasting model,
# so they're dropped here (kept in the raw table if needed elsewhere).
df_open = df[df["Open"] == 1].copy()

df_open["is_holiday"] = df_open["StateHoliday"].astype(str).apply(lambda x: x != "0")

out_path = DATA_DIR / "rossmann_clean.csv"
df_open.to_csv(out_path, index=False)
print(f"\nSaved: {out_path}  shape={df_open.shape}")
