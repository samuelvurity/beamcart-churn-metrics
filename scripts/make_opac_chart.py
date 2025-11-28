#!/usr/bin/env python3
# Make OPAC line chart from data/interim/opac_by_week.csv

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
interim = ROOT / "data" / "interim"
charts = ROOT / "docs" / "charts"
charts.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(interim / "opac_by_week.csv", parse_dates=["week_start"]).sort_values("week_start")

plt.figure(figsize=(7,4))
plt.plot(df["week_start"], df["opac"], marker="o")
plt.title("Orders per Active Customer (OPAC)")
plt.xlabel("ISO Week Start (UTC)")
plt.ylabel("OPAC")
plt.grid(True, linewidth=0.4)
plt.tight_layout()

out = charts / "opac_trend.png"
plt.savefig(out, dpi=160)
print(f"✅ saved chart: {out}")
print(df.to_string(index=False, formatters={"opac":"{:.4f}".format}))
