#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
INTERIM.mkdir(parents=True, exist_ok=True)

orders = pd.read_csv(RAW / "orders.csv", parse_dates=["order_ts"])
orders["is_refund"] = pd.to_numeric(orders["is_refund"], errors="coerce").fillna(0).astype(int)

# include ALL orders to keep weeks that have only refunds
orders["week_start"] = (
    orders["order_ts"] - pd.to_timedelta(orders["order_ts"].dt.weekday, unit="D")
).dt.normalize()

# conditional aggregation to mirror SQL
grp = orders.groupby("week_start", as_index=False)
aov_by_week = grp.agg(
    orders_net=("is_refund", lambda s: (s == 0).sum()),
    revenue_net=("revenue", lambda s: s.where(orders.loc[s.index, "is_refund"] == 0, 0).sum()),
)

# compute AOV; keep NaN when orders_net == 0 (same as SQL)
aov_by_week["aov"] = aov_by_week["revenue_net"] / aov_by_week["orders_net"]

aov_by_week = aov_by_week.sort_values("week_start")
out = INTERIM / "aov_by_week.csv"
aov_by_week.to_csv(out, index=False)

print(f"✅ recomputed pandas AOV -> {out}")
print(aov_by_week.to_string(index=False, formatters={"aov": "{:.6f}".format}))
