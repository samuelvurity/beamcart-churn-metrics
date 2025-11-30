#!/usr/bin/env python3
"""
Switch active raw dataset between:
  - small: native files users.csv/events.csv/orders.csv (no symlinks)
  - big  : symlink canonical names -> *_big.csv

Usage:
  python scripts/switch_data_scale.py [small|big]
"""
from pathlib import Path
import sys
import os

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def relink(dst: Path, target: Path):
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    try:
        os.symlink(os.path.relpath(target, start=dst.parent), dst)
    except OSError:
        import shutil

        shutil.copyfile(target, dst)


def use_small():
    # remove symlinks, keep/expect native CSVs
    for name in ("users.csv", "events.csv", "orders.csv"):
        p = RAW / name
        if p.is_symlink():
            p.unlink()
    missing = [n for n in ("users.csv", "events.csv", "orders.csv") if not (RAW / n).exists()]
    if missing:
        print(f"ℹ️  Missing {', '.join(missing)}. Generate the small dataset first:")
        print("    python scripts/seed_synthetic_data.py")
        sys.exit(3)
    import pandas as pd

    u = pd.read_csv(RAW / "users.csv")
    e = pd.read_csv(RAW / "events.csv")
    o = pd.read_csv(RAW / "orders.csv")
    print("✅ Switched to 'small' dataset (native files).")
    print(f"  users.csv  ({len(u):,} rows)")
    print(f"  events.csv ({len(e):,} rows)")
    print(f"  orders.csv ({len(o):,} rows)")


def use_big():
    targets = {
        "users.csv": RAW / "users_big.csv",
        "events.csv": RAW / "events_big.csv",
        "orders.csv": RAW / "orders_big.csv",
    }
    missing = [p.name for p in targets.values() if not p.exists()]
    if missing:
        print(f"❌ Missing required big files: {', '.join(missing)}")
        print("   Run: python scripts/seed_synthetic_data_big.py")
        sys.exit(2)
    for dst_name, target in targets.items():
        relink(RAW / dst_name, target)
    import pandas as pd

    u = pd.read_csv(RAW / "users.csv")
    e = pd.read_csv(RAW / "events.csv")
    o = pd.read_csv(RAW / "orders.csv")
    print("✅ Switched to 'big' dataset (symlinks).")
    print(f"  users.csv  -> users_big.csv   ({len(u):,} rows)")
    print(f"  events.csv -> events_big.csv  ({len(e):,} rows)")
    print(f"  orders.csv -> orders_big.csv  ({len(o):,} rows)")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"small", "big"}:
        print("Usage: python scripts/switch_data_scale.py [small|big]")
        sys.exit(1)
    scale = sys.argv[1]
    if scale == "small":
        use_small()
    else:
        use_big()


if __name__ == "__main__":
    main()
