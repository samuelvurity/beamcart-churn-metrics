#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
interim = ROOT / "data" / "interim"
charts = ROOT / "docs" / "charts"
memo = ROOT / "docs" / "decision_memo.md"

wk = pd.read_csv(interim / "weekly_kpis.csv", parse_dates=["week_start"]).sort_values("week_start")
last = wk.iloc[-1]


def fmt(v, f):
    try:
        return f.format(v)
    except Exception:
        return str(v)


md = f"""# BeamCart — Churn & North-Star Metrics Playbook (v0)

## Problem & context
WAU flat, paid acquisition rising, and refunds previously spiked. We need a single weekly metric that is actionable and tied to value, plus guardrails to avoid gaming.

## North-Star
**OPAC — Orders per Active Customer (weekly)**.  
*Why:* It’s a leading, controllable metric; moving order frequency via product & lifecycle levers moves revenue quickly.  
**Identity:** Revenue ≈ WAU × OPAC × AOV (all net of refunds).

## Latest KPI snapshot (ISO week starting {last['week_start'].date()})
- **WAU:** {int(last['wau'])}
- **Orders (net):** {int(last['orders_net'])}
- **Revenue (net):** {last['revenue_net']:.2f}
- **AOV:** {last['aov']:.2f}
- **OPAC:** {last['opac']:.4f}
- **Rev/WAU:** {last['rev_per_wau']:.2f}
- **Refund rate:** {last['refund_rate']:.4f}

## Driver tree (text)
OPAC
- Visit frequency (sessions/active): lifecycle nudges, on-site recirculation
- Conversion/session: UX friction, merchandising fit, trust
- Supply & price: in-stock rate, promo strategy (avoid refund-inducing)

**Guardrails:** Refund rate ≤ 6% (weekly).  
**Segments:** acquisition_channel, country (compute and watch deltas).

## Charts
- WAU trend: `docs/charts/wau_trend.png`
- Cohort retention: `docs/charts/cohort_heatmap.png`
- OPAC trend: `docs/charts/opac_trend.png`
- Rev/WAU trend: `docs/charts/rev_per_wau_trend.png`
- OPAC by channel (latest): `docs/charts/opac_by_channel_latest.png`

## First experiment (v0)
- Lever: “Continue your cart” sticky card + 2-item bundle on Home.  
- Audience: Activated WAU (≥1 session within 7 days of signup).  
- Target: +5% OPAC vs control over 2 weeks; **guardrail:** refund_rate ≤ 6%.  
- Design: 50/50 user-level holdout; cap notifications; ISO-week attribution (UTC).  
- Readout: OPAC (primary), Rev/WAU + AOV (secondary), WAU context; cut by channel & country; spot-check D1/D7.  
- Ship rule: Ship if OPAC lift ≥ +5% and guardrail holds; else pivot to size-finder UX test.

## Risks & assumptions
- Tiny seed dataset; numbers demonstrate wiring/parity, not real magnitude.
- UTC + ISO week definitions locked; refunds excluded from revenue/AOV/OPAC.

## Next steps (1–2 weeks)
- Scale seed → larger synthetic/public CSVs (50k–200k rows).
- Add cohort-by-channel table; annotate promo weeks.
- Add simple KPI tile (optional).
"""
memo.write_text(md)
print(f"✅ wrote memo: {memo}")
