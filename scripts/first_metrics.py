#!/usr/bin/env python3
# Minimal WAU & AOV from the seeded CSVs (UTC, ISO week = Monday start)

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
INTERIM.mkdir(parents=True, exist_ok=True)

# --- Helpers ---
def week_start_utc(ts_series: pd.Series) -> pd.Series:
    # Monday 00:00:00 as start of ISO week (UTC-naive timestamps)
    return (ts_series - pd.to_timedelta(ts_series.dt.weekday, unit="D")).dt.normalize()

# --- Events → WAU ---
events = pd.read_csv(RAW / "events.csv", parse_dates=["event_ts"])
events = events[events["event_type"] == "session_start"].copy()
events["week_start"] = week_start_utc(events["event_ts"])
wau = (
    events.groupby("week_start", as_index=False)["user_id"]
    .nunique()
    .rename(columns={"user_id": "wau"})
    .sort_values("week_start")
)

# --- Orders → AOV (exclude refunds) ---
orders = pd.read_csv(RAW / "orders.csv", parse_dates=["order_ts"])
# be robust to 0/1 or "0"/"1"
orders["is_refund"] = pd.to_numeric(orders["is_refund"], errors="coerce").fillna(0).astype(int)
orders_nr = orders[orders["is_refund"] == 0].copy()
orders_nr["week_start"] = week_start_utc(orders_nr["order_ts"])

aov_by_week = (
    orders_nr.groupby("week_start")
    .agg(orders_net=("order_id", "count"), revenue_net=("revenue", "sum"))
    .reset_index()
    .sort_values("week_start")
)
aov_by_week["aov"] = aov_by_week["revenue_net"] / aov_by_week["orders_net"]

# --- Save + print ---
wau_path = INTERIM / "wau_by_week.csv"
aov_path = INTERIM / "aov_by_week.csv"
wau.to_csv(wau_path, index=False)
aov_by_week.to_csv(aov_path, index=False)

print("✅ Saved:")
print(f"  {wau_path}")
print(f"  {aov_path}\n")
print("WAU by week:")
print(wau.to_string(index=False))
print("\nAOV by week (net of refunds):")
print(aov_by_week.to_string(index=False, formatters={'aov': '{:.2f}'.format}))
