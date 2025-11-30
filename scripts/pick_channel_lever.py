#!/usr/bin/env python3
# Pick the top channel by OPAC in the most recent ISO week

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"

df = pd.read_csv(INTERIM / "opac_by_channel_week.csv", parse_dates=["week_start"])
df = df[df["wau"] > 0].copy()
latest = df["week_start"].max()
week = df[df["week_start"] == latest].copy()

week = week.sort_values("opac", ascending=False)
top = week.iloc[0]

print("=== OPAC by Channel — Latest Week ===")
print(
    week[["week_start", "acquisition_channel", "wau", "orders_net", "opac"]].to_string(
        index=False, formatters={"opac": "{:.4f}".format}
    )
)
print("\n>>> Recommended initial lever (highest OPAC):")
print(
    f"Week starting {latest.date()} — channel = {top['acquisition_channel']} "
    f"(WAU={int(top['wau'])}, orders={int(top['orders_net'])}, OPAC={top['opac']:.4f})"
)
