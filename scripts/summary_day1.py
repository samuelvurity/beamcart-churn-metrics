#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"

# Load
wau = pd.read_csv(INTERIM / "wau_by_week.csv", parse_dates=["week_start"]).sort_values("week_start")
aov = pd.read_csv(INTERIM / "aov_by_week.csv", parse_dates=["week_start"]).sort_values("week_start")
mau = pd.read_csv(INTERIM / "mau_by_month.csv").sort_values("month")

# Latest points (ignore NaN AOV if last week had only refunds)
last_wau = wau.iloc[-1]
last_aov = aov[aov["aov"].notna()].iloc[-1] if aov["aov"].notna().any() else aov.iloc[-1]
last_mau = mau.iloc[-1]

print("=== BeamCart KPI Snapshot (Day 1) ===")
print(f"WAU (week starting {last_wau['week_start'].date()}): {int(last_wau['wau'])}")
print(
    f"AOV (week starting {last_aov['week_start'].date()}): {last_aov['aov']:.2f}  "
    f"[orders={int(last_aov['orders_net'])}, revenue={last_aov['revenue_net']:.2f}]"
)
print(f"MAU ({last_mau['month']}): {int(last_mau['mau'])}")

# also save a small CSV for reference
out = INTERIM / "kpis_day1.csv"
pd.DataFrame(
    [
        {
            "week_start_wau": last_wau["week_start"],
            "wau": int(last_wau["wau"]),
            "week_start_aov": last_aov["week_start"],
            "aov": float(last_aov["aov"]),
            "orders_net": int(last_aov["orders_net"]),
            "revenue_net": float(last_aov["revenue_net"]),
            "month_mau": last_mau["month"],
            "mau": int(last_mau["mau"]),
        }
    ]
).to_csv(out, index=False)
print(f"\nSaved: {out}")
