#!/usr/bin/env python3
# Verify: revenue_net ≈ WAU × OPAC × AOV (all net of refunds)

import pandas as pd
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
INTERIM.mkdir(parents=True, exist_ok=True)

wau  = pd.read_csv(INTERIM / "wau_by_week.csv", parse_dates=["week_start"])
opac = pd.read_csv(INTERIM / "opac_by_week.csv", parse_dates=["week_start"])
aov  = pd.read_csv(INTERIM / "aov_by_week.csv",  parse_dates=["week_start"])

df = (wau.merge(opac[["week_start","opac","orders_net","revenue_net"]], on="week_start", how="outer")
          .merge(aov[["week_start","aov","orders_net","revenue_net"]]
                   .rename(columns={"orders_net":"orders_net_aov","revenue_net":"revenue_net_aov"}),
                 on="week_start", how="outer"))

# Prefer revenue_net from AOV file (same numbers), fall back to OPAC file if needed
df["revenue_net_final"] = df["revenue_net_aov"].fillna(df["revenue_net"])
df["predicted_revenue"] = df["wau"] * df["opac"] * df["aov"]

# Differences
df["abs_diff"] = (df["predicted_revenue"] - df["revenue_net_final"]).abs()
df["pct_diff"] = df["abs_diff"] / df["revenue_net_final"].replace({0: np.nan})

out = df[["week_start","wau","opac","aov","predicted_revenue","revenue_net_final","abs_diff","pct_diff"]] \
         .sort_values("week_start")

out_path = INTERIM / "decomposition_check.csv"
out.to_csv(out_path, index=False)

print(f"✅ saved {out_path}")
print(out.to_string(index=False, 
                    formatters={
                        "opac":"{:.4f}".format,
                        "aov":"{:.2f}".format,
                        "predicted_revenue":"{:.2f}".format,
                        "revenue_net_final":"{:.2f}".format,
                        "abs_diff":"{:.2f}".format,
                        "pct_diff": (lambda v: "—" if pd.isna(v) else f"{v*100:.2f}%")
                    }))
# Quick pass/fail (ignore weeks with zero revenue)
mask = out["revenue_net_final"] > 0
if mask.any() and not (out.loc[mask, "pct_diff"] <= 1e-6).all():
    raise SystemExit("❌ Decomposition mismatch beyond tolerance.")
print("✅ Decomposition parity OK")
