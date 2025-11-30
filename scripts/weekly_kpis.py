#!/usr/bin/env python3
# Combine WAU, OPAC, AOV, Rev/WAU, Refund Rate into one weekly KPI table

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
INTERIM.mkdir(parents=True, exist_ok=True)


def read_csv(name, parse_dates=None):
    return pd.read_csv(INTERIM / name, parse_dates=parse_dates)


wau = read_csv("wau_by_week.csv", parse_dates=["week_start"])
opac = read_csv("opac_by_week.csv", parse_dates=["week_start"])
aov = read_csv("aov_by_week.csv", parse_dates=["week_start"])
rpw = read_csv("rev_per_wau.csv", parse_dates=["week_start"])
rref = read_csv("refund_rate_by_week.csv", parse_dates=["week_start"])

df = (
    (
        wau.merge(
            opac[["week_start", "orders_net", "revenue_net", "opac"]], on="week_start", how="outer"
        )
        .merge(aov[["week_start", "aov"]], on="week_start", how="outer")
        .merge(
            rpw[["week_start", "revenue_net", "rev_per_wau"]].rename(
                columns={"revenue_net": "revenue_net_check"}
            ),
            on="week_start",
            how="outer",
        )
        .merge(rref, on="week_start", how="outer")
    )
    .sort_values("week_start")
    .reset_index(drop=True)
)

# prefer revenue_net from AOV computation; fall back to OPAC file if missing
df["revenue_net"] = df["revenue_net"].fillna(df["revenue_net_check"])

# tidy types / fills
for c in ["wau", "orders_net", "all_orders", "refund_orders"]:
    if c in df:
        df[c] = df[c].fillna(0).astype(int)
for c in ["aov", "opac", "rev_per_wau", "refund_rate"]:
    if c in df:
        df[c] = df[c].astype(float)

out_cols = [
    "week_start",
    "wau",
    "orders_net",
    "revenue_net",
    "aov",
    "opac",
    "rev_per_wau",
    "refund_rate",
]
out = df[out_cols]

# save & print
out_path = INTERIM / "weekly_kpis.csv"
out.to_csv(out_path, index=False)

fmt = {
    "aov": "{:.2f}".format,
    "opac": "{:.4f}".format,
    "rev_per_wau": "{:.2f}".format,
    "refund_rate": "{:.4f}".format,
}
print(f"✅ saved {out_path}")
print(out.to_string(index=False, formatters=fmt))
