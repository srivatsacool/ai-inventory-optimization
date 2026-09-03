#!/usr/bin/env python
"""Wire MASE/RMSSE through the shared metrics pipeline (Step 3).

For every family all_forecasts.csv:
  - per-series MASE and RMSSE with seasonal_period=7 (weekly retail
    seasonality, both datasets), denominator = in-sample one-step
    seasonal-naive error on the FROZEN TRAIN period only
    (2013-01-01 -> 2015-10-31, 1034 days). Never touches validation/test.
  - honest NaN when the denominator is zero (constant train history);
    NaN counts are reported, never silently epsilon-guarded.
  - adds MASE/RMSSE columns to metrics_by_series.csv and metrics_by_model.csv
    in place. Originals are backed up once to 06_results/_pre_hardening_backup/
    with a manifest (no silent overwrites).

Outputs: updated metrics_by_series.csv / metrics_by_model.csv per family
  + 06_results/scale_free_metrics/summary.csv (per dataset/model MASE/RMSSE
    with n_series and n_nan_denominator).
"""
from __future__ import annotations

import json
import pathlib
import re
import shutil
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "11_src"))

import numpy as np
import pandas as pd
from metrics import mase as mase_fn
from metrics import rmsse as rmsse_fn

ROOT = pathlib.Path(__file__).resolve().parents[1]
BACKUP = ROOT / "06_results" / "_pre_hardening_backup"
BACKUP.mkdir(parents=True, exist_ok=True)
OUT = ROOT / "06_results" / "scale_free_metrics"
OUT.mkdir(parents=True, exist_ok=True)

SEASONAL_PERIOD = 7  # weekly retail seasonality, both datasets (documented choice)
TRAIN_START = pd.Timestamp("2013-01-01")
TRAIN_END = pd.Timestamp("2015-10-31")

FAMILIES = ["baselines", "exponential_smoothing", "arima", "lstm", "croston"]

manifest: dict = {"backup_files": [], "seasonal_period": SEASONAL_PERIOD,
                  "train_period": [str(TRAIN_START.date()), str(TRAIN_END.date())]}


def backup_once(path: pathlib.Path) -> None:
    rel = str(path.relative_to(ROOT))
    dest = BACKUP / rel
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)
    manifest["backup_files"].append(rel)


def store_canon(s: str) -> tuple[int, int]:
    s = str(s)
    m = re.match(r"S0*(\d+)_I0*(\d+)", s)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    m = re.match(r"store_(\d+)_item_(\d+)", s)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    raise ValueError(f"unparseable store series_id {s!r}")


print("loading train histories (frozen train period only) ...")
# M5 train matrix over the common window
M5_RAW = ROOT / "02_data" / "dataset_01_m5" / "raw"
cal = pd.read_csv(M5_RAW / "calendar.csv")
cal["date"] = pd.to_datetime(cal["date"])
d_to_date = dict(zip(cal["d"], cal["date"]))
cfg = json.load(open(ROOT / "05_experiments" / "config.json"))
cs = pd.Timestamp(cfg["common_window"]["start"])
ce = pd.Timestamp(cfg["common_window"]["end"])
m5_wide = pd.read_csv(M5_RAW / "sales_train_evaluation.csv")
d_cols = [c for c in m5_wide.columns if c.startswith("d_")]
common_d = [c for c in d_cols if cs <= d_to_date[c] <= ce]
dates_common = pd.to_datetime([d_to_date[c] for c in common_d])
m5_common = m5_wide.set_index("id")[common_d]
train_mask = (dates_common >= TRAIN_START) & (dates_common <= TRAIN_END)
print(f"M5 common {m5_common.shape}, train cols {int(train_mask.sum())}")
m5_train = m5_common.loc[:, train_mask]

# Store-Item train pivot over the common window
SIT_RAW = ROOT / "02_data" / "dataset_02_store_item_demand" / "raw"
sit = pd.read_csv(SIT_RAW / "train.csv", parse_dates=["date"])
sit = sit[(sit["date"] >= cs) & (sit["date"] <= ce)].copy()
sit["series_id"] = "store_" + sit["store"].astype(str) + "_item_" + sit["item"].astype(str)
pivot = sit.pivot_table(index="date", columns="series_id", values="sales",
                        aggfunc="sum").sort_index().reindex(dates_common)
