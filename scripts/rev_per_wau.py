#!/usr/bin/env python3
# Revenue per Weekly Active User (Rev/WAU), refunds excluded

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
INTERIM.mkdir(parents=True, exist_ok=True)


def week_start_utc(ts: pd.Series) -> pd.Series:
    return (ts - pd.to_timedelta(ts.dt.weekday, unit="D")).dt.normalize()


# WAU
events = pd.read_csv(RAW / "events.csv", parse_dates=["event_ts"])
events = events[events["event_type"] == "session_start"].copy()
events["week_start"] = week_start_utc(events["event_ts"])
wau = (
    events.groupby("week_start", as_index=False)["user_id"]
    .nunique()
    .rename(columns={"user_id": "wau"})
)

# Net revenue (exclude refunds)
orders = pd.read_csv(RAW / "orders.csv", parse_dates=["order_ts"])
orders["is_refund"] = pd.to_numeric(orders["is_refund"], errors="coerce").fillna(0).astype(int)
orders["week_start"] = week_start_utc(orders["order_ts"])
rev = orders.groupby("week_start", as_index=False).agg(
    revenue_net=("revenue", lambda s: s.where(orders.loc[s.index, "is_refund"] == 0, 0).sum())
)

# Join + compute
out = wau.merge(rev, on="week_start", how="left").fillna({"revenue_net": 0.0})
out["rev_per_wau"] = out["revenue_net"] / out["wau"]
out = out.sort_values("week_start")

path = INTERIM / "rev_per_wau.csv"
out.to_csv(path, index=False)

print(f"✅ saved {path}")
print(out.to_string(index=False, formatters={"rev_per_wau": "{:.2f}".format}))
