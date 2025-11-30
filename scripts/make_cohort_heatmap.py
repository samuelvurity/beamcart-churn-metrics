#!/usr/bin/env python3
# Make a D1/D7/D30 cohort heatmap from data/interim/retention_summary.csv

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
interim = ROOT / "data" / "interim"
charts = ROOT / "docs" / "charts"
charts.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(interim / "retention_summary.csv", parse_dates=["signup_date"])
df = df.sort_values("signup_date").reset_index(drop=True)

# Matrix of retention values in [0,1]
cols = ["d1_retention", "d7_retention", "d30_retention"]
mat = df[cols].to_numpy()

# Labels
ylabels = [d.date().isoformat() for d in df["signup_date"]]
xlabels = ["D1", "D7", "D30"]

# Plot
fig, ax = plt.subplots(figsize=(6, max(2.5, 0.5 * len(ylabels) + 1)))
im = ax.imshow(mat, aspect="auto")

# Ticks & labels
ax.set_xticks(np.arange(len(xlabels)), labels=xlabels)
ax.set_yticks(np.arange(len(ylabels)), labels=ylabels)
ax.set_xlabel("Retention Window")
ax.set_ylabel("Signup Cohort (UTC)")
ax.set_title("Cohort Retention (D1 / D7 / D30)")

# Annotate cells with percentages
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        val = mat[i, j]
        txt = f"{val*100:.0f}%"
        ax.text(
            j, i, txt, ha="center", va="center", fontsize=9, color="white" if val > 0.5 else "black"
        )

fig.tight_layout()
out = charts / "cohort_heatmap.png"
fig.savefig(out, dpi=160)
print(f"✅ saved chart: {out}")
