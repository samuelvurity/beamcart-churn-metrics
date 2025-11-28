-- AOV by ISO week, excluding refunded orders
-- expects a table/view `orders(order_id, user_id, order_ts, revenue, items, is_refund)`

WITH o AS (
  SELECT
    DATE_TRUNC('week', CAST(order_ts AS TIMESTAMP)) AS week_start,
    order_id,
    CAST(revenue AS DOUBLE) AS revenue,
    CAST(is_refund AS INTEGER) AS is_refund
  FROM orders
),
nr AS (
  SELECT
    week_start,
    COUNT(*) FILTER (WHERE is_refund = 0) AS orders_net,
    SUM(CASE WHEN is_refund = 0 THEN revenue ELSE 0 END) AS revenue_net
  FROM o
  GROUP BY 1
)
SELECT
  week_start,
  orders_net,
  revenue_net,
  revenue_net / NULLIF(orders_net, 0) AS aov
FROM nr
ORDER BY 1;
