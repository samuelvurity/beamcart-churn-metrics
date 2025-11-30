#!/usr/bin/env python3
# Compute D7 retention by signup_date (UTC calendar days)

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
INTERIM.mkdir(parents=True, exist_ok=True)

users = pd.read_csv(RAW / "users.csv", parse_dates=["signup_ts"])
events = pd.read_csv(RAW / "events.csv", parse_dates=["event_ts"])

users["signup_date"] = users["signup_ts"].dt.normalize()
sess = events[events["event_type"] == "session_start"].copy()
sess["event_day"] = sess["event_ts"].dt.normalize()

cohort = (
    users.groupby("signup_date", as_index=False)["user_id"]
    .nunique()
    .rename(columns={"user_id": "cohort_size"})
)

ue = users[["user_id", "signup_date"]].merge(
    sess[["user_id", "event_day"]], on="user_id", how="left"
)
ue["is_d7"] = ue["event_day"] == (ue["signup_date"] + pd.to_timedelta(7, "D"))

d7 = (
    ue.loc[ue["is_d7"]]
    .groupby("signup_date", as_index=False)["user_id"]
    .nunique()
    .rename(columns={"user_id": "d7_users"})
)

out = cohort.merge(d7, on="signup_date", how="left").fillna({"d7_users": 0})
out["d7_retention"] = (out["d7_users"] / out["cohort_size"]).round(4)
out = out.sort_values("signup_date")

path = INTERIM / "retention_d7.csv"
out.to_csv(path, index=False)
print(f"✅ saved {path}")
print(out.to_string(index=False))
