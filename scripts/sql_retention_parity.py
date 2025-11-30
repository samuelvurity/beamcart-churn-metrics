#!/usr/bin/env python3
import duckdb
import pandas as pd
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
SQL_PATH = ROOT / "sql" / "cohort_retention.sql"
INTERIM.mkdir(parents=True, exist_ok=True)

csv_users = str(RAW / "users.csv").replace("'", "''")
csv_events = str(RAW / "events.csv").replace("'", "''")

con = duckdb.connect()
con.execute(
    f"""
CREATE OR REPLACE VIEW users AS
SELECT user_id,
       CAST(signup_ts AS TIMESTAMP) AS signup_ts,
       country,
       acquisition_channel
FROM read_csv_auto('{csv_users}', header=True);
"""
)
con.execute(
    f"""
CREATE OR REPLACE VIEW events AS
SELECT user_id,
       CAST(event_ts AS TIMESTAMP) AS event_ts,
       event_type
FROM read_csv_auto('{csv_events}', header=True);
"""
)

sql = SQL_PATH.read_text()
sql_ret = con.execute(
    sql
).df()  # signup_date, cohort_size, d1_retention, d7_retention, d30_retention
sql_ret["signup_date"] = pd.to_datetime(sql_ret["signup_date"])

# save for reference
(sql_ret.sort_values("signup_date").to_csv(INTERIM / "retention_summary_sql.csv", index=False))

# pandas version
py_ret = pd.read_csv(INTERIM / "retention_summary.csv", parse_dates=["signup_date"])

merged = py_ret.merge(sql_ret, on="signup_date", suffixes=("_py", "_sql")).sort_values(
    "signup_date"
)


def close(a, b, rtol=1e-9, atol=1e-12):
    return np.isclose(a, b, rtol=rtol, atol=atol)


merged["d1_match"] = close(merged["d1_retention_py"], merged["d1_retention_sql"])
merged["d7_match"] = close(merged["d7_retention_py"], merged["d7_retention_sql"])
merged["d30_match"] = close(merged["d30_retention_py"], merged["d30_retention_sql"])

print("DuckDB retention:")
print(
    sql_ret.to_string(
        index=False,
        formatters={
            "d1_retention": "{:.4f}".format,
            "d7_retention": "{:.4f}".format,
            "d30_retention": "{:.4f}".format,
        },
    )
)
print("\nParity vs pandas:")
cols = [
    "signup_date",
    "cohort_size_py",
    "cohort_size_sql",
    "d1_retention_py",
    "d1_retention_sql",
    "d1_match",
    "d7_retention_py",
    "d7_retention_sql",
    "d7_match",
    "d30_retention_py",
    "d30_retention_sql",
    "d30_match",
]
# cohort_size_py column name may not exist if not in summary; bring from d1 csv if needed
if "cohort_size_py" not in merged.columns:
    # fall back: pull cohort_size from retention_d1.csv
    d1 = pd.read_csv(INTERIM / "retention_d1.csv", parse_dates=["signup_date"])
    merged = merged.merge(
        d1[["signup_date", "cohort_size"]].rename(columns={"cohort_size": "cohort_size_py"}),
        on="signup_date",
        how="left",
    )
print(merged[cols].to_string(index=False))

if not (merged["d1_match"] & merged["d7_match"] & merged["d30_match"]).all():
    raise SystemExit("❌ Parity failed. See rows above.")
print("✅ Parity OK")
