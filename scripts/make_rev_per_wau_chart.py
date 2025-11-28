#!/usr/bin/env python3
# Make Revenue per WAU line chart from data/interim/rev_per_wau.csv

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
interim = ROOT / "data" / "interim"
charts = ROOT / "docs" / "charts"
charts.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(interim / "rev_per_wau.csv", parse_dates=["week_start"]).sort_values("week_start")

plt.figure(figsize=(7,4))
plt.plot(df["week_start"], df["rev_per_wau"], marker="o")
plt.title("Revenue per Weekly Active User (Rev/WAU)")
plt.xlabel("ISO Week Start (UTC)")
plt.ylabel("Rev/WAU")
plt.grid(True, linewidth=0.4)
plt.tight_layout()

out = charts / "rev_per_wau_trend.png"
plt.savefig(out, dpi=160)
print(f"✅ saved chart: {out}")
print(df.to_string(index=False, formatters={"rev_per_wau":"{:.2f}".format}))
