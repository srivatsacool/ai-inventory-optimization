#!/usr/bin/env python
"""Shared inventory policy + simulator — single source of truth for the inventory layer.

Why this module exists
----------------------
`inventory_simulation.py` and `sensitivity_analysis.py` must feed *every* forecast
model through the *same* inventory policy (same lead time, same service target /
safety factor, same cost structure).  All policy parameters live here, in one
place, so a per-model or per-family divergence is impossible by construction.
The default policy reproduces the historical Phase-1 simulation exactly.

Policy object
-------------
A policy is a plain dict with keys:
    lead_time       int      review/replenishment lead time in days
    service_target  float    cycle-service target (0..1); z is derived from it
    z               float    safety factor (norm.ppf(service_target)); if None it
                             is derived from service_target
    H               float    holding cost per unit per day   (base unit = 1.0)
    P               float    stockout (lost-sales) cost per unit; P/H is the
                             cost ratio used in sensitivity analysis
    sigma_floor     float    floor on the per-series error std used for safety
                             stock (avoids zero ss on perfectly forecast series)

Simulation (order-up-to / base stock, lost sales, daily review)
---------------------------------------------------------------
For each series-origin instance (28 evaluation days in this project):
  * safety stock  ss = z * max(std(forecast - actual), sigma_floor) * sqrt(lead_time)
  * initial on-hand = max(sum of first L forecasts, 1.0)   (no opening pipeline)
  * each day: receive due pipeline -> review: if inventory position
    (on-hand + pipeline) < order-up-to level
    [sum of next L forecasts (truncated at horizon) + ss], place an order for the
    difference (arrives in L days).
  * demand is served from on-hand only; unmet demand is lost (charged P).
  * holding cost charged on end-of-day on-hand (H per unit).

This is the exact math of the original Phase-1 script (kept bit-for-bit for the
scalar path); the vectorized batch path is validated to agree with it.
"""
from __future__ import annotations

import pathlib
import warnings

import numpy as np
import pandas as pd
from scipy.stats import norm

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Default policy — historical Phase-1 values (lead 7, 95% target, P/H = 5)
# ---------------------------------------------------------------------------
POLICY_DEFAULT = {
    "lead_time": 7,
    "service_target": 0.95,
    "z": None,  # derived from service_target on use
    "H": 1.0,
    "P": 5.0,
    "sigma_floor": 0.1,
}


def make_policy(lead_time: int, service_target: float, cost_ratio_p_to_h: float) -> dict:
    """Build a fully-specified policy from grid coordinates.

    H is normalised to 1.0 so `cost_ratio_p_to_h` IS the stockout cost P.
    z is the standard-normal quantile of the cycle-service target,
    i.e. z = norm.ppf(service_target).
    """
    if not (0.0 < service_target < 1.0):
        raise ValueError(f"service_target must be in (0,1), got {service_target}")
    return {
        "lead_time": int(lead_time),
        "service_target": float(service_target),
        "z": float(norm.ppf(service_target)),
        "H": 1.0,
        "P": float(cost_ratio_p_to_h),
        "sigma_floor": 0.1,
    }


def resolve_policy(policy: dict) -> dict:
    """Return a policy with all fields filled (derive z when None)."""
    p = dict(policy)
    if p.get("z") is None:
        p["z"] = float(norm.ppf(p["service_target"]))
    return p


