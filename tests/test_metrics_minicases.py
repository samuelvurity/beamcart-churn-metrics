import numpy as np
import pandas as pd


# --- Test 1: Refund exclusion & empty-AOV weeks are retained ---
def test_refund_exclusion_keeps_week_and_sets_aov_nan():
    # Week starts: Mon Oct 27 and Mon Nov 3, 2025
    w1 = pd.Timestamp("2025-10-27")
    w2 = pd.Timestamp("2025-11-03")
    # Build tiny orders: week1 = all refunds; week2 = 2 net orders
    orders = pd.DataFrame(
        {
            "order_id": ["o1", "o2", "o3", "o4"],
            "user_id": ["u1", "u2", "u3", "u4"],
            "order_ts": [w1, w1 + pd.Timedelta(days=1), w2, w2 + pd.Timedelta(days=2)],
            "revenue": [30.0, 20.0, 40.0, 60.0],
            "items": [1, 1, 1, 1],
            "is_refund": [1, 1, 0, 0],
        }
    )
    orders["order_ts"] = pd.to_datetime(orders["order_ts"])
    orders["is_refund"] = orders["is_refund"].astype(int)
    orders["week_start"] = (
        orders["order_ts"] - pd.to_timedelta(orders["order_ts"].dt.weekday, unit="D")
    ).dt.normalize()

    grp = orders.groupby("week_start", as_index=False)
    aov_by_week = grp.agg(
        orders_net=("is_refund", lambda s: (s == 0).sum()),
        revenue_net=("revenue", lambda s: s.where(orders.loc[s.index, "is_refund"] == 0, 0).sum()),
    )
    aov_by_week["aov"] = aov_by_week["revenue_net"] / aov_by_week["orders_net"]
    aov = aov_by_week.set_index("week_start")

    # week1 kept, but net orders/revenue = 0 and AOV = NaN
    assert w1 in aov.index
    assert aov.loc[w1, "orders_net"] == 0
    assert aov.loc[w1, "revenue_net"] == 0.0
    assert np.isnan(aov.loc[w1, "aov"])
    # week2 sane
    assert aov.loc[w2, "orders_net"] == 2
    assert aov.loc[w2, "revenue_net"] == 100.0
    assert aov.loc[w2, "aov"] == 50.0


# --- Test 2: Churn is counted at t only for users active in t-1 and missing in t (no double count) ---
def test_weekly_churn_then_return_counts_once():
    # ISO weeks: w1, w2, w3
    w1 = pd.Timestamp("2025-10-27")
    w2 = w1 + pd.Timedelta(days=7)
    w3 = w2 + pd.Timedelta(days=7)

    # Events: u1 active w1 & w3 (churns at w2), u2 active w1 & w2 (churns at w3)
    events = pd.DataFrame(
        {
            "user_id": ["u1", "u2", "u2", "u1"],
            "event_ts": [w1, w1, w2, w3],
            "event_type": ["session_start"] * 4,
        }
    )
    events["event_ts"] = pd.to_datetime(events["event_ts"])
    events["week_start"] = (
        events["event_ts"] - pd.to_timedelta(events["event_ts"].dt.weekday, unit="D")
    ).dt.normalize()
    wk_user = events[events["event_type"] == "session_start"][
        ["user_id", "week_start"]
    ].drop_duplicates()

    weeks = sorted(wk_user["week_start"].unique())
    active = {w: set(wk_user.loc[wk_user["week_start"] == w, "user_id"]) for w in weeks}

    # churn at w2: users active in w1 but not in w2 -> {u1}
    churn_w2 = active[w1] - active.get(w2, set())
    assert churn_w2 == {"u1"}
    # churn at w3: users active in w2 but not in w3 -> {u2}
    churn_w3 = active[w2] - active.get(w3, set())
    assert churn_w3 == {"u2"}


# --- Test 3: D7 retention boundary (any time on D+7 counts; D+8 does not) ---
def test_d7_retention_boundary_includes_entire_day():
    signup = pd.Timestamp("2025-11-01 10:15:00")
    users = pd.DataFrame({"user_id": ["u1", "u2"], "signup_ts": [signup, signup]})
    # u1 returns at D+7 00:00 and 23:59; u2 returns at D+8
    events = pd.DataFrame(
        {
            "user_id": ["u1", "u1", "u2"],
            "event_ts": [
                signup.normalize() + pd.Timedelta(days=7),  # D+7 00:00
                (
                    signup.normalize() + pd.Timedelta(days=7) + pd.Timedelta(hours=23, minutes=59)
                ),  # D+7 23:59
                signup.normalize() + pd.Timedelta(days=8),  # D+8
            ],
            "event_type": ["session_start", "session_start", "session_start"],
        }
    )
    users["signup_date"] = pd.to_datetime(users["signup_ts"]).dt.normalize()
    sess = events[events["event_type"] == "session_start"].copy()
    sess["event_day"] = pd.to_datetime(sess["event_ts"]).dt.normalize()

    cohort = (
        users.groupby("signup_date", as_index=False)["user_id"]
        .nunique()
        .rename(columns={"user_id": "cohort_size"})
    )
    ue = users[["user_id", "signup_date"]].merge(
        sess[["user_id", "event_day"]], on="user_id", how="left"
    )
    ue["is_d7"] = ue["event_day"] == (ue["signup_date"] + pd.to_timedelta(7, "D"))
    d7 = (
        ue.loc[ue["is_d7"]]
        .groupby("signup_date", as_index=False)["user_id"]
        .nunique()
        .rename(columns={"user_id": "d7_users"})
    )
    out = cohort.merge(d7, on="signup_date", how="left").fillna({"d7_users": 0})
    # 2 users in cohort; only u1 qualifies → d7_users = 1, rate = 0.5
    assert int(out.loc[0, "cohort_size"]) == 2
    assert int(out.loc[0, "d7_users"]) == 1
    assert float(out.loc[0, "d7_users"] / out.loc[0, "cohort_size"]) == 0.5
