# Metrics Definitions — minimal (v0)

**Timezone:** UTC  
**Week grain:** ISO week (Mon–Sun, UTC)  
**Event of interest:** `session_start`  
**Refund policy:** Exclude `is_refund = 1` from revenue and order counts; track refund rate as a guardrail.

**Schemas (CSV)**
- users(user_id, signup_ts, country, acquisition_channel)
- events(user_id, event_ts, event_type ∈ {session_start, view, add_to_cart, purchase})
- orders(order_id, user_id, order_ts, revenue, items, is_refund)

**One-line metric contracts**
- Activation: user has ≥1 `session_start` within 7 days of signup.
- WAU/MAU/DAU: distinct users with ≥1 `session_start` in the week/month/day.
- Weekly churn: active in week t−1, not active in week t.
- Retention D1/D7/D30: % of signup-day cohort with a `session_start` on D+1/D+7/D+30.
- AOV: sum(revenue) / count(orders where is_refund=0).
- OPAC: orders(where is_refund=0) / WAU.
- Guardrail: Refund rate = refunds / all orders (target ≤ 6%).