# ---------------------------------------------------------------------------
# Scalar simulator — canonical reference (bit-for-bit = Phase-1 script)
# ---------------------------------------------------------------------------
def simulate_series(fc: np.ndarray, act: np.ndarray, policy: dict) -> dict:
    """Simulate one series instance (arrays, same length).

    Reproduces the original Phase-1 `simulate_one` exactly for the default
    policy; only the policy parameters are parameterised.
    """
    p = resolve_policy(policy)
    L, z, H, P, floor = p["lead_time"], p["z"], p["H"], p["P"], p["sigma_floor"]
    n = len(fc)
    err_std = max(float(np.std(fc - act)), floor)
    ss = z * err_std * np.sqrt(L)
    inv = max(float(np.sum(fc[:L])), 1.0)
    pipeline = np.zeros(L)
    h_cost = s_cost = s_days = s_qty = reorders = 0.0
    for d in range(n):
        inv += pipeline[0]
        pipeline = np.roll(pipeline, -1)
        pipeline[-1] = 0
        ord_up = float(np.sum(fc[d : min(d + L, n)])) + ss
        if inv + float(np.sum(pipeline)) < ord_up:
            pipeline[-1] = max(0.0, ord_up - inv - float(np.sum(pipeline)))
            reorders += 1
        dem = act[d]
        if dem > 0:
            if inv >= dem:
                inv -= dem
            else:
                s_qty += dem - inv
                s_cost += (dem - inv) * P
                s_days += 1
                inv = 0
        h_cost += inv * H
    return {
        "total_holding_cost": h_cost,
        "total_stockout_cost": s_cost,
        "total_cost": h_cost + s_cost,
        "service_level": 1 - s_days / n if n else 1,
        "average_inventory": h_cost / n if n else 0,
        "stockout_frequency": s_days,
        "stockout_quantity": s_qty,
        "reorder_count": reorders,
    }


def simulate_group(group: pd.DataFrame, policy: dict) -> dict:
    """Wrapper: sort a (model, series, origin) forecast frame by date, simulate."""
    g = group.sort_values("forecast_date").reset_index(drop=True)
    return simulate_series(
        g["forecast"].to_numpy(dtype=float),
        g["actual"].to_numpy(dtype=float),
        policy,
    )


# ---------------------------------------------------------------------------
# Vectorized batch simulator — same math, all instances at once.
#   F, A : (n_instances, n_days)  pre-sorted by (series, origin, forecast_date)
# ---------------------------------------------------------------------------
def simulate_batch(F: np.ndarray, A: np.ndarray, policy: dict) -> dict:
    """Vectorised order-up-to / lost-sales simulation over stacked instances.

    Validated against `simulate_series` (see self-test in __main__); results
    are bit-identical for the array shapes used in this project because NumPy
    reduces contiguous rows with the same pairwise-summation algorithm.
    """
    p = resolve_policy(policy)
    L, z, H, P, floor = p["lead_time"], p["z"], p["H"], p["P"], p["sigma_floor"]
    n = A.shape[1]
    n_inst = A.shape[0]

    err_std = np.maximum(np.std(F - A, axis=1), floor)
    ss = (z * err_std * np.sqrt(L)).astype(float)

    # pad forecasts with zeros so the lead-time sum truncates exactly like
    # the scalar `np.sum(fc[d:min(d+L, n)])`
    Fpad = np.zeros((n_inst, n + L))
    Fpad[:, :n] = F

    inv = np.maximum(Fpad[:, :L].sum(axis=1), 1.0)
    pipeline = np.zeros((n_inst, L))
    h_cost = np.zeros(n_inst)
    s_cost = np.zeros(n_inst)
    s_days = np.zeros(n_inst)
    s_qty = np.zeros(n_inst)
    reorders = np.zeros(n_inst)

    for d in range(n):
        inv += pipeline[:, 0]
        pipeline = np.roll(pipeline, -1, axis=1)
        pipeline[:, -1] = 0
        ord_up = Fpad[:, d : d + L].sum(axis=1) + ss
        ip = inv + pipeline.sum(axis=1)
        mask = ip < ord_up
        qty = np.clip(ord_up - ip, 0.0, None)
        pipeline[:, -1] = np.where(mask, qty, 0.0)
        reorders += mask
        dem = A[:, d]
        shortage = np.clip(dem - inv, 0.0, None)  # lost sales
        inv = np.clip(inv - dem, 0.0, None)
        s_qty += shortage
        s_cost += shortage * P
        s_days += shortage > 0
        h_cost += inv * H

    return {
        "total_holding_cost": h_cost,
        "total_stockout_cost": s_cost,
        "total_cost": h_cost + s_cost,
        "service_level": 1 - s_days / n,
        "average_inventory": h_cost / n,
        "stockout_frequency": s_days,
        "stockout_quantity": s_qty,
        "reorder_count": reorders,
    }


