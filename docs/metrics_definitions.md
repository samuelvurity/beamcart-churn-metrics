# Metrics Definitions

- **Timezone:** UTC
- **ISO week start:** Monday

Revenue/AOV/OPAC are net of refunds. All cohort windows use calendar days in UTC.

### WAU

- **Grain:** week (ISO)
- **Window:** per ISO week
- **Business intent:** Weekly reach of active customers
- **Definition:** Count distinct users with ≥1 session_start in the ISO week
- **Inclusion/exclusion:** Exclude bots if flagged; sessions only (not views)
- **Formula:** `WAU = COUNT_DISTINCT(user_id WHERE session_start within week)`
- **SQL:** sql/weekly_active.sql
- **Segments:** acquisition_channel, country
- **Guardrails:** —
- **Edge cases:** Weeks with zero sessions (0 WAU)

### MAU

- **Grain:** month (calendar)
- **Window:** per calendar month
- **Business intent:** Monthly reach of active customers
- **Definition:** Count distinct users with ≥1 session_start in the month
- **Inclusion/exclusion:** Exclude bots if flagged; sessions only
- **Formula:** `MAU = COUNT_DISTINCT(user_id WHERE session_start within month)`
- **SQL:** (computed in pandas)
- **Segments:** acquisition_channel, country
- **Guardrails:** —
- **Edge cases:** Months truncated at dataset boundaries

### AOV

- **Grain:** week (ISO)
- **Window:** per ISO week
- **Business intent:** Average order value, net of refunds
- **Definition:** Net revenue divided by net orders, excluding refunded orders
- **Inclusion/exclusion:** Exclude is_refund=1 from both revenue and order counts
- **Formula:** `AOV = SUM(revenue WHERE not refunded) / COUNT(orders WHERE not refunded)`
- **SQL:** sql/aov_by_week.sql
- **Segments:** —
- **Guardrails:** refund_rate
- **Edge cases:** Weeks with only refunds → orders_net=0 → AOV = NaN

### OPAC

- **Grain:** week (ISO)
- **Window:** per ISO week
- **Business intent:** Order frequency per active customer
- **Definition:** Net orders divided by WAU
- **Inclusion/exclusion:** Exclude refunded orders from numerator
- **Formula:** `OPAC = orders_net / WAU`
- **SQL:** sql/opac_by_week.sql
- **Segments:** acquisition_channel, country
- **Guardrails:** refund_rate
- **Edge cases:** WAU=0 → OPAC undefined → treat as 0 in charts

### Rev/WAU

- **Grain:** week (ISO)
- **Window:** per ISO week
- **Business intent:** Monetization per active customer
- **Definition:** Net revenue divided by WAU
- **Inclusion/exclusion:** Exclude refunded orders from revenue
- **Formula:** `Rev/WAU = revenue_net / WAU`
- **SQL:** sql/rev_per_wau.sql
- **Segments:** acquisition_channel, country
- **Guardrails:** refund_rate
- **Edge cases:** WAU=0 → undefined → show 0 in charts

### Retention D1

- **Grain:** day (cohort)
- **Window:** calendar
- **Business intent:** Next-day habit signal
- **Definition:** Percentage of signup-day users who return with a session_start on D+1 (UTC)
- **Inclusion/exclusion:** Session_start only; calendar-day compare
- **Formula:** `d1 = users_with_session_on(signup_date+1) / cohort_size`
- **SQL:** sql/cohort_retention.sql
- **Segments:** —
- **Guardrails:** —
- **Edge cases:** Sparse cohorts → keep zeros

### Retention D7

- **Grain:** day (cohort)
- **Window:** calendar
- **Business intent:** Week-later habit signal
- **Definition:** Percentage of signup-day users who return on D+7 (UTC)
- **Inclusion/exclusion:** Session_start only
- **Formula:** `d7 = users_with_session_on(signup_date+7) / cohort_size`
- **SQL:** sql/cohort_retention.sql
- **Segments:** —
- **Guardrails:** —
- **Edge cases:** Include entire D+7 day (00:00–23:59 UTC)

### Retention D30

- **Grain:** day (cohort)
- **Window:** calendar
- **Business intent:** 30-day habit signal
- **Definition:** Percentage of signup-day users who return on D+30 (UTC)
- **Inclusion/exclusion:** Session_start only
- **Formula:** `d30 = users_with_session_on(signup_date+30) / cohort_size`
- **SQL:** sql/cohort_retention.sql
- **Segments:** —
- **Guardrails:** —
- **Edge cases:** Early cohorts only have measurable D30

### Churn (weekly)

- **Grain:** week (ISO)
- **Window:** rolling week to week
- **Business intent:** Drop-off of actives
- **Definition:** Users active in week t-1 but not active in week t
- **Inclusion/exclusion:** Session_start-based activeness
- **Formula:** `churn_rate_t = churned_users_t / active_t_minus_1`
- **SQL:** sql/churn_rate.sql
- **Segments:** —
- **Guardrails:** —
- **Edge cases:** Skip first observed week (no t-1)

### Refund rate

- **Grain:** week (ISO)
- **Window:** per ISO week
- **Business intent:** Quality guardrail
- **Definition:** refund_orders / all_orders
- **Inclusion/exclusion:** Count all refunded vs total orders
- **Formula:** `refund_rate = refund_orders / all_orders`
- **SQL:** (pandas)
- **Segments:** —
- **Guardrails:** —
- **Edge cases:** Weeks with zero orders → NaN
