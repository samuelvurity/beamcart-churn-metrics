## North-Star (v0)
**OPAC — Orders per Active Customer (weekly).**
*Why:* It’s an actionable, leading metric—lifting order frequency via product & lifecycle levers moves revenue quickly and decomposes cleanly as Revenue ≈ WAU × OPAC × AOV (net of refunds).

## First Experiment (v0)
- **Lever:** “Continue your cart” sticky card + 2-item bundle on Home.
- **Audience:** Activated WAU (users with ≥1 session within 7 days of signup).
- **Target:** +5% OPAC vs control over 2 weeks; **guardrail:** refund_rate ≤ 6%.
- **Design:** 50/50 user-level holdout; cap notifications; revenue/AOV net of refunds; ISO-week attribution (UTC).
- **Readout:** OPAC (primary), Rev/WAU + AOV (secondary), WAU context; cut by acquisition_channel & country; spot-check D1/D7.
- **Ship rule:** Ship if OPAC lift ≥ +5% and guardrail holds; else pivot to size-finder UX test to reduce refunds.
