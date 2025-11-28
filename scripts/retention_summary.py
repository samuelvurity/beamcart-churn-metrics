#!/usr/bin/env python3
# Join D1/D7/D30 retention into one CSV for plotting

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
INTERIM.mkdir(parents=True, exist_ok=True)

d1  = pd.read_csv(INTERIM / "retention_d1.csv",  parse_dates=["signup_date"])
d7  = pd.read_csv(INTERIM / "retention_d7.csv",  parse_dates=["signup_date"])
d30 = pd.read_csv(INTERIM / "retention_d30.csv", parse_dates=["signup_date"])

# outer-join on signup_date so we don't lose any cohorts
out = (d1[["signup_date","cohort_size","d1_retention"]]
       .merge(d7[["signup_date","d7_retention"]],  on="signup_date", how="outer")
       .merge(d30[["signup_date","d30_retention"]], on="signup_date", how="outer")
       .sort_values("signup_date")
       .reset_index(drop=True))

# Fill any missing rates with 0.0 (safe for our tiny seed; in real data you might leave NaN)
for c in ["d1_retention","d7_retention","d30_retention"]:
    if c in out:
        out[c] = out[c].fillna(0.0)

path = INTERIM / "retention_summary.csv"
out.to_csv(path, index=False)

print(f"✅ saved {path}")
print(out.to_string(index=False, 
                    formatters={"d1_retention":"{:.4f}".format,
                                "d7_retention":"{:.4f}".format,
                                "d30_retention":"{:.4f}".format}))
