#!/usr/bin/env python3
# Compute D1 retention by signup_date (UTC calendar days)

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
INTERIM.mkdir(parents=True, exist_ok=True)

# Load
users = pd.read_csv(RAW / "users.csv", parse_dates=["signup_ts"])
events = pd.read_csv(RAW / "events.csv", parse_dates=["event_ts"])

# Prep
users["signup_date"] = users["signup_ts"].dt.normalize()  # floor to day (UTC)
sess = events[events["event_type"] == "session_start"].copy()
sess["event_day"] = sess["event_ts"].dt.normalize()

# Cohort size per signup_date
cohort = (
    users.groupby("signup_date", as_index=False)["user_id"]
    .nunique()
    .rename(columns={"user_id": "cohort_size"})
)

# For each user, did they return on D+1 (exact calendar day)?
ue = users[["user_id", "signup_date"]].merge(
    sess[["user_id", "event_day"]], on="user_id", how="left"
)
ue["is_d1"] = ue["event_day"] == (ue["signup_date"] + pd.to_timedelta(1, "D"))

d1 = (
    ue.loc[ue["is_d1"]]
    .groupby("signup_date", as_index=False)["user_id"]
    .nunique()
    .rename(columns={"user_id": "d1_users"})
)

# Combine and compute rate
out = cohort.merge(d1, on="signup_date", how="left").fillna({"d1_users": 0})
out["d1_retention"] = (out["d1_users"] / out["cohort_size"]).round(4)
out = out.sort_values("signup_date")

# Save + print
path = INTERIM / "retention_d1.csv"
out.to_csv(path, index=False)
print(f"✅ saved {path}")
print(out.to_string(index=False))
