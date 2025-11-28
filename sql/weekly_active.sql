-- WAU from an `events` table with columns: user_id, event_ts (TIMESTAMP), event_type
WITH sess AS (
  SELECT
    user_id,
    DATE_TRUNC('week', event_ts) AS week_start
  FROM events
  WHERE event_type = 'session_start'
)
SELECT
  week_start,
  COUNT(DISTINCT user_id) AS wau
FROM sess
GROUP BY 1
ORDER BY 1;
