#!/usr/bin/env python3
# Make WAU line chart from data/interim/wau_by_week.csv

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
interim = ROOT / "data" / "interim"
charts = ROOT / "docs" / "charts"
charts.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(interim / "wau_by_week.csv", parse_dates=["week_start"])
df = df.sort_values("week_start")

plt.figure(figsize=(7, 4))
plt.plot(df["week_start"], df["wau"], marker="o")
plt.title("Weekly Active Users (WAU)")
plt.xlabel("ISO Week Start (UTC)")
plt.ylabel("WAU")
plt.grid(True, linewidth=0.4)
plt.tight_layout()

out = charts / "wau_trend.png"
plt.savefig(out, dpi=160)
print(f"✅ saved chart: {out}")
print(df.to_string(index=False))
