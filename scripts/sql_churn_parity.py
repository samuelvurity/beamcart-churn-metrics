#!/usr/bin/env python3
import duckdb, pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
SQL_PATH = ROOT / "sql" / "churn_rate.sql"
INTERIM.mkdir(parents=True, exist_ok=True)

csv_events = str(RAW / "events.csv").replace("'", "''")

con = duckdb.connect()
con.execute(f"""
CREATE OR REPLACE VIEW events AS
SELECT user_id,
       CAST(event_ts AS TIMESTAMP) AS event_ts,
       event_type
FROM read_csv_auto('{csv_events}', header=True);
""")

sql = SQL_PATH.read_text()
sql_churn = con.execute(sql).df()  # week_start, active_t_minus_1, churned_users, churn_rate

out_sql = INTERIM / "churn_weekly_sql.csv"
sql_churn.to_csv(out_sql, index=False)

py_churn = pd.read_csv(INTERIM / "churn_weekly.csv", parse_dates=["week_start"])
sql_churn["week_start"] = pd.to_datetime(sql_churn["week_start"])

merged = (py_churn.merge(sql_churn, on="week_start", how="outer", suffixes=("_py","_sql"))
                  .sort_values("week_start"))

# exact matches for counts; ~equal for rate
merged["active_match"] = merged["active_t_minus_1_py"].fillna(-1).eq(merged["active_t_minus_1_sql"].fillna(-1))
merged["churned_match"] = merged["churned_users_py"].fillna(-1).eq(merged["churned_users_sql"].fillna(-1))

def close(a, b, tol=1e-9):
    return (a - b).abs() <= tol

merged["rate_match"] = close(merged["churn_rate_py"], merged["churn_rate_sql"])
merged["all_match"] = merged[["active_match","churned_match","rate_match"]].all(axis=1)

print("DuckDB churn:")
print(sql_churn.to_string(index=False))
print("\nParity vs pandas:")
cols = ["week_start",
        "active_t_minus_1_py","active_t_minus_1_sql",
        "churned_users_py","churned_users_sql",
        "churn_rate_py","churn_rate_sql",
        "active_match","churned_match","rate_match"]
print(merged[cols].to_string(index=False))

if not merged["all_match"].all():
    raise SystemExit("❌ Parity failed. See rows above.")
print("✅ Parity OK")
