#!/usr/bin/env python3
"""
BeamCart big seed (deterministic):
- ~10k users over 10 ISO weeks
- Weekend session bump, 2 promo weeks (↑ sessions & purchase), 1 refund spike week
- Writes users_big.csv, events_big.csv, orders_big.csv in data/raw/
"""
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# --- params (tweakable) ---
SEED = 42
N_USERS = 10_000
WEEKS = 10
BASE_MON = datetime(2025, 10, 27)  # Monday, ISO-week start
PROMO_WEEK_IDX = [2, 6]  # 0-based indices into week list
REFUND_SPIKE_IDX = 3  # one week with high refunds
LAMBDA_SESS = 1.2  # avg sessions per user-week (Poisson)
PURCHASE_P = 0.25  # per-session purchase probability
WEEKEND_BUMP = 1.4  # relative weight for Sat/Sun session timing
PROMO_SESS_MULT = 1.5  # sessions increase in promo weeks
PROMO_PURCHASE_MULT = 1.2  # purchase prob increase in promo weeks
REFUND_BASE = 0.06  # baseline refund prob
REFUND_SPIKE = 0.20  # refund prob in spike week

# --- setup ---
np.random.seed(SEED)
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

# --- week grid ---
weeks = [BASE_MON + timedelta(days=7 * i) for i in range(WEEKS)]
is_promo = np.array([i in PROMO_WEEK_IDX for i in range(WEEKS)], dtype=bool)
is_refund_spike = np.array([i == REFUND_SPIKE_IDX for i in range(WEEKS)], dtype=bool)

# --- users ---
countries = np.array(["US", "IN", "CA", "UK"])
p_c = np.array([0.5, 0.2, 0.2, 0.1])

channels = np.array(["paid", "organic", "email", "referral"])
p_ch = np.array([0.35, 0.35, 0.15, 0.15])

user_id = np.array([f"u{i+1}" for i in range(N_USERS)])

# signup dates uniform across the 10 weeks
signup_offsets_days = np.random.randint(0, 7 * WEEKS, size=N_USERS)
signup_ts = np.array(
    [
        BASE_MON
        + timedelta(days=int(d), hours=np.random.randint(0, 24), minutes=np.random.randint(0, 60))
        for d in signup_offsets_days
    ]
)

user_country = np.random.choice(countries, size=N_USERS, p=p_c)
user_channel = np.random.choice(channels, size=N_USERS, p=p_ch)

df_users = pd.DataFrame(
    {
        "user_id": user_id,
        "signup_ts": pd.to_datetime(signup_ts).strftime("%Y-%m-%d %H:%M:%S"),
        "country": user_country,
        "acquisition_channel": user_channel,
    }
)

# --- helper to draw event times with weekend bump ---
dow_weights = np.array([1, 1, 1, 1, 1, WEEKEND_BUMP, WEEKEND_BUMP], dtype=float)
dow_prob = dow_weights / dow_weights.sum()


def sample_times_in_week(w_start: datetime, n: int):
    if n <= 0:
        return []
    dows = np.random.choice(np.arange(7), size=n, p=dow_prob)
    hours = np.random.randint(0, 24, size=n)
    mins = np.random.randint(0, 60, size=n)
    return [
        w_start + timedelta(days=int(d), hours=int(h), minutes=int(m))
        for d, h, m in zip(dows, hours, mins)
    ]


# --- events (session_start only for simplicity) + orders ---
events_rows, orders_rows = [], []

for uid, s_ts in zip(user_id, pd.to_datetime(signup_ts)):
    signup_week_start = s_ts - timedelta(days=s_ts.weekday())
    for wi, w_start in enumerate(weeks):
        if w_start < signup_week_start:
            continue
        lam = LAMBDA_SESS * (PROMO_SESS_MULT if is_promo[wi] else 1.0)
        n_sessions = np.random.poisson(lam)
        if n_sessions <= 0:
            continue
        sess_times = sample_times_in_week(w_start, n_sessions)
        for t in sess_times:
            events_rows.append((uid, t.strftime("%Y-%m-%d %H:%M:%S"), "session_start"))
            p_buy = PURCHASE_P * (PROMO_PURCHASE_MULT if is_promo[wi] else 1.0)
            if np.random.rand() < p_buy:
                revenue = float(np.round(np.random.lognormal(mean=np.log(35), sigma=0.35), 2))
                items = int(np.random.choice([1, 2, 3], p=[0.7, 0.25, 0.05]))
                refund_p = REFUND_SPIKE if is_refund_spike[wi] else REFUND_BASE
                is_refund = int(np.random.rand() < refund_p)
                order_id = f"o{len(orders_rows)+1}"
                orders_rows.append(
                    (order_id, uid, t.strftime("%Y-%m-%d %H:%M:%S"), revenue, items, is_refund)
                )

df_events = pd.DataFrame(events_rows, columns=["user_id", "event_ts", "event_type"])
df_orders = pd.DataFrame(
    orders_rows, columns=["order_id", "user_id", "order_ts", "revenue", "items", "is_refund"]
)

# write
users_path = RAW / "users_big.csv"
events_path = RAW / "events_big.csv"
orders_path = RAW / "orders_big.csv"
df_users.to_csv(users_path, index=False)
df_events.to_csv(events_path, index=False)
df_orders.to_csv(orders_path, index=False)

print("✅ Wrote big synthetic CSVs:")
print(f"  users_big.csv   : {len(df_users):,} rows")
print(f"  events_big.csv  : {len(df_events):,} rows  (session_start only)")
print(f"  orders_big.csv  : {len(df_orders):,} rows")

# quick weekly sanity
df_events["event_ts"] = pd.to_datetime(df_events["event_ts"])
df_events["week_start"] = (
    df_events["event_ts"] - pd.to_timedelta(df_events["event_ts"].dt.weekday, unit="D")
).dt.normalize()
wk = df_events.groupby("week_start")["user_id"].nunique().rename("WAU").reset_index()
print("\nWAU (first 5 weeks):")
print(wk.head().to_string(index=False))
