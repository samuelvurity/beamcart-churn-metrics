#!/usr/bin/env python3
"""
Sample size (per arm) for OPAC lift tests.

Model:
- Per-user weekly orders ~ Poisson(λ)  with λ ≈ baseline OPAC.
- Overdispersion φ >= 1 allowed: Var ≈ φ * λ.
- Two-sample z-test approximation on means.

n_per_arm ≈ 2 * (z_{1-α/2} + z_{power})^2 * (φ * λ) / (Δ^2),
where Δ = lift * λ  (e.g., lift=0.05 for +5%).

CUPED (optional):
- If you use a covariate with correlation ρ to the outcome,
  effective n reduces by (1 - ρ^2).

CLI:
  --baseline BASE_OPAC      (default: take last row from data/interim/opac_by_week.csv)
  --lift 0.05               target proportional lift (e.g., 0.05 = +5%)
  --alpha 0.05
  --power 0.80
  --overdispersion 1.0      φ (>=1). Use 1.2–1.5 if you expect extra variability.
  --rho 0.0                 CUPED correlation (0..1); n_cuped = n * (1-ρ^2)
  --weeks 1                 number of **measurement weeks** (if you measure for multiple weeks, divide n per arm by weeks to interpret as WAU per arm needed)
"""
import argparse, math
import pandas as pd
from pathlib import Path
from math import sqrt
from statistics import fmean
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"

def read_baseline_opac():
    p = INTERIM / "opac_by_week.csv"
    if not p.exists():
        raise SystemExit("Missing data/interim/opac_by_week.csv. Run the pipeline first.")
    df = pd.read_csv(p, parse_dates=["week_start"]).sort_values("week_start")
    last = df.iloc[-1]
    return float(last["opac"]), pd.to_datetime(last["week_start"]).date(), int(last.get("wau", 0))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", type=float, default=None, help="Baseline OPAC (override).")
    ap.add_argument("--lift", type=float, default=0.05, help="Target proportional lift (e.g., 0.05 = +5%).")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--power", type=float, default=0.80)
    ap.add_argument("--overdispersion", type=float, default=1.0)
    ap.add_argument("--rho", type=float, default=0.0, help="CUPED correlation (0..1).")
    ap.add_argument("--weeks", type=int, default=1, help="Measurement weeks (>=1).")
    args = ap.parse_args()

    # Baseline OPAC
    if args.baseline is None:
        lam, last_week, last_wau = read_baseline_opac()
        src = f"last observed week ({last_week}, WAU={last_wau})"
    else:
        lam = float(args.baseline)
        src = "override --baseline"

    if lam <= 0:
        raise SystemExit("Baseline OPAC must be > 0 for this approximation.")

    alpha = args.alpha
    power = args.power
    lift = args.lift
    phi = max(1.0, args.overdispersion)
    rho = max(0.0, min(0.999, args.rho))
    weeks = max(1, args.weeks)

    z_alpha = norm.ppf(1 - alpha/2)
    z_beta  = norm.ppf(power)

    delta = lift * lam                 # absolute lift in orders/user-week
    var_u = phi * lam                  # per-user variance (Poisson * overdispersion)
    n_per_arm = 2 * (z_alpha + z_beta)**2 * var_u / (delta**2)

    # CUPED reduction
    n_cuped = n_per_arm * (1 - rho**2)

    # If measuring for multiple weeks (same users), you effectively get weeks× observations
    # So translate to **WAU per arm** as n_per_arm / weeks
    wau_per_arm = math.ceil(n_per_arm / weeks)
    wau_per_arm_cuped = math.ceil(n_cuped / weeks)

    print("=== OPAC A/B Sample Size (per arm) ===")
    print(f"Baseline OPAC (λ):      {lam:.4f}  [{src}]")
    print(f"Target lift:            {lift*100:.1f}%")
    print(f"Alpha (two-sided):      {alpha:.3f}")
    print(f"Power:                  {power:.2f}")
    print(f"Overdispersion φ:       {phi:.2f}")
    print(f"Measurement weeks:      {weeks}")
    print(f"---")
    print(f"Required users/arm (WAU, 1 week): {math.ceil(n_per_arm):,}")
    if weeks > 1:
        print(f"Required WAU/arm given {weeks} week(s): {wau_per_arm:,}")
    if rho > 0:
        print(f"\nCUPED (ρ={rho:.2f}) → users/arm: {math.ceil(n_cuped):,}  |  WAU/arm for {weeks} week(s): {wau_per_arm_cuped:,}")
    print("\nNotes:")
    print("- Model assumes per-user orders ≈ Poisson; φ accounts for extra variance.")
    print("- For 2-week tests, set --weeks 2; result is WAU per arm per week.")
    print("- If your pre-period metric correlates with outcome, pass --rho for CUPED.")
    print("- Always sanity-check with your actual traffic and guardrails.")
if __name__ == "__main__":
    main()
