#!/usr/bin/env python3
import subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(__file__))
S = [
  "scripts/seed_synthetic_data.py",

  # core metrics
  "scripts/first_metrics.py",
  "scripts/compute_mau.py",
  "scripts/recompute_aov_pandas.py",

  # parity checks
  "scripts/sql_wau_parity.py",
  "scripts/sql_aov_parity.py",

  # retention & churn
  "scripts/retention_d1.py",
  "scripts/retention_d7.py",
  "scripts/retention_d30.py",
  "scripts/retention_summary.py",
  "scripts/churn_weekly.py",
  "scripts/sql_churn_parity.py",

  # north-star + drivers
  "scripts/opac_by_week.py",
  "scripts/rev_per_wau.py",
  "scripts/decomposition_check.py",
  "scripts/refund_rate_by_week.py",
  "scripts/opac_by_channel_week.py",

  # charts
  "scripts/make_wau_chart.py",
  "scripts/make_cohort_heatmap.py",
  "scripts/make_opac_chart.py",
  "scripts/make_rev_per_wau_chart.py",
  "scripts/make_opac_channel_bar_latest.py",

  # snapshot
  "scripts/weekly_kpis.py",
  "scripts/summary_day1.py",
]

def run(py):
  print(f"→ {py}")
  subprocess.run([sys.executable, os.path.join(ROOT, py)], check=True)

def main():
  for script in S:
    run(script)
  print("\n✅ Pipeline complete. Artifacts in data/interim/ and docs/charts/.")

if __name__ == "__main__":
  main()
