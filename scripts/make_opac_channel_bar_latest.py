#!/usr/bin/env python3
# Bar chart: OPAC by acquisition_channel for the most recent ISO week

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
interim = ROOT / "data" / "interim"
charts = ROOT / "docs" / "charts"
charts.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(interim / "opac_by_channel_week.csv", parse_dates=["week_start"])
latest = df["week_start"].max()
week = df[df["week_start"] == latest].copy().sort_values("opac", ascending=False)

plt.figure(figsize=(7, 4))
plt.bar(week["acquisition_channel"], week["opac"])
for i, (ch, opac, wau) in enumerate(zip(week["acquisition_channel"], week["opac"], week["wau"])):
    plt.text(i, opac, f"{opac:.2f}\nWAU={int(wau)}", ha="center", va="bottom", fontsize=9)

plt.title(f"OPAC by Channel — Week starting {latest.date()}")
plt.xlabel("Acquisition Channel")
plt.ylabel("OPAC")
plt.tight_layout()

out = charts / "opac_by_channel_latest.png"
plt.savefig(out, dpi=160)
print(f"✅ saved chart: {out}")
print(
    week[["week_start", "acquisition_channel", "wau", "orders_net", "opac"]].to_string(
        index=False, formatters={"opac": "{:.4f}".format}
    )
)
