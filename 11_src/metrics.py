"""Forecast accuracy metrics — transparent, leakage-free, well-documented.

All metrics are computed per-series then averaged (never pooled before scaling).
Seasonal period defaults to 7 (weekly retail seasonality) but is explicit.
"""
from __future__ import annotations

import numpy as np


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    mask = np.isfinite(y_true) & np.isfinite(y_pred)
    if mask.sum() == 0:
        return float("nan")
    return float(np.mean(np.abs(y_true[mask] - y_pred[mask])))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    mask = np.isfinite(y_true) & np.isfinite(y_pred)
    if mask.sum() == 0:
        return float("nan")
    return float(np.sqrt(np.mean((y_true[mask] - y_pred[mask]) ** 2)))


def rmsse(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_train: np.ndarray,
    seasonal_period: int = 7,
) -> float:
    """RMSSE (M5 competition metric).

    RMSE(model) / RMSE(seasonal-naive in-sample one-step errors).
    Returns NaN if the denominator is zero (constant training series).
    """
    y_true = np.asarray(y_true, float)
    y_pred = np.asarray(y_pred, float)
    y_train = np.asarray(y_train, float)

    num = rmse(y_true, y_pred)
    if len(y_train) <= seasonal_period:
        return float("nan")
    naive_errors = y_train[seasonal_period:] - y_train[:-seasonal_period]
    denom = float(np.sqrt(np.mean(naive_errors**2)))
    if denom == 0 or not np.isfinite(denom):
        return float("nan")
    return float(num / denom)


def mase(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_train: np.ndarray,
    seasonal_period: int = 1,
) -> float:
    """MASE (Hyndman & Koehler, 2006)."""
    y_true = np.asarray(y_true, float)
    y_pred = np.asarray(y_pred, float)
    y_train = np.asarray(y_train, float)
    num = mae(y_true, y_pred)
    if len(y_train) <= seasonal_period:
        return float("nan")
    naive_errors = np.abs(y_train[seasonal_period:] - y_train[:-seasonal_period])
    denom = float(np.mean(naive_errors))
    if denom == 0 or not np.isfinite(denom):
        return float("nan")
    return float(num / denom)


def smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Symmetric MAPE (as percentage).

    Zero limitation: pairs where *both* actual and forecast are zero are
    excluded from the mean (their contribution is 0/0). The metric is
    therefore NaN when all pairs are zero-zero, and on intermittent series
    (many both-zero days) the reported value is an average over the
    informative non-zero pairs only — it can look artificially good and is
    not directly comparable with dense series. Use MASE/RMSSE (scale-free)
    or WAPE (zero-aware denominator) alongside it for sparse demand.
    """
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    denom = (np.abs(y_true) + np.abs(y_pred)) / 2
    mask = denom != 0
    if mask.sum() == 0:
        return float("nan")
    return float(100 * np.mean(np.abs(y_true[mask] - y_pred[mask]) / denom[mask]))


def wape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Weighted Absolute Percentage Error (sum|actual-forecast| / sum|actual|).

    Scale-free like MASE/RMSSE, but driven by the *absolute* actual level:
    a unit error on a high-demand day weighs less than on a low-demand day.

    Zero limitation: the denominator is total actual demand, so WAPE is NaN
    when all actuals in the window are zero (a zero-demand origin on an
    intermittent series) — and the metric is *inflated* by any non-zero
    forecast on zero-actual days (each such unit contributes 1.0 to the
    numerator while adding nothing to the denominator). Notebooks that add
    an epsilon (`+1e-9`) to keep it finite silently understate the error,
    more so the sparser the window is. Prefer this NaN-honest version.
    """
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    mask = np.isfinite(y_true) & np.isfinite(y_pred)
    if mask.sum() == 0:
        return float("nan")
    denom = float(np.sum(np.abs(y_true[mask])))
    if denom == 0:
        return float("nan")
    return float(np.sum(np.abs(y_true[mask] - y_pred[mask])) / denom)


# Convenient bundle
def all_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_train: np.ndarray | None = None,
    seasonal_period: int = 7,
) -> dict[str, float]:
    out: dict[str, float] = {
        "MAE": mae(y_true, y_pred),
        "RMSE": rmse(y_true, y_pred),
        "sMAPE": smape(y_true, y_pred),
        "WAPE": wape(y_true, y_pred),
    }
    if y_train is not None:
        out["RMSSE"] = rmsse(y_true, y_pred, y_train, seasonal_period)
        out["MASE"] = mase(y_true, y_pred, y_train, seasonal_period)
    return out
