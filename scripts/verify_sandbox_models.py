"""Verify that the sandbox model implementations reproduce the frozen
benchmark forecasts (origin 1) bit-for-bit within float tolerance.
Research-only script; writes nothing.
"""
import sys
import pathlib

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.lib import models as M  # noqa: E402

ext = pd.read_parquet(ROOT / "app_data" / "interactive_series.parquet")
ext["date"] = pd.to_datetime(ext["date"])


def hist_and_actual(ds, sid, origin_date):
    s = ext[(ext.dataset == ds) & (ext.series_id == sid)].sort_values("date")
    hist = s[s.date < origin_date].demand.values
    return hist


CHECKS = [
    ("m5", "FOODS_3_365_WI_2_evaluation", "Naive", "06_results/baselines/all_forecasts.csv", None),
    ("m5", "FOODS_2_258_TX_1_evaluation", "Seasonal Naive", "06_results/baselines/all_forecasts.csv", None),
    ("m5", "FOODS_3_365_WI_2_evaluation", "Moving Average", "06_results/baselines/all_forecasts.csv", None),
    ("m5", "HOBBIES_1_415_WI_3_evaluation", "SES", "06_results/exponential_smoothing/all_forecasts.csv", None),
    ("m5", "HOBBIES_1_415_WI_3_evaluation", "DES", "06_results/exponential_smoothing/all_forecasts.csv", None),
    ("m5", "HOBBIES_1_415_WI_3_evaluation", "TES", "06_results/exponential_smoothing/all_forecasts.csv", None),
    ("m5", "FOODS_3_365_WI_2_evaluation", "Croston", "06_results/croston/all_forecasts_croston.csv", None),
    ("m5", "FOODS_3_365_WI_2_evaluation", "SBA", "06_results/croston/all_forecasts_sba.csv", None),
    ("m5", "FOODS_3_365_WI_2_evaluation", "TSB", "06_results/croston/all_forecasts_tsb.csv", None),
    ("store_item_demand", "S10_I01", "ARIMA", "06_results/arima/all_forecasts.csv", "store_10_item_1"),
    ("store_item_demand", "S10_I01", "SARIMA", "06_results/arima/all_forecasts.csv", "store_10_item_1"),
]

failures = 0
for ds, sid, model, rel, frozen_sid in CHECKS:
    header = pd.read_csv(ROOT / rel, nrows=0).columns.tolist()
    ocol = "origin_id" if "origin_id" in header else "origin"
    fc = pd.read_csv(ROOT / rel, usecols=["dataset", "series_id", "forecast", "model", "origin_date", ocol])
    frozen_model = {"Croston": "CROSTON"}.get(model, model)  # croston file uses uppercase
    fc = fc[(fc.dataset == ds) & (fc.series_id == (frozen_sid or sid)) & (fc[ocol] == 1) & (fc.model == frozen_model)]
    frozen = fc.forecast.values[:28]
    hist = hist_and_actual(ds, sid, None) if False else None
    s = ext[(ext.dataset == ds) & (ext.series_id == sid)].sort_values("date")
    od = pd.Timestamp(fc.origin_date.iloc[0])
    hist = s[s.date < od].demand.values
    fn = M.MODEL_LADDER[model]["func"]
    if model == "Moving Average":
        pred = fn(hist, horizon=28, dataset=ds)
    else:
        pred = fn(hist)
    diff = float(np.abs(pred - frozen).max())
    ok = diff < 1e-6
    failures += 0 if ok else 1
    print(f"{'PASS' if ok else 'FAIL'}  {model:16s} max|diff|={diff:.8f}  (frozen n={len(frozen)})")

print("RESULT:", "ALL PASS" if failures == 0 else f"{failures} FAILURES")
sys.exit(1 if failures else 0)
