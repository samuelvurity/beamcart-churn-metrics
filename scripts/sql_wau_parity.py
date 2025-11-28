#!/usr/bin/env python3
import duckdb, pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
SQL_PATH = ROOT / "sql" / "weekly_active.sql"
INTERIM.mkdir(parents=True, exist_ok=True)

# Read CSV via DuckDB; escape single quotes in the path for SQL literal
csv_events = str(RAW / "events.csv").replace("'", "''")

con = duckdb.connect()
con.execute(f"""
CREATE OR REPLACE VIEW events AS
SELECT
  user_id,
  CAST(event_ts AS TIMESTAMP) AS event_ts,
  event_type
FROM read_csv_auto('{csv_events}', header=True);
""")

sql = SQL_PATH.read_text()
sql_wau = con.execute(sql).df()  # columns: week_start (TIMESTAMP), wau (INT)

# Save DuckDB result
out_sql = INTERIM / "wau_by_week_sql.csv"
sql_wau.to_csv(out_sql, index=False)

# Load pandas result from Step 9
py_wau = pd.read_csv(INTERIM / "wau_by_week.csv", parse_dates=["week_start"])
sql_wau["week_start"] = pd.to_datetime(sql_wau["week_start"])

merged = (py_wau.merge(sql_wau, on="week_start", how="outer", suffixes=("_py", "_sql"))
                 .sort_values("week_start"))
merged["match"] = merged["wau_py"].fillna(-1).eq(merged["wau_sql"].fillna(-1))

print("DuckDB WAU:")
print(sql_wau.to_string(index=False))
print("\nParity vs pandas:")
print(merged.to_string(index=False))

if not merged["match"].all():
    raise SystemExit("❌ Parity failed. See rows above.")
print("✅ Parity OK")
