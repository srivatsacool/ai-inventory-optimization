"""Tests for inventory_policy: loader coverage + scalar/batch parity.

Run: python 11_src/test_inventory_policy.py
Exit 0 = all pass.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "11_src"))

import numpy as np
from inventory_policy import (
    FORECAST_FILES,
    POLICY_DEFAULT,
    load_all_forecasts,
    simulate_batch,
    simulate_series,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
    if not cond:
        failures.append(name)


# 1. Loader covers all registered families (incl. croston)
check("croston registered in FORECAST_FILES", "croston" in FORECAST_FILES)
all_fc = load_all_forecasts(ROOT / "06_results")
fams = set(all_fc["family"].unique())
check("Croston-family present in loaded frame", "Croston-family" in fams, str(sorted(fams)))
for m in ["CROSTON", "SBA", "TSB"]:
    n = len(all_fc[all_fc["model"] == m])
    check(f"model {m} has 112000 rows (500x8x28)", n == 112_000, f"got {n}")
    ds = set(all_fc[all_fc["model"] == m]["dataset"].unique())
    check(f"model {m} is M5-only by design", ds == {"m5"}, str(ds))

# 2. Full-population models keep 112k rows per dataset
for m in ["Naive", "Seasonal Naive", "Moving Average", "SES", "DES", "TES", "ARIMA", "LSTM"]:
    for ds in ["m5", "store_item_demand"]:
        n = len(all_fc[(all_fc["model"] == m) & (all_fc["dataset"] == ds)])
        check(f"{m}/{ds} full population", n == 112_000, f"got {n}")

# 3. No duplicate keys, schema complete
dup = all_fc.duplicated(subset=["dataset", "model", "series_id", "origin", "forecast_date"]).sum()
check("zero duplicate forecast keys", dup == 0, f"got {dup}")
check("origin column normalized (no origin_id leak)",
      "origin" in all_fc.columns and all_fc["origin"].isna().sum() == 0)
check("error column present", "error" in all_fc.columns)

# 4. Scalar vs batch parity across policies (incl. non-default grid corners)
from inventory_policy import make_policy

rng = np.random.default_rng(42)
max_diff = 0.0
for trial in range(5):
    m = int(rng.integers(2, 12))
    Fs = rng.integers(0, 30, size=(m, 28)).astype(float)
    As = rng.integers(0, 40, size=(m, 28)).astype(float)
    for pol in [POLICY_DEFAULT, make_policy(3, 0.90, 3), make_policy(14, 0.99, 10)]:
        bat = simulate_batch(Fs, As, pol)
        for k in range(m):
            sca = simulate_series(Fs[k], As[k], pol)
            for key in bat:
                max_diff = max(max_diff, float(abs(bat[key][k] - sca[key])))
check("scalar/batch parity < 1e-9", max_diff < 1e-9, f"max diff {max_diff:.3e}")

print(f"\n{len(failures)} failures out of all checks.")
sys.exit(1 if failures else 0)