# ---------------------------------------------------------------------------
# Forecast loading — shared by both scripts (schema normalisation included)
# ---------------------------------------------------------------------------
FORECAST_FILES = {
    "baselines": ("Baseline", "baselines"),
    "exponential_smoothing": ("Smoothing", "exponential_smoothing"),
    "arima": ("ARIMA/SARIMA", "arima"),
    "lstm": ("LSTM", "lstm"),
    "croston": ("Croston-family", "croston"),
}

_RESULTS_DIR = pathlib.Path(__file__).resolve().parents[1] / "06_results"


def load_all_forecasts(results_dir: pathlib.Path | None = None) -> pd.DataFrame:
    """Load + normalise all families' forecasts into one long frame.

    Columns: dataset, model, series_id, origin, origin_date, forecast_date,
    actual, forecast, error, family.
    """
    rd = pathlib.Path(results_dir) if results_dir is not None else _RESULTS_DIR
    # Defensive: accept the repo root too (resolve to 06_results when needed).
    if not (rd / "baselines" / "all_forecasts.csv").exists() and (rd / "06_results" / "baselines" / "all_forecasts.csv").exists():
        rd = rd / "06_results"
    frames = []
    for fam_key, (family, subdir) in FORECAST_FILES.items():
        df = pd.read_csv(rd / subdir / "all_forecasts.csv")
        if "origin_id" in df.columns and "origin" not in df.columns:
            df = df.rename(columns={"origin_id": "origin"})
        if "error" not in df.columns:
            df["error"] = df["actual"] - df["forecast"]
        df["family"] = family
        cols = ["dataset", "model", "series_id", "origin", "origin_date",
                "forecast_date", "actual", "forecast", "error", "family"]
        frames.append(df[cols])
    all_fc = pd.concat(frames, ignore_index=True)
    return all_fc


def prepare_batch(all_fc: pd.DataFrame, dataset: str, model: str) -> tuple[np.ndarray, np.ndarray, pd.Index]:
    """Stack (series, origin) instances of one (dataset, model) into matrices.

    Rows are sorted by (series_id, origin, forecast_date) so each row is one
    simulated instance; returns (F, A, instance_index).
    Raises if instance lengths differ (batch simulation requires equal n).
    """
    sub = all_fc[(all_fc["dataset"] == dataset) & (all_fc["model"] == model)].copy()
    sub = sub.sort_values(["series_id", "origin", "forecast_date"])
    lens = sub.groupby(["series_id", "origin"]).size()
    if lens.nunique() != 1:
        raise ValueError(f"{dataset}/{model}: unequal instance lengths {sorted(lens.unique())}")
    n = int(lens.iloc[0])
    n_inst = len(lens)
    F = sub["forecast"].to_numpy(dtype=float).reshape(n_inst, n)
    A = sub["actual"].to_numpy(dtype=float).reshape(n_inst, n)
    idx = pd.MultiIndex.from_tuples(lens.index.tolist(), names=["series_id", "origin"])
    return F, A, idx


if __name__ == "__main__":
    # Self-test: scalar vs batch parity (must be bit-identical)
    rng = np.random.default_rng(0)
    np.random.seed(0)
    pols = [
        make_policy(3, 0.90, 3),
        make_policy(7, 0.95, 5),
        make_policy(14, 0.99, 10),
    ]
    all_max = 0.0
    for trial in range(5):
        m = rng.integers(2, 12)
        L = rng.integers(3, 15)
        Fs = rng.integers(0, 30, size=(m, 28)).astype(float)
        As = rng.integers(0, 40, size=(m, 28)).astype(float)
        for p in pols:
            bat = simulate_batch(Fs, As, p)
            for k in range(m):
                sca = simulate_series(Fs[k], As[k], p)
                for key in bat:
                    d = abs(bat[key][k] - sca[key])
                    all_max = max(all_max, float(d))
    ok = all_max < 1e-9
    print(f"[inventory_policy] self-test parity: max |batch - scalar| = {all_max:.3e} "
          f"({'OK (machine precision)' if ok else 'FAIL: diverges'})")