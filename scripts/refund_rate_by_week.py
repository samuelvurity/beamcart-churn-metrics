#!/usr/bin/env python3
# Weekly refund rate = refund_orders / all_orders (ISO week = Monday start)

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
INTERIM.mkdir(parents=True, exist_ok=True)

def week_start_utc(ts: pd.Series) -> pd.Series:
    return (ts - pd.to_timedelta(ts.dt.weekday, unit="D")).dt.normalize()

orders = pd.read_csv(RAW / "orders.csv", parse_dates=["order_ts"])
orders["is_refund"] = pd.to_numeric(orders["is_refund"], errors="coerce").fillna(0).astype(int)
orders["week_start"] = week_start_utc(orders["order_ts"])

agg = (orders.groupby("week_start", as_index=False)
             .agg(all_orders=("order_id","count"),
                  refund_orders=("is_refund", lambda s: (s == 1).sum())))

agg["refund_rate"] = agg["refund_orders"] / agg["all_orders"]
agg = agg.sort_values("week_start")

out = INTERIM / "refund_rate_by_week.csv"
agg.to_csv(out, index=False)

print(f"✅ saved {out}")
print(agg.to_string(index=False, 
                    formatters={"refund_rate": (lambda v: "NaN" if pd.isna(v) else f"{v:.4f}")}))
