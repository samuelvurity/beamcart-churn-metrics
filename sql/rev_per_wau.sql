-- Revenue per WAU (weekly), refunds excluded
WITH wau AS (
  SELECT
    DATE_TRUNC('week', CAST(event_ts AS TIMESTAMP)) AS week_start,
    COUNT(DISTINCT user_id) AS wau
  FROM events
  WHERE event_type = 'session_start'
  GROUP BY 1
),
rev AS (
  SELECT
    DATE_TRUNC('week', CAST(order_ts AS TIMESTAMP)) AS week_start,
    SUM(CASE WHEN CAST(is_refund AS INTEGER) = 0
             THEN CAST(revenue AS DOUBLE) ELSE 0 END) AS revenue_net
  FROM orders
  GROUP BY 1
)
SELECT
  w.week_start,
  w.wau,
  COALESCE(r.revenue_net, 0) AS revenue_net,
  1.0 * COALESCE(r.revenue_net, 0) / NULLIF(w.wau, 0) AS rev_per_wau
FROM wau w
LEFT JOIN rev r USING (week_start)
ORDER BY 1;
