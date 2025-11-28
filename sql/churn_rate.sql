-- Weekly churn: users active in week t-1 but not in week t
-- expects `events(user_id, event_ts, event_type)`

WITH ua AS (
  SELECT
    user_id,
    DATE_TRUNC('week', CAST(event_ts AS TIMESTAMP)) AS week_start
  FROM events
  WHERE event_type = 'session_start'
  GROUP BY 1,2
),
weeks AS (
  SELECT DISTINCT week_start FROM ua
),
-- Only evaluate weeks that have a prior active week (skip the first observed week)
eval_weeks AS (
  SELECT w.week_start
  FROM weeks w
  JOIN weeks pw ON pw.week_start = w.week_start - INTERVAL 7 DAY
),
churn_calc AS (
  SELECT
    ew.week_start,
    COUNT(DISTINCT prev.user_id) AS active_t_minus_1,
    COUNT(DISTINCT prev.user_id) FILTER (WHERE cur.user_id IS NULL) AS churned_users
  FROM eval_weeks ew
  LEFT JOIN ua prev
         ON prev.week_start = ew.week_start - INTERVAL 7 DAY
  LEFT JOIN ua cur
         ON cur.user_id = prev.user_id
        AND cur.week_start = ew.week_start
  GROUP BY 1
)
SELECT
  week_start,
  active_t_minus_1,
  churned_users,
  1.0 * churned_users / NULLIF(active_t_minus_1, 0) AS churn_rate
FROM churn_calc
ORDER BY 1;
