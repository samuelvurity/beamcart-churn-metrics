-- OPAC by ISO week, excluding refunds
-- expects views/tables:
--   events(user_id, event_ts, event_type)
--   orders(order_id, user_id, order_ts, revenue, items, is_refund)

WITH wau AS (
  SELECT
    DATE_TRUNC('week', CAST(event_ts AS TIMESTAMP)) AS week_start,
    COUNT(DISTINCT user_id) AS wau
  FROM events
  WHERE event_type = 'session_start'
  GROUP BY 1
),
ord AS (
  SELECT
    DATE_TRUNC('week', CAST(order_ts AS TIMESTAMP)) AS week_start,
    COUNT(*) FILTER (WHERE CAST(is_refund AS INTEGER) = 0) AS orders_net,
    SUM(CASE WHEN CAST(is_refund AS INTEGER) = 0
             THEN CAST(revenue AS DOUBLE) ELSE 0 END) AS revenue_net
  FROM orders
  GROUP BY 1
)
SELECT
  w.week_start,
  w.wau,
  COALESCE(o.orders_net, 0) AS orders_net,
  COALESCE(o.revenue_net, 0) AS revenue_net,
  1.0 * COALESCE(o.orders_net, 0) / NULLIF(w.wau, 0) AS opac
FROM wau w
LEFT JOIN ord o USING (week_start)
ORDER BY 1;
