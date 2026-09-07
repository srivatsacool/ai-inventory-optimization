"""Demand scenario transforms for the Interactive Experiment sandbox.

All transforms are pure functions on a demand array and return a new array
(never mutate the input). Transforms are seeded so the same configuration
always produces the same series.
"""
from __future__ import annotations

import numpy as np


def apply_level(demand: np.ndarray, multiplier: float) -> np.ndarray:
    return np.maximum(np.asarray(demand, dtype=float) * multiplier, 0.0)


def apply_trend(demand: np.ndarray, per_day: float, ramp_days: int = 90) -> np.ndarray:
    """Add a linear ramp of ±per_day units/day over the last `ramp_days` days."""
    d = np.asarray(demand, dtype=float).copy()
    n = len(d)
    k = min(ramp_days, n)
    ramp = per_day * np.arange(1, k + 1)
    d[-k:] = np.maximum(d[-k:] + ramp, 0.0)
    return d


def apply_seasonality(demand: np.ndarray, amplitude: float) -> np.ndarray:
    """Amplify/dampen the weekly pattern: series + (amplitude-1) * weekly anomaly."""
    d = np.asarray(demand, dtype=float).copy()
    n = len(d)
    if n < 14:
        return d
    week_idx = np.arange(n) % 7
    week_mean = np.array([d[week_idx == w].mean() for w in range(7)])
    overall = d.mean()
    anomaly = week_mean[week_idx] - overall
    return np.maximum(d + (amplitude - 1.0) * anomaly, 0.0)


def apply_volatility(demand: np.ndarray, scale: float, seed: int = 42) -> np.ndarray:
    """Multiplicative noise: d * N(1, scale), clipped at 0."""
    rng = np.random.default_rng(seed)
    d = np.asarray(demand, dtype=float)
    noise = rng.normal(1.0, scale, size=len(d))
    return np.maximum(d * noise, 0.0)


def apply_intermittency(demand: np.ndarray, zero_rate: float, seed: int = 42) -> np.ndarray:
    """Zero out positive days (largest-first removal would bias; use seeded random
    selection) until the series reaches the requested zero-demand rate."""
    rng = np.random.default_rng(seed)
    d = np.asarray(demand, dtype=float).copy()
    pos = np.where(d > 0)[0]
    current = float((d == 0).mean())
    n_to_zero = int(round(zero_rate * len(d) - current * len(d)))
    if n_to_zero <= 0:
        return d
    n_to_zero = min(n_to_zero, len(pos))
    kill = rng.choice(pos, size=n_to_zero, replace=False)
    d[kill] = 0.0
    return d


def apply_shock(demand: np.ndarray, kind: str, factor: float, window: int = 14) -> np.ndarray:
    """Demand spike or drop over the last `window` days (the evaluation zone)."""
    d = np.asarray(demand, dtype=float).copy()
    k = min(window, len(d))
    if kind == "spike":
        d[-k:] = d[-k:] * factor
    elif kind == "drop":
        d[-k:] = d[-k:] * factor  # factor < 1
    else:
        raise ValueError(kind)
    return np.maximum(d, 0.0)


def apply_all(demand: np.ndarray, cfg: dict, seed: int = 42) -> np.ndarray:
    """Apply scenario controls in a fixed order. Unknown keys are ignored."""
    d = np.asarray(demand, dtype=float)
    if cfg.get("level", 1.0) != 1.0:
        d = apply_level(d, cfg["level"])
    if cfg.get("trend_per_day", 0.0):
        d = apply_trend(d, cfg["trend_per_day"])
    if cfg.get("seasonality", 1.0) != 1.0:
        d = apply_seasonality(d, cfg["seasonality"])
    if cfg.get("volatility", 0.0):
        d = apply_volatility(d, cfg["volatility"], seed)
    if cfg.get("zero_rate", None) is not None and cfg["zero_rate"] > 0:
        d = apply_intermittency(d, cfg["zero_rate"], seed)
    if cfg.get("shock_kind") in ("spike", "drop"):
        d = apply_shock(d, cfg["shock_kind"], cfg.get("shock_factor", 2.0))
    return d


# Named demo scenarios for the Scenario engine (demand-side only; policy-side
# changes — lead time / service target / P-H ratio — are made in Policy Lab and
# the Inventory Simulator, which re-run everything automatically).
SCENARIOS: dict[str, dict] = {
    "Baseline (no change)": {},
    "Demand spike (+50% last 2 weeks)": {"shock_kind": "spike", "shock_factor": 1.5},
    "Demand drop (-40% last 2 weeks)": {"shock_kind": "drop", "shock_factor": 0.6},
    "Higher volatility (σ = 0.4)": {"volatility": 0.4},
    "More intermittent (zero rate +15pp)": {"zero_rate": 0.45},
    "Level shift ×1.5": {"level": 1.5},
    "Rising trend (+0.3/day)": {"trend_per_day": 0.3},
    "Stronger weekly seasonality (×1.5)": {"seasonality": 1.5},
}
