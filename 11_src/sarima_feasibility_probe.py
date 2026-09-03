"""SARIMA full-500 feasibility probe — frozen protocol, Store Item Demand.

Fits SARIMAX(1,1,0)(0,1,1,7) on a small sample of (series x origin) windows
using the exact history boundary (history strictly < origin) and the exact
sarima_forecast helper logic from Notebook 07, times them, and extrapolates
to the full 500 series x 8 origins = 4000 fits.

Outputs: 05_experiments/sarima_feasibility.json + stdout summary.
"""
from __future__ import annotations

import json
import pathlib
import time
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

PROJ = pathlib.Path(__file__).resolve().parents[1]
SIT_RAW = PROJ / "02_data" / "dataset_02_store_item_demand" / "raw"

H = 28
N_ORIGINS = 8
ORIGINS = [pd.Timestamp("2016-03-01") + pd.Timedelta(days=7 * k) for k in range(N_ORIGINS)]

print("loading store-item train.csv ...", flush=True)
sit = pd.read_csv(SIT_RAW / "train.csv", parse_dates=["date"])
sit["series_id"] = "store_" + sit["store"].astype(str) + "_item_" + sit["item"].astype(str)
dates_common = pd.date_range("2013-01-01", "2016-05-22", freq="D")
pivot = sit.pivot_table(index="date", columns="series_id", values="sales", aggfunc="sum").sort_index()
pivot = pivot.reindex(dates_common)
print(f"pivot {pivot.shape} (expect 1238 x 500)", flush=True)

from statsmodels.tsa.statespace.sarimax import SARIMAX  # noqa: E402


def sarima_forecast(history, horizon=H):
    if len(history) < 30 or np.all(history == 0):
        return np.repeat(history[-1] if len(history) > 0 else 0, horizon), "skip"
    m = SARIMAX(history, order=(1, 1, 0), seasonal_order=(0, 1, 1, 7),
                enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
    fc = np.asarray(m.get_forecast(steps=horizon).predicted_mean, dtype=float)
    fc = np.where(np.isfinite(fc), fc, history[-1])
    return np.maximum(fc, 0), "ok"


rng = np.random.default_rng(42)
sample_ids = sorted(rng.choice(pivot.columns.tolist(), size=8, replace=False).tolist())
sample_origins = [ORIGINS[0], ORIGINS[4]]  # early + mid test window
times: list[float] = []
statuses: list[str] = []
for sid in sample_ids:
    for od in sample_origins:
        hist_len = int((dates_common < od).sum())
        hist = pivot[sid].values[:hist_len].astype(float)
        t0 = time.time()
        try:
            _, st = sarima_forecast(hist)
        except Exception as e:  # noqa: BLE001
            st = f"fail:{type(e).__name__}"
        dt = time.time() - t0
        times.append(dt)
        statuses.append(st)
        print(f"{sid} {od.date()} hist={hist_len} {st} {dt:.2f}s", flush=True)

times = np.array(times)
res = {
    "protocol": "SARIMAX(1,1,0)(0,1,1,7), Store Item 500x8, H=28, history<origin",
    "n_probe": len(times),
    "mean_s_per_fit": float(times.mean()),
    "median_s_per_fit": float(np.median(times)),
    "max_s_per_fit": float(times.max()),
    "statuses": {s: statuses.count(s) for s in sorted(set(statuses))},
    "fits_full_500": 4000,
    "eta_s_mean": float(times.mean() * 4000),
    "eta_s_median": float(np.median(times) * 4000),
}
out = PROJ / "05_experiments" / "sarima_feasibility.json"
out.write_text(json.dumps(res, indent=2))
print(json.dumps(res, indent=2))
print(f"saved {out}")
