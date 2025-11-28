-- Cohort retention by signup_date with D1/D7/D30 (calendar-day windows, UTC)
-- expects:
--   users(user_id, signup_ts)
--   events(user_id, event_ts, event_type)
WITH cohorts AS (
  SELECT
    user_id,
    DATE_TRUNC('day', CAST(signup_ts AS TIMESTAMP)) AS signup_date
  FROM users
),
hits AS (
  SELECT
    user_id,
    DATE_TRUNC('day', CAST(event_ts AS TIMESTAMP)) AS event_day
  FROM events
  WHERE event_type = 'session_start'
),
joined AS (
  SELECT
    c.signup_date,
    c.user_id,
    h.event_day
  FROM cohorts c
  LEFT JOIN hits h USING (user_id)
),
agg AS (
  SELECT
    signup_date,
    COUNT(DISTINCT user_id)                                  AS cohort_size,
    COUNT(DISTINCT CASE WHEN event_day = signup_date + INTERVAL 1 DAY  THEN user_id END) AS d1_users,
    COUNT(DISTINCT CASE WHEN event_day = signup_date + INTERVAL 7 DAY  THEN user_id END) AS d7_users,
    COUNT(DISTINCT CASE WHEN event_day = signup_date + INTERVAL 30 DAY THEN user_id END) AS d30_users
  FROM joined
  GROUP BY 1
)
SELECT
  signup_date,
  cohort_size,
  1.0 * d1_users  / NULLIF(cohort_size,0) AS d1_retention,
  1.0 * d7_users  / NULLIF(cohort_size,0) AS d7_retention,
  1.0 * d30_users / NULLIF(cohort_size,0) AS d30_retention
FROM agg
ORDER BY 1;
