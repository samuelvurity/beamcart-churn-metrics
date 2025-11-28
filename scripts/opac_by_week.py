#!/usr/bin/env python3
# OPAC (Orders per Active Customer) weekly:
# OPAC = net_orders / WAU  (refunds excluded, ISO week = Monday start)

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
INTERIM.mkdir(parents=True, exist_ok=True)

def week_start_utc(ts: pd.Series) -> pd.Series:
    return (ts - pd.to_timedelta(ts.dt.weekday, unit="D")).dt.normalize()

# --- WAU from events ---
events = pd.read_csv(RAW / "events.csv", parse_dates=["event_ts"])
events = events[events["event_type"] == "session_start"].copy()
events["week_start"] = week_start_utc(events["event_ts"])
wau = (events.groupby("week_start", as_index=False)["user_id"]
             .nunique()
             .rename(columns={"user_id":"wau"}))

# --- Net orders from orders (exclude refunds) ---
orders = pd.read_csv(RAW / "orders.csv", parse_dates=["order_ts"])
orders["is_refund"] = pd.to_numeric(orders["is_refund"], errors="coerce").fillna(0).astype(int)
orders["week_start"] = week_start_utc(orders["order_ts"])

ord_week = (orders.groupby("week_start", as_index=False)
                 .agg(orders_net=("is_refund", lambda s: (s == 0).sum()),
                      revenue_net=("revenue",  lambda s: s.where(orders.loc[s.index, "is_refund"] == 0, 0).sum())))

# --- OPAC join + compute ---
out = wau.merge(ord_week, on="week_start", how="left").fillna({"orders_net": 0, "revenue_net": 0.0})
out["opac"] = out["orders_net"] / out["wau"]
out = out.sort_values("week_start")

path = INTERIM / "opac_by_week.csv"
out.to_csv(path, index=False)

print(f"✅ saved {path}")
print(out.to_string(index=False, formatters={"opac":"{:.4f}".format}))
