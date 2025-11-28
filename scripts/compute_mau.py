#!/usr/bin/env python3
# Compute MAU from events.csv (UTC, calendar month)

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
INTERIM.mkdir(parents=True, exist_ok=True)

events = pd.read_csv(RAW / "events.csv", parse_dates=["event_ts"])
events = events[events["event_type"] == "session_start"].copy()

# calendar month label like "2025-10"
events["month"] = events["event_ts"].dt.strftime("%Y-%m")

mau = (
    events.groupby("month", as_index=False)["user_id"]
    .nunique()
    .rename(columns={"user_id": "mau"})
    .sort_values("month")
)

out = INTERIM / "mau_by_month.csv"
mau.to_csv(out, index=False)

print(f"✅ saved: {out}")
print(mau.to_string(index=False))
