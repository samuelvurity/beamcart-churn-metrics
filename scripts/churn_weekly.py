#!/usr/bin/env python3
# Weekly churn: users active in week t-1 but NOT in week t

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
INTERIM.mkdir(parents=True, exist_ok=True)


def week_start_utc(ts: pd.Series) -> pd.Series:
    return (ts - pd.to_timedelta(ts.dt.weekday, unit="D")).dt.normalize()


# Load events and create weekly active sets
events = pd.read_csv(RAW / "events.csv", parse_dates=["event_ts"])
events = events[events["event_type"] == "session_start"].copy()
events["week_start"] = week_start_utc(events["event_ts"])

# one row per (week, user)
wk_user = events[["user_id", "week_start"]].drop_duplicates()

# Build dict: week_start -> set(user_id)
weeks = sorted(wk_user["week_start"].unique())
active_sets = {w: set(wk_user.loc[wk_user["week_start"] == w, "user_id"]) for w in weeks}

rows = []
for i in range(1, len(weeks)):
    t = weeks[i]
    tm1 = weeks[i - 1]
    prev_set = active_sets.get(tm1, set())
    cur_set = active_sets.get(t, set())
    churned = prev_set - cur_set
    rows.append(
        {
            "week_start": t,
            "active_t_minus_1": len(prev_set),
            "churned_users": len(churned),
            "churn_rate": (len(churned) / len(prev_set)) if len(prev_set) > 0 else float("nan"),
        }
    )

out = pd.DataFrame(rows).sort_values("week_start")
path = INTERIM / "churn_weekly.csv"
out.to_csv(path, index=False)

print(f"✅ saved {path}")
print(out.to_string(index=False, formatters={"churn_rate": "{:.4f}".format}))
