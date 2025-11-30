#!/usr/bin/env python3
import duckdb
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
SQL_PATH = ROOT / "sql" / "rev_per_wau.sql"
INTERIM.mkdir(parents=True, exist_ok=True)

csv_events = str(RAW / "events.csv").replace("'", "''")
csv_orders = str(RAW / "orders.csv").replace("'", "''")

con = duckdb.connect()
con.execute(
    f"""
CREATE OR REPLACE VIEW events AS
SELECT user_id, CAST(event_ts AS TIMESTAMP) AS event_ts, event_type
FROM read_csv_auto('{csv_events}', header=True);
"""
)
con.execute(
    f"""
CREATE OR REPLACE VIEW orders AS
SELECT order_id, user_id, CAST(order_ts AS TIMESTAMP) AS order_ts,
       CAST(revenue AS DOUBLE) AS revenue, CAST(items AS INTEGER) AS items,
       CAST(is_refund AS INTEGER) AS is_refund
FROM read_csv_auto('{csv_orders}', header=True);
"""
)

sql = SQL_PATH.read_text()
sql_df = con.execute(sql).df()  # week_start, wau, revenue_net, rev_per_wau
sql_df["week_start"] = pd.to_datetime(sql_df["week_start"])

py_df = pd.read_csv(INTERIM / "rev_per_wau.csv", parse_dates=["week_start"]).sort_values(
    "week_start"
)

m = py_df.merge(sql_df, on="week_start", how="outer", suffixes=("_py", "_sql")).sort_values(
    "week_start"
)


def close(a, b, rtol=1e-9, atol=1e-12):
    return np.isclose(a, b, rtol=rtol, atol=atol)


m["wau_match"] = m["wau_py"].fillna(-1) == m["wau_sql"].fillna(-1)
m["revenue_match"] = close(m["revenue_net_py"], m["revenue_net_sql"])
m["rpw_match"] = close(m["rev_per_wau_py"], m["rev_per_wau_sql"])
m["all_match"] = m[["wau_match", "revenue_match", "rpw_match"]].all(axis=1)

print("DuckDB Rev/WAU:")
print(sql_df.to_string(index=False, formatters={"rev_per_wau": "{:.2f}".format}))
print("\nParity vs pandas:")
cols = [
    "week_start",
    "wau_py",
    "wau_sql",
    "revenue_net_py",
    "revenue_net_sql",
    "rev_per_wau_py",
    "rev_per_wau_sql",
    "wau_match",
    "revenue_match",
    "rpw_match",
]
print(m[cols].to_string(index=False))

if not m["all_match"].all():
    raise SystemExit("❌ Parity failed.")
print("✅ Parity OK")
