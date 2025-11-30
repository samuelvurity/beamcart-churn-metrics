-- OPAC by channel per ISO week, refunds excluded
WITH wau AS (
  SELECT
    DATE_TRUNC('week', CAST(e.event_ts AS TIMESTAMP)) AS week_start,
    u.acquisition_channel,
    COUNT(DISTINCT e.user_id) AS wau
  FROM events e
  JOIN users u USING (user_id)
  WHERE e.event_type = 'session_start'
  GROUP BY 1, 2
),
ord AS (
  SELECT
    DATE_TRUNC('week', CAST(o.order_ts AS TIMESTAMP)) AS week_start,
    u.acquisition_channel,
    COUNT(*) FILTER (WHERE CAST(o.is_refund AS INTEGER) = 0) AS orders_net,
    SUM(CASE WHEN CAST(o.is_refund AS INTEGER) = 0
             THEN CAST(o.revenue AS DOUBLE) ELSE 0 END) AS revenue_net
  FROM orders o
  JOIN users u USING (user_id)
  GROUP BY 1, 2
)
SELECT
  COALESCE(w.week_start, o.week_start) AS week_start,
  COALESCE(w.acquisition_channel, o.acquisition_channel) AS acquisition_channel,
  COALESCE(w.wau, 0) AS wau,
  COALESCE(o.orders_net, 0) AS orders_net,
  COALESCE(o.revenue_net, 0) AS revenue_net,
  1.0 * COALESCE(o.orders_net, 0) / NULLIF(COALESCE(w.wau, 0), 0) AS opac
FROM wau w
FULL OUTER JOIN ord o
ON w.week_start = o.week_start AND w.acquisition_channel = o.acquisition_channel
ORDER BY 1, 2;
