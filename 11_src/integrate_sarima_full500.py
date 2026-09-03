#!/usr/bin/env python
"""Integrate full-500 SARIMA into the arima family results (Step 2 completion).

1. Rebuilds 06_results/arima/all_forecasts.csv as
     arima_forecasts.csv (224000: ARIMA full-pop both datasets)
   + sarima_store_item_full500.csv (112000: SARIMA full-pop Store)
   The 100-series subset file sarima_store_item_subset.csv is RETAINED
   untouched as a labelled exploratory artifact (see decisions.md).
2. Recomputes arima metrics_by_model / metrics_by_series / metrics_by_origin
   (MAE/RMSE/sMAPE/WAPE with the shared definitions) + MASE/RMSSE
   (seasonal_period=7, frozen-train denominator via metrics.py).
3. Merges convergence_details_full500.csv into convergence bookkeeping and
   rewrites convergence_report.csv with a scope column
   (subset100_exploratory vs full500_primary).
Prior all_forecasts.csv (subset-based) is preserved once at
06_results/_pre_hardening_backup/06_results/arima/all_forecasts_subset_based.csv.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "11_src"))

import numpy as np
import pandas as pd
from metrics import mase as mase_fn
from metrics import rmsse as rmsse_fn
from metrics import smape as smape_fn

ROOT = pathlib.Path(__file__).resolve().parents[1]
RES = ROOT / "06_results" / "arima"
BACKUP = ROOT / "06_results" / "_pre_hardening_backup" / "06_results" / "arima"
BACKUP.mkdir(parents=True, exist_ok=True)

# 0. preserve subset-based all_forecasts once
if not (BACKUP / "all_forecasts_subset_based.csv").exists():
    shutil.copy2(RES / "all_forecasts.csv", BACKUP / "all_forecasts_subset_based.csv")
    print("preserved subset-based all_forecasts.csv in backup")

# 1. rebuild
arima = pd.read_csv(RES / "arima_forecasts.csv")
full = pd.read_csv(RES / "sarima_store_item_full500.csv")
assert len(arima) == 224000, len(arima)
assert len(full) == 112000, len(full)
all_fc = pd.concat([arima, full], ignore_index=True)
assert all_fc.duplicated(subset=["dataset", "model", "series_id", "origin", "forecast_date"]).sum() == 0
all_fc.to_csv(RES / "all_forecasts.csv", index=False)
print(f"rebuilt all_forecasts.csv: {len(all_fc)} rows (ARIMA 224000 + SARIMA-full500 112000)")

# 2. metrics (shared definitions: MAE/RMSE mean, WAPE ratio-of-sums +1e-9 guard
#    as in Notebook 07 frozen code, sMAPE via metrics.py masked mean)
rows_m, rows_s, rows_o = [], [], []
for (ds, model), sub in all_fc.groupby(["dataset", "model"]):
    a = sub["actual"].values.astype(float)
    f = sub["forecast"].values.astype(float)
    rows_m.append({"dataset": ds, "model": model, "n": len(sub),
                   "MAE": float(np.mean(np.abs(a - f))),
                   "RMSE": float(np.sqrt(np.mean((a - f) ** 2))),
                   "sMAPE": float(smape_fn(a, f)),
                   "WAPE": float(np.sum(np.abs(a - f)) / (np.sum(np.abs(a)) + 1e-9))})
    for sid, g in sub.groupby("series_id"):
        ga, gf = g["actual"].values.astype(float), g["forecast"].values.astype(float)
        rows_s.append({"dataset": ds, "model": model, "series_id": sid, "n": len(g),
                       "MAE": float(np.mean(np.abs(ga - gf))),
                       "RMSE": float(np.sqrt(np.mean((ga - gf) ** 2))),
                       "sMAPE": float(smape_fn(ga, gf)),
                       "WAPE": float(np.sum(np.abs(ga - gf)) / (np.sum(np.abs(ga)) + 1e-9))})
    for oi, g in sub.groupby("origin"):
        ga, gf = g["actual"].values.astype(float), g["forecast"].values.astype(float)
        rows_o.append({"dataset": ds, "model": model, "origin": oi, "n": len(g),
                       "MAE": float(np.mean(np.abs(ga - gf))),
                       "RMSE": float(np.sqrt(np.mean((ga - gf) ** 2))),
                       "sMAPE": float(smape_fn(ga, gf)),
                       "WAPE": float(np.sum(np.abs(ga - gf)) / (np.sum(np.abs(ga)) + 1e-9))})
mm = pd.DataFrame(rows_m).sort_values(["dataset", "MAE"])
ms = pd.DataFrame(rows_s)
mo = pd.DataFrame(rows_o)

# MASE/RMSSE per series (train-only denominator, m=7) then mean per model
cfg = json.load(open(ROOT / "05_experiments" / "config.json"))
cs, ce = pd.Timestamp(cfg["common_window"]["start"]), pd.Timestamp(cfg["common_window"]["end"])
M5_RAW = ROOT / "02_data" / "dataset_01_m5" / "raw"
cal = pd.read_csv(M5_RAW / "calendar.csv")
cal["date"] = pd.to_datetime(cal["date"])
d2d = dict(zip(cal["d"], cal["date"]))
m5w = pd.read_csv(M5_RAW / "sales_train_evaluation.csv")
dc = [c for c in m5w.columns if c.startswith("d_") and cs <= d2d[c] <= ce]
dts = pd.to_datetime([d2d[c] for c in dc])
m5tr = m5w.set_index("id")[dc].loc[:, (dts >= "2013-01-01") & (dts <= "2015-10-31")]
SIT = pd.read_csv(ROOT / "02_data" / "dataset_02_store_item_demand" / "raw" / "train.csv",
                  parse_dates=["date"])
SIT = SIT[(SIT["date"] >= cs) & (SIT["date"] <= ce)].copy()
SIT["series_id"] = "store_" + SIT["store"].astype(str) + "_item_" + SIT["item"].astype(str)
pv = SIT.pivot_table(index="date", columns="series_id", values="sales",
                     aggfunc="sum").sort_index()
sit_tr = pv.loc[(pv.index >= "2013-01-01") & (pv.index <= "2015-10-31")]
import re as _re


def _canon(s):
    m = _re.match(r"S0*(\d+)_I0*(\d+)", str(s))
    return f"store_{int(m.group(1))}_item_{int(m.group(2))}" if m else str(s)


sit_canon = {_canon(c): sit_tr[c].values.astype(float) for c in sit_tr.columns}
sf = []
for (ds, model, sid), g in all_fc.groupby(["dataset", "model", "series_id"]):
    ga, gf = g["actual"].values.astype(float), g["forecast"].values.astype(float)
    ytr = m5tr.loc[sid].values.astype(float) if ds == "m5" else sit_canon[_canon(sid)]
    sf.append({"dataset": ds, "model": model, "series_id": sid,
               "MASE": mase_fn(ga, gf, ytr, 7), "RMSSE": rmsse_fn(ga, gf, ytr, 7)})
sf = pd.DataFrame(sf)
ms = ms.merge(sf, on=["dataset", "model", "series_id"], how="left")
mag = sf.groupby(["dataset", "model"]).agg(MASE=("MASE", "mean"),
                                            RMSSE=("RMSSE", "mean")).reset_index()
mm = mm.merge(mag, on=["dataset", "model"], how="left")
mm.to_csv(RES / "metrics_by_model.csv", index=False)
ms.to_csv(RES / "metrics_by_series.csv", index=False)
mo.to_csv(RES / "metrics_by_origin.csv", index=False)
print(mm.round(4).to_string(index=False))
print(f"NaN MASE series: {int(sf['MASE'].isna().sum())}/{len(sf)}")

# 3. convergence bookkeeping: tag scope, rewrite report
old = pd.read_csv(RES / "convergence_details.csv")
old["scope"] = "subset100_exploratory"
new = pd.read_csv(RES / "convergence_details_full500.csv")
new["scope"] = "full500_primary"
if "archetype" not in new.columns:
    new["archetype"] = ""
both = pd.concat([old, new], ignore_index=True)
both.to_csv(RES / "convergence_details_all.csv", index=False)
rep = (both.assign(fallback=(both["status"] != "fit_ok").astype(int),
                   attempted=(both["status"] != "fallback_skip").astype(int),
                   failed=(both["status"] == "fallback_fail").astype(int))
       .groupby(["scope", "dataset", "model"], as_index=False)
       .agg(n_series=("status", "size"), n_fits_attempted=("attempted", "sum"),
            n_fit_failures=("failed", "sum"), n_fallback_naive=("fallback", "sum")))
rep["failure_pct"] = (100 * rep["n_fit_failures"] / rep["n_fits_attempted"]).round(2)
rep["fallback_pct"] = (100 * rep["n_fallback_naive"] / rep["n_series"]).round(2)
rep.to_csv(RES / "convergence_report.csv", index=False)
print(rep.to_string(index=False))
print("SARIMA INTEGRATION COMPLETE")
