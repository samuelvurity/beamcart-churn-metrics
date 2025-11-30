#!/usr/bin/env python3
"""
BeamCart minimal seed — tiny, deterministic CSVs (UTC) just to unblock WAU/AOV/retention.
Generates a few users across 3 ISO weeks with session_start events and a couple orders (one refund).
"""

import csv
import os
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(__file__))
RAW = os.path.join(ROOT, "data", "raw")
os.makedirs(RAW, exist_ok=True)


# Helper to write rows
def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


# Base Monday (ISO week): 2025-10-27 is a Monday (UTC)
BASE = datetime(2025, 10, 27, 0, 0, 0)  # Mon

# Users: spread signups across weeks
users = [
    # user_id, signup_ts, country, acquisition_channel
    ("u1", (BASE + timedelta(days=0, hours=9)).strftime("%Y-%m-%d %H:%M:%S"), "US", "paid"),
    ("u2", (BASE + timedelta(days=3, hours=11)).strftime("%Y-%m-%d %H:%M:%S"), "US", "organic"),
    ("u3", (BASE + timedelta(days=7, hours=8)).strftime("%Y-%m-%d %H:%M:%S"), "IN", "referral"),
    ("u4", (BASE + timedelta(days=10, hours=10)).strftime("%Y-%m-%d %H:%M:%S"), "CA", "paid"),
    ("u5", (BASE + timedelta(days=14, hours=9)).strftime("%Y-%m-%d %H:%M:%S"), "US", "email"),
]

# Events: session_start across 3 ISO weeks to enable WAU/churn/retention
S = "session_start"
events = [
    # user_id, event_ts, event_type
    ("u1", (BASE + timedelta(days=0, hours=10)).strftime("%Y-%m-%d %H:%M:%S"), S),  # week 1
    ("u1", (BASE + timedelta(days=7, hours=9)).strftime("%Y-%m-%d %H:%M:%S"), S),  # week 2
    ("u1", (BASE + timedelta(days=14, hours=11)).strftime("%Y-%m-%d %H:%M:%S"), S),  # week 3
    ("u2", (BASE + timedelta(days=4, hours=12)).strftime("%Y-%m-%d %H:%M:%S"), S),  # week 1
    (
        "u2",
        (BASE + timedelta(days=12, hours=12)).strftime("%Y-%m-%d %H:%M:%S"),
        S,
    ),  # week 2 (churns after)
    ("u3", (BASE + timedelta(days=7, hours=8)).strftime("%Y-%m-%d %H:%M:%S"), S),  # week 2
    ("u3", (BASE + timedelta(days=8, hours=9)).strftime("%Y-%m-%d %H:%M:%S"), S),  # week 2 extra
    ("u3", (BASE + timedelta(days=14, hours=9)).strftime("%Y-%m-%d %H:%M:%S"), S),  # week 3
    (
        "u4",
        (BASE + timedelta(days=11, hours=12)).strftime("%Y-%m-%d %H:%M:%S"),
        S,
    ),  # week 2 only (then churn)
    # u4 no week 3
    (
        "u5",
        (BASE + timedelta(days=15, hours=10)).strftime("%Y-%m-%d %H:%M:%S"),
        S,
    ),  # week 3 (activated within 7d)
]

# Orders: include one refund to test guardrail; exclude refunds in AOV/OPAC
orders = [
    # order_id, user_id, order_ts, revenue, items, is_refund
    (
        "o1",
        "u1",
        (BASE + timedelta(days=7, hours=12, minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
        40.00,
        1,
        0,
    ),
    (
        "o2",
        "u2",
        (BASE + timedelta(days=4, hours=12, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
        35.00,
        1,
        1,
    ),  # refund
    ("o3", "u3", (BASE + timedelta(days=8, hours=10)).strftime("%Y-%m-%d %H:%M:%S"), 55.00, 2, 0),
    (
        "o4",
        "u4",
        (BASE + timedelta(days=11, hours=13, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
        20.00,
        1,
        0,
    ),
    ("o5", "u1", (BASE + timedelta(days=14, hours=13)).strftime("%Y-%m-%d %H:%M:%S"), 42.00, 1, 0),
    (
        "o6",
        "u3",
        (BASE + timedelta(days=14, hours=13, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
        30.00,
        1,
        0,
    ),
]

write_csv(
    os.path.join(RAW, "users.csv"),
    ["user_id", "signup_ts", "country", "acquisition_channel"],
    users,
)

write_csv(os.path.join(RAW, "events.csv"), ["user_id", "event_ts", "event_type"], events)

write_csv(
    os.path.join(RAW, "orders.csv"),
    ["order_id", "user_id", "order_ts", "revenue", "items", "is_refund"],
    orders,
)

print("✅ Wrote:")
print(f"  users.csv   : {len(users)} rows")
print(f"  events.csv  : {len(events)} rows")
print(f"  orders.csv  : {len(orders)} rows")
print("Dates are UTC-like strings (YYYY-MM-DD HH:MM:SS). ISO weeks start Monday.")