sit_train = pivot.loc[(pivot.index >= TRAIN_START) & (pivot.index <= TRAIN_END)]
print(f"Store pivot {pivot.shape}, train rows {sit_train.shape}")
# canonical (store,item) -> train vector for format-agnostic lookup
sit_train_canon = {store_canon(c): sit_train[c].values.astype(float) for c in sit_train.columns}

summary_rows = []
for fam in FAMILIES:
    fdir = ROOT / "06_results" / fam
    fc = pd.read_csv(fdir / "all_forecasts.csv")
    if "origin_id" in fc.columns and "origin" not in fc.columns:
        fc = fc.rename(columns={"origin_id": "origin"})
    per_series = []
    for (ds, model, sid), sub in fc.groupby(["dataset", "model", "series_id"]):
        a = sub["actual"].values.astype(float)
        f = sub["forecast"].values.astype(float)
        if ds == "m5":
            ytr = m5_train.loc[sid].values.astype(float)
        else:
            ytr = sit_train_canon[store_canon(sid)]
        per_series.append({
            "dataset": ds, "series_id": sid, "model": model,
            "MASE": mase_fn(a, f, ytr, SEASONAL_PERIOD),
            "RMSSE": rmsse_fn(a, f, ytr, SEASONAL_PERIOD),
            "mase_denom_nan": bool(np.isnan(mase_fn(a, f, ytr, SEASONAL_PERIOD))),
        })
    sf = pd.DataFrame(per_series)

    for fname in ["metrics_by_series.csv", "metrics_by_model.csv"]:
        backup_once(fdir / fname)
    ms = pd.read_csv(fdir / "metrics_by_series.csv")
    # join key: dataset+series_id+model (metrics_by_series may lack model? check)
    print(f"{fam}: metrics_by_series cols {list(ms.columns)}")
    key = ["dataset", "series_id"]
    if "model" in ms.columns:
        key.append("model")
    ms = ms.merge(sf[["dataset", "series_id", "model", "MASE", "RMSSE"]],
                  on=key, how="left", suffixes=("", "_new"))
    if "MASE_new" in ms.columns:  # idempotent rerun: refresh values
        ms["MASE"] = ms["MASE_new"]
        ms["RMSSE"] = ms["RMSSE_new"]
        ms = ms.drop(columns=["MASE_new", "RMSSE_new"])
    ms.to_csv(fdir / "metrics_by_series.csv", index=False)

    mm = pd.read_csv(fdir / "metrics_by_model.csv")
    agg = sf.groupby(["dataset", "model"]).agg(
        MASE=("MASE", "mean"), RMSSE=("RMSSE", "mean"),
        n_series=("MASE", "size"),
        n_nan_mase=("mase_denom_nan", "sum")).reset_index()
    mm = mm.merge(agg, on=["dataset", "model"], how="left", suffixes=("", "_new"))
    for c in ["MASE", "RMSSE", "n_series", "n_nan_mase"]:
        if c + "_new" in mm.columns:
            mm[c] = mm[c + "_new"]
            mm = mm.drop(columns=[c + "_new"])
    mm.to_csv(fdir / "metrics_by_model.csv", index=False)
    for _, r in agg.iterrows():
        summary_rows.append({"family": fam, **r.to_dict()})
    print(f"{fam}: MASE/RMSSE wired "
          f"(NaN-denominator series: {int(sf['mase_denom_nan'].sum())}/{len(sf)})")

summ = pd.DataFrame(summary_rows)
summ.to_csv(OUT / "summary.csv", index=False)
(OUT / "method_note.txt").write_text(
    "MASE/RMSSE, seasonal_period=7 (weekly retail seasonality) for BOTH datasets.\n"
    "Denominator = in-sample one-step seasonal-naive error on frozen TRAIN ONLY "
    "(2013-01-01..2015-10-31, 1034d). Validation/test never enter the denominator.\n"
    "Denominator zero (constant train history) -> honest NaN (see n_nan_mase), "
    "never epsilon-guarded. Per-series scale-free value, then mean across series.\n")
(BACKUP / "manifest.json").write_text(json.dumps(manifest, indent=2))
print(f"\nsummary:\n{summ.round(4).to_string(index=False)}")
print(f"saved {OUT / 'summary.csv'}; backups in {BACKUP}")
