#!/usr/bin/env python3
# OPAC by acquisition_channel per ISO week:
# OPAC_channel_week = net_orders_channel_week / WAU_channel_week

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
INTERIM.mkdir(parents=True, exist_ok=True)


def week_start_utc(ts: pd.Series) -> pd.Series:
    return (ts - pd.to_timedelta(ts.dt.weekday, unit="D")).dt.normalize()


# Load base tables
users = pd.read_csv(RAW / "users.csv", parse_dates=["signup_ts"])
events = pd.read_csv(RAW / "events.csv", parse_dates=["event_ts"])
orders = pd.read_csv(RAW / "orders.csv", parse_dates=["order_ts"])

# Clean flags
orders["is_refund"] = pd.to_numeric(orders["is_refund"], errors="coerce").fillna(0).astype(int)

# --- WAU by channel & week (session_start only) ---
sess = events[events["event_type"] == "session_start"].merge(
    users[["user_id", "acquisition_channel"]], on="user_id", how="left"
)
sess["week_start"] = week_start_utc(sess["event_ts"])

wau_ch = (
    sess.drop_duplicates(subset=["user_id", "week_start"])  # distinct users per week
    .groupby(["week_start", "acquisition_channel"], as_index=False)["user_id"]
    .nunique()
    .rename(columns={"user_id": "wau"})
)

# --- Net orders by channel & week (exclude refunds) ---
ordu = orders.merge(users[["user_id", "acquisition_channel"]], on="user_id", how="left")
ordu["week_start"] = week_start_utc(ordu["order_ts"])

ord_ch = ordu.groupby(["week_start", "acquisition_channel"], as_index=False).agg(
    orders_net=("is_refund", lambda s: (s == 0).sum()),
    revenue_net=("revenue", lambda s: s.where(ordu.loc[s.index, "is_refund"] == 0, 0).sum()),
)

# --- Join + compute OPAC ---
out = (
    wau_ch.merge(ord_ch, on=["week_start", "acquisition_channel"], how="outer")
    .fillna({"wau": 0, "orders_net": 0, "revenue_net": 0.0})
    .sort_values(["week_start", "acquisition_channel"])
)

# avoid divide-by-zero
out["opac"] = out.apply(lambda r: (r["orders_net"] / r["wau"]) if r["wau"] > 0 else 0.0, axis=1)

# Save + print
path = INTERIM / "opac_by_channel_week.csv"
out.to_csv(path, index=False)

fmt = {"opac": "{:.4f}".format}
print(f"✅ saved {path}")
print(
    out[["week_start", "acquisition_channel", "wau", "orders_net", "opac"]].to_string(
        index=False, formatters=fmt
    )
)
