#!/usr/bin/env python3
import pandas as pd, matplotlib.pyplot as plt
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
interim, charts = ROOT/"data"/"interim", ROOT/"docs"/"charts"
charts.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(interim/"wau_by_week.csv", parse_dates=["week_start"]).sort_values("week_start")
if df.empty: raise SystemExit("No WAU data. Run pipeline first.")
mu = df["wau"].mean()
sigma = df["wau"].std(ddof=1) if len(df) > 1 else 0.0
ucl, lcl = mu + 3*sigma, max(0, mu - 3*sigma)

out_of_ctrl = df[(df["wau"] > ucl) | (df["wau"] < lcl)]

plt.figure(figsize=(7,4))
plt.plot(df["week_start"], df["wau"], marker="o")
plt.axhline(mu, linestyle="--", linewidth=1)
plt.axhline(ucl, linestyle=":", linewidth=1)
plt.axhline(lcl, linestyle=":", linewidth=1)
for _, r in out_of_ctrl.iterrows():
    plt.scatter(r["week_start"], r["wau"], s=60)
    plt.text(r["week_start"], r["wau"], f"{int(r['wau'])}", ha="left", va="bottom", fontsize=8)
plt.title("WAU Control Chart (mean ± 3σ)")
plt.xlabel("ISO Week Start (UTC)"); plt.ylabel("WAU"); plt.grid(True, linewidth=0.4); plt.tight_layout()
out = charts/"wau_control_chart.png"; plt.savefig(out, dpi=160)
print(f"✅ saved chart: {out}")
if len(out_of_ctrl):
    print("\n⚠️ Out-of-control weeks:")
    print(out_of_ctrl[["week_start","wau"]].to_string(index=False))
else:
    print("\n✅ No points beyond control limits.")
