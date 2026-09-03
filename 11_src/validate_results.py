#!/usr/bin/env python
"""Validate all result files: schemas, coverage, dates, metric definitions (Step 8).

Checks per family all_forecasts.csv:
  - expected row counts (112000 per full-pop model/dataset; 22400 SARIMA subset)
  - zero duplicate (dataset,model,series_id,origin,forecast_date) keys
  - origins exactly {1..8}, 28 forecast days per (series,origin)
  - forecast_date in test window 2016-03-01..2016-05-22 and
    forecast_date >= origin_date (history<origin boundary)
  - finite actuals/forecasts, non-negative forecasts
Cross-family: actuals identical for same (dataset,series_id,origin,forecast_date)
  (sampled). Metrics: MASE/RMSSE present, NaN counts reported.
Inventory: every loader model present, costs finite.
Writes 06_results/validation_report.json + stdout PASS/FAIL per gate.
Exit 1 on any FAIL.
"""
from __future__ import annotations

import json
import pathlib
import sys
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
RES = ROOT / "06_results"
TEST_START = pd.Timestamp("2016-03-01")
TEST_END = pd.Timestamp("2016-05-22")

report: dict = {"gates": {}}
fail = 0


def gate(name: str, ok: bool, detail: str = "") -> None:
    global fail
    report["gates"][name] = {"status": "PASS" if ok else "FAIL", "detail": detail}
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        fail += 1


EXPECTED = {  # (family file) -> {(dataset, model): rows}
    "baselines": {(("m5", "Naive"), 112000), (("m5", "Seasonal Naive"), 112000),
                  (("m5", "Moving Average"), 112000),
                  (("store_item_demand", "Naive"), 112000),
                  (("store_item_demand", "Seasonal Naive"), 112000),
                  (("store_item_demand", "Moving Average"), 112000)},
    "exponential_smoothing": {(("m5", "SES"), 112000), (("m5", "DES"), 112000),
                              (("m5", "TES"), 112000),
                              (("store_item_demand", "SES"), 112000),
                              (("store_item_demand", "DES"), 112000),
                              (("store_item_demand", "TES"), 112000)},
    "arima": {(("m5", "ARIMA"), 112000), (("store_item_demand", "ARIMA"), 112000),
              (("store_item_demand", "SARIMA"), 22400)},
    "lstm": {(("m5", "LSTM"), 112000), (("store_item_demand", "LSTM"), 112000)},
    "croston": {(("m5", "CROSTON"), 112000), (("m5", "SBA"), 112000), (("m5", "TSB"), 112000)},
}

full500 = RES / "arima" / "sarima_store_item_full500.csv"
if full500.exists():
    EXPECTED["arima"] = {(("m5", "ARIMA"), 112000), (("store_item_demand", "ARIMA"), 112000),
                         (("store_item_demand", "SARIMA"), 112000)}
    gate("sarima_full500_present", True, f"{len(pd.read_csv(full500))} rows")

for fam, cells in EXPECTED.items():
    df = pd.read_csv(RES / fam / "all_forecasts.csv")
    if "origin_id" in df.columns and "origin" not in df.columns:
        df = df.rename(columns={"origin_id": "origin"})
    df = df[["dataset", "model", "series_id", "origin",
             "origin_date", "forecast_date", "actual", "forecast"]]
    counts = df.groupby(["dataset", "model"]).size().to_dict()
    ok = all(counts.get(k) == v for k, v in cells)
    gate(f"{fam}_row_counts", ok, str({k: counts.get(k) for k, _ in cells}))
    dup = int(df.duplicated(subset=["dataset", "model", "series_id", "origin", "forecast_date"]).sum())
    gate(f"{fam}_no_dup_keys", dup == 0, f"dups={dup}")
    gate(f"{fam}_origins_1_to_8", set(df["origin"].unique()) == set(range(1, 9)),
         str(sorted(df["origin"].unique())))
    per = df.groupby(["dataset", "model", "series_id", "origin"]).size()
    gate(f"{fam}_h28_everywhere", bool((per == 28).all()),
         f"min={int(per.min())} max={int(per.max())}")
    fd = pd.to_datetime(df["forecast_date"])
    od = pd.to_datetime(df["origin_date"])
    gate(f"{fam}_dates_in_test_window",
         bool(((fd >= TEST_START) & (fd <= TEST_END)).all() & (fd >= od).all()))
    gate(f"{fam}_forecasts_finite_nonneg",
         bool(np.isfinite(df["forecast"]).all() and (df["forecast"] >= 0).all()))

# cross-family actual agreement (sample 20k rows)
import random
random.seed(42)
frames = []
for fam in ["baselines", "exponential_smoothing", "arima", "lstm", "croston"]:
    d = pd.read_csv(RES / fam / "all_forecasts.csv")
    if "origin_id" in d.columns and "origin" not in d.columns:
        d = d.rename(columns={"origin_id": "origin"})
    d = d[["dataset", "series_id", "origin", "forecast_date", "actual"]]
    d["family"] = fam
    frames.append(d.sample(min(len(d), 20000), random_state=42))
s = pd.concat(frames, ignore_index=True)


def _canon_store(sid: str) -> str:
    import re as _re
    s = str(sid)
    m = _re.match(r"S0*(\d+)_I0*(\d+)", s)
    if m:
        return f"store_{int(m.group(1))}_item_{int(m.group(2))}"
    return s


mask = s["dataset"] == "store_item_demand"
s.loc[mask, "series_id"] = s.loc[mask, "series_id"].map(_canon_store)
spread = s.groupby(["dataset", "series_id", "origin", "forecast_date"])["actual"].agg(["min", "max"])
spread["d"] = spread["max"] - spread["min"]
gate("cross_family_actuals_identical", bool((spread["d"] == 0).all()),
     f"max spread={float(spread['d'].max()):.6f}")

# metrics files carry MASE/RMSSE without unexpected NaN
for fam in ["baselines", "exponential_smoothing", "arima", "lstm", "croston"]:
    mm = pd.read_csv(RES / fam / "metrics_by_model.csv")
    gate(f"{fam}_metrics_have_MASE_RMSSE", {"MASE", "RMSSE"} <= set(mm.columns),
         str(list(mm.columns)))
    gate(f"{fam}_metrics_no_unexpected_NaN",
         bool(mm[["MAE", "RMSE", "WAPE", "MASE", "RMSSE"]].notna().all().all()),
         mm[mm[["MAE", "RMSE", "WAPE", "MASE", "RMSSE"]].isna().any(axis=1)][["dataset", "model"]].to_string(index=False))

# inventory covers every loader model
sys.path.insert(0, str(ROOT / "11_src"))
from inventory_policy import load_all_forecasts
all_fc = load_all_forecasts(RES)
inv = pd.read_csv(RES / "inventory" / "inventory_by_model.csv")
need = set(map(tuple, all_fc[["dataset", "model"]].drop_duplicates().values.tolist()))
have = set(map(tuple, inv[["dataset", "model"]].drop_duplicates().values.tolist()))
gate("inventory_covers_all_models", need == have, f"missing={need - have} extra={have - need}")
gate("inventory_costs_finite", bool(np.isfinite(inv["total_cost"]).all()))

(RES / "validation_report.json").write_text(json.dumps(report, indent=2))
print(f"\n{fail} FAIL gates. Report: {RES / 'validation_report.json'}")
sys.exit(1 if fail else 0)
