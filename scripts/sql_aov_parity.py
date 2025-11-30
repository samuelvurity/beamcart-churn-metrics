#!/usr/bin/env python3
import duckdb
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
SQL_PATH = ROOT / "sql" / "aov_by_week.sql"
INTERIM.mkdir(parents=True, exist_ok=True)

# Read CSV via DuckDB; escape single quotes in the path for SQL literal
csv_orders = str(RAW / "orders.csv").replace("'", "''")

con = duckdb.connect()
con.execute(
    f"""
CREATE OR REPLACE VIEW orders AS
SELECT
  order_id,
  user_id,
  CAST(order_ts AS TIMESTAMP) AS order_ts,
  CAST(revenue AS DOUBLE) AS revenue,
  CAST(items AS INTEGER) AS items,
  CAST(is_refund AS INTEGER) AS is_refund
FROM read_csv_auto('{csv_orders}', header=True);
"""
)

sql = SQL_PATH.read_text()
sql_aov = con.execute(sql).df()  # week_start, orders_net, revenue_net, aov

# Save DuckDB result
out_sql = INTERIM / "aov_by_week_sql.csv"
sql_aov.to_csv(out_sql, index=False)

# Load pandas result from Step 9
py_aov = pd.read_csv(INTERIM / "aov_by_week.csv", parse_dates=["week_start"])
sql_aov["week_start"] = pd.to_datetime(sql_aov["week_start"])

merged = py_aov.merge(sql_aov, on="week_start", how="outer", suffixes=("_py", "_sql")).sort_values(
    "week_start"
)


def close(a, b, rtol=1e-6, atol=1e-9):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    return np.isclose(a, b, rtol=rtol, atol=atol) | (pd.isna(a) & pd.isna(b))


merged["orders_match"] = merged["orders_net_py"].fillna(-1).astype(float) == merged[
    "orders_net_sql"
].fillna(-1).astype(float)
merged["revenue_match"] = close(merged["revenue_net_py"], merged["revenue_net_sql"])
merged["aov_match"] = close(merged["aov_py"], merged["aov_sql"])
merged["all_match"] = merged[["orders_match", "revenue_match", "aov_match"]].all(axis=1)

print("DuckDB AOV:")
print(sql_aov.to_string(index=False))
print("\nParity vs pandas:")
cols = [
    "week_start",
    "orders_net_py",
    "orders_net_sql",
    "revenue_net_py",
    "revenue_net_sql",
    "aov_py",
    "aov_sql",
    "orders_match",
    "revenue_match",
    "aov_match",
]
print(merged[cols].to_string(index=False))

if not merged["all_match"].all():
    raise SystemExit("❌ Parity failed. See rows above.")
print("✅ Parity OK")
