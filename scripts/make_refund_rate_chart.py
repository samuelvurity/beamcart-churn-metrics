#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

THRESHOLD = 0.06  # 6%
ROOT = Path(__file__).resolve().parents[1]
interim, charts = ROOT / "data" / "interim", ROOT / "docs" / "charts"
charts.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(interim / "refund_rate_by_week.csv", parse_dates=["week_start"]).sort_values(
    "week_start"
)
if df.empty:
    raise SystemExit("No refund data. Run pipeline first.")
last = df.iloc[-1]
alert = float(last["refund_rate"]) > THRESHOLD


plt.figure(figsize=(7, 4))
plt.plot(df["week_start"], df["refund_rate"], marker="o")
plt.axhline(THRESHOLD, linestyle="--", linewidth=1)
for x, y in zip(df["week_start"], df["refund_rate"]):
    plt.text(x, y, f"{y:.2%}", ha="center", va="bottom", fontsize=8)
plt.title(f"Refund Rate (guardrail {THRESHOLD:.0%})")
plt.xlabel("ISO Week Start (UTC)")
plt.ylabel("Refund Rate")
plt.grid(True, linewidth=0.4)
plt.tight_layout()
out = charts / "refund_rate_trend.png"
plt.savefig(out, dpi=160)

print(f"✅ saved chart: {out}")
print(f"Latest week {last['week_start'].date()} refund_rate={float(last['refund_rate']):.2%}")
print("⚠️ ALERT: above guardrail!" if alert else "✅ Within guardrail.")
