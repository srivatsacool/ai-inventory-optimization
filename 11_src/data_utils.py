"""Data audit helpers — lightweight, dataset-agnostic checks used in NB 02.

These are intentionally simple functions that notebooks call and explain.
They do not hide logic; they just avoid copy-pasting the same 20 lines.
"""
from __future__ import annotations

import pathlib
import pandas as pd
import numpy as np


def date_range_info(dates: pd.Series) -> dict:
    s = pd.to_datetime(dates)
    return {
        "min": s.min(),
        "max": s.max(),
        "n_unique": s.nunique(),
        "n_days_span": (s.max() - s.min()).days + 1,
        "missing_days": (s.max() - s.min()).days + 1 - s.nunique(),
    }


def overlap_window(a_start, a_end, b_start, b_end):
    """Return (overlap_start, overlap_end, n_days) for two date ranges."""
    a_start, a_end = pd.Timestamp(a_start), pd.Timestamp(a_end)
    b_start, b_end = pd.Timestamp(b_start), pd.Timestamp(b_end)
    o_start = max(a_start, b_start)
    o_end = min(a_end, b_end)
    n_days = (o_end - o_start).days + 1 if o_end >= o_start else 0
    return o_start, o_end, n_days


def demand_profile(y: np.ndarray) -> dict:
    """Quick Syntetos-Boylan style profile for one series."""
    y = np.asarray(y, float)
    n = len(y)
    n_zeros = int((y == 0).sum())
    zero_share = n_zeros / n if n else float("nan")
    # ADI = avg interval between non-zero demands; CV2 = (std/mean)^2 for non-zeros
    nz_idx = np.where(y > 0)[0]
    if len(nz_idx) < 2:
        adi = float("nan")
    else:
        adi = float(np.mean(np.diff(nz_idx)) + 1)  # +1 so consecutive days → 1, not 0
    nz = y[y > 0]
    if len(nz) < 2 or nz.mean() == 0:
        cv2 = float("nan")
    else:
        cv2 = float((nz.std(ddof=1) / nz.mean()) ** 2)
    return {
        "n": n,
        "mean": float(y.mean()) if n else float("nan"),
        "std": float(y.std(ddof=1)) if n > 1 else float("nan"),
        "zero_share": float(zero_share),
        "ADI": adi,
        "CV2": cv2,
    }


def file_hash(path: pathlib.Path, n_bytes: int = 1_000_000) -> str:
    """Fast hash of first n_bytes (enough to fingerprint dataset versions)."""
    import hashlib

    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read(n_bytes))
    return h.hexdigest()[:16]
