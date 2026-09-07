"""Interactive experiment engine.

Bridges the sandbox to the frozen research modules:
- 11_src/inventory_policy.py  (order-up-to simulator — imported, never copied)
- 11_src/metrics.py           (MAE/RMSE/MASE/RMSSE/WAPE/sMAPE — imported)
- app/lib/models.py           (forecast models lifted verbatim from notebooks)

Every function here is pure (deterministic, no st.* calls) so Streamlit's
@st.cache_data can memoise them. The views layer owns session_state and the
run log; nothing in this module writes to disk.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import importlib.util
import pathlib
import time
import uuid

import numpy as np
import pandas as pd
import streamlit as st

from . import models as M

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _load_research_module(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "11_src" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_inventory_policy = _load_research_module("inventory_policy")
_research_metrics = _load_research_module("metrics")

POLICY_DEFAULT = dict(_inventory_policy.POLICY_DEFAULT)
GRID_LEADS = [3, 7, 14]
GRID_TARGETS = [0.90, 0.95, 0.99]
GRID_P = [3, 5, 10]  # H fixed at 1.0 → P == P/H ratio (research convention)

# ---------------------------------------------------------------------------
# Built-in data (derived extract — never touches frozen files)
# ---------------------------------------------------------------------------


@st.cache_data(show_spinner=False)
def load_catalog() -> pd.DataFrame:
    """One row per built-in series with quick profile stats."""
    df = pd.read_parquet(ROOT / "app_data" / "interactive_series.parquet")
    g = df.groupby(["dataset", "series_id"])["demand"]
    cat = g.agg(["size", "mean", "std", "max"]).reset_index()
    cat["zero_rate"] = g.apply(lambda s: float((s == 0).mean())).values
    cat = cat.rename(columns={"size": "n_days", "mean": "mean_demand"})
    cat["dataset_label"] = cat["dataset"].map({"m5": "M5", "store_item_demand": "Store Item Demand"})
    return cat


@st.cache_data(show_spinner=False)
def get_series(dataset: str, series_id: str) -> pd.DataFrame:
    df = pd.read_parquet(ROOT / "app_data" / "interactive_series.parquet")
    s = df[(df.dataset == dataset) & (df.series_id == series_id)].sort_values("date")
    s = s[["date", "demand"]].reset_index(drop=True)
    s["date"] = pd.to_datetime(s["date"])
    return s


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def hash_series(series: np.ndarray) -> str:
    return hashlib.blake2b(np.asarray(series, dtype=float).tobytes(), digest_size=12).hexdigest()


def split_history_actual(demand: np.ndarray, horizon: int = M.HORIZON):
    """Last `horizon` days are the evaluation window; the rest is history."""
    demand = np.asarray(demand, dtype=float)
    assert len(demand) > horizon, "series too short for the evaluation horizon"
    return demand[:-horizon], demand[-horizon:]


def new_experiment_id() -> str:
    return f"EXP-{uuid.uuid4().hex[:6].upper()}"


def provenance(exp_id: str, dataset: str, series_id: str, origin_date, horizon: int,
               policy: dict, model_list: list[str], config: dict) -> dict:
    return {
        "experiment_id": exp_id,
        "mode": "SANDBOX",
        "dataset": dataset,
        "series_id": series_id,
        "origin_date": str(origin_date),
        "horizon": horizon,
        "policy": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in policy.items()},
        "models": list(model_list),
        "config": config,
        "timestamp": _dt.datetime.now().isoformat(timespec="seconds"),
    }


# ---------------------------------------------------------------------------
# Forecast stage
# ---------------------------------------------------------------------------


@st.cache_data(show_spinner="Fitting models…")
def run_forecasts(hist_hash: str, history: np.ndarray, horizon: int,
                  model_list: tuple[str, ...], dataset: str) -> pd.DataFrame:
    """Run each model on the same leakage-free history.

    Returns long DataFrame: model, h (1..horizon), yhat, runtime_s, status, status_note.
    """
    rows = []
    for name in model_list:
        fn = M.MODEL_LADDER[name]["func"]
        kwargs = {}
        if name == "Moving Average":
            kwargs = {"dataset": dataset}
        avail, avail_note = M.model_available(name)
        if not avail:
            rows.extend({"model": name, "h": h + 1, "yhat": 0.0, "runtime_s": 0.0,
                         "status": "unavailable", "status_note": avail_note}
                        for h in range(horizon))
            continue
        t0 = time.perf_counter()
        status, note = "ok", ""
        conv: dict = {}
        try:
            if name in ("ARIMA", "SARIMA"):
                yhat = fn(history, horizon=horizon, conv=conv)
                if conv.get("status", "fit_ok") != "fit_ok":
                    status, note = "fallback", conv.get("reason", conv.get("status", ""))
            else:
                yhat = fn(history, horizon=horizon, **kwargs)
            yhat = np.asarray(yhat, dtype=float)
            if not np.all(np.isfinite(yhat)):
                raise ValueError("non-finite forecast")
        except Exception as e:  # sandbox must never crash on one model
            status, note = "error", f"{type(e).__name__}: {e}"
            yhat = np.zeros(horizon)
        runtime = time.perf_counter() - t0
        for h in range(horizon):
            rows.append({"model": name, "h": h + 1, "yhat": float(yhat[h]),
                         "runtime_s": runtime, "status": status, "status_note": note})
    return pd.DataFrame(rows)


def pivot_forecasts(fc_long: pd.DataFrame, horizon: int) -> dict[str, np.ndarray]:
    out = {}
    for name, g in fc_long.groupby("model", sort=False):
        arr = np.empty((horizon, len(g)))
        arr[:] = np.nan
        arr[g["h"].to_numpy() - 1, 0] = g["yhat"].to_numpy()
        out[name] = arr[:, 0]
    return out


def model_status_table(fc_long: pd.DataFrame) -> pd.DataFrame:
    return (fc_long.groupby("model", sort=False)
            .agg(status=("status", "first"), status_note=("status_note", "first"),
                 runtime_s=("runtime_s", "first"))
            .reset_index())


# ---------------------------------------------------------------------------
# Metrics stage (reuse 11_src/metrics.py)
# ---------------------------------------------------------------------------


@st.cache_data(show_spinner=False)
def forecast_metrics(hist_hash: str, actual_hash: str, history: np.ndarray, actual: np.ndarray,
                     _fc_long: pd.DataFrame) -> pd.DataFrame:
    """Per-model forecast metrics via the frozen research metrics module.

    Keyed on content hashes; _fc_long is derived from the same inputs.
    """
    actual = np.asarray(actual, dtype=float)
    rows = []
    ok = _fc_long[_fc_long["status"] != "unavailable"]
    for name, g in ok.groupby("model", sort=False):
        yhat = g.sort_values("h")["yhat"].to_numpy()
        m = _research_metrics.all_metrics(actual, yhat, y_train=history, seasonal_period=M.SEASON)
        m = {"MAE": m["MAE"], "RMSE": m["RMSE"], "MASE": m["MASE"], "RMSSE": m["RMSSE"],
             "WAPE": m["WAPE"], "sMAPE": m["sMAPE"]}
        rows.append({"model": name, **m})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Inventory stage (reuse 11_src/inventory_policy.py)
# ---------------------------------------------------------------------------


def inventory_result(fc: np.ndarray, actual: np.ndarray, policy: dict) -> dict:
    return _inventory_policy.simulate_series(np.asarray(fc, dtype=float),
                                             np.asarray(actual, dtype=float), policy)


def inventory_table(fc_by_model: dict[str, np.ndarray], actual: np.ndarray,
                    policy: dict, statuses: dict[str, str] | None = None) -> pd.DataFrame:
    rows = []
    for name, fc in fc_by_model.items():
        if statuses and statuses.get(name) in ("error", "unavailable"):
            continue
        r = inventory_result(fc, actual, policy)
        rows.append({"model": name, **r})
    df = pd.DataFrame(rows)
    if len(df):
        df["family"] = df["model"].map(lambda m: M.MODEL_LADDER[m]["family"])
    return df


def simulation_chain(fc: np.ndarray, actual: np.ndarray, policy: dict) -> dict:
    """Recompute the order-up-to chain step by step for the 'Show calculation' expanders.

    Mirrors 11_src/inventory_policy.simulate_series exactly and records the
    intermediate quantities the research simulator computes internally.
    """
    p = _inventory_policy.resolve_policy(policy)
    L, z, H, P, floor = p["lead_time"], p["z"], p["H"], p["P"], p["sigma_floor"]
    fc = np.asarray(fc, dtype=float)
    act = np.asarray(actual, dtype=float)
    n = len(fc)
    err = fc - act
    err_std = max(float(np.std(err)), floor)
    ss = z * err_std * np.sqrt(L)
    initial_inventory = max(float(np.sum(fc[:L])), 1.0)
    pipeline = np.zeros(L)
    inv = initial_inventory
    days = []
    h_cost = s_cost = reorders = 0.0
    s_days = 0
    for d in range(n):
        inv += pipeline[0]
        pipeline = np.roll(pipeline, -1)
        pipeline[-1] = 0
        lead_demand = float(np.sum(fc[d:min(d + L, n)]))
        ord_up = lead_demand + ss
        inv_pos = inv + float(np.sum(pipeline))
        order = 0.0
        if inv_pos < ord_up:
            order = max(0.0, ord_up - inv_pos)
            pipeline[-1] = order
            reorders += 1
        dem = act[d]
        served = short = 0.0
        if dem > 0:
            served = min(inv, dem)
            short = dem - served
            inv -= served
            if short > 0:
                s_days += 1
        h_cost += H * inv
        s_cost += P * short
        days.append({"day": d + 1, "demand": float(dem), "received": float(pipeline[0]) if d > 0 else 0.0,
                     "start_inventory": inv + served, "lead_time_demand": lead_demand,
                     "order_up_to": ord_up, "inventory_position": inv_pos, "order": order,
                     "end_inventory": inv, "shortage": short})
    return {
        "err_std": err_std, "safety_stock": ss, "z": z, "lead_time": L,
        "initial_inventory": initial_inventory,
        "avg_lead_time_demand": float(np.mean([np.sum(fc[d:min(d + L, n)]) for d in range(n)])),
        "total_holding_cost": h_cost, "total_stockout_cost": s_cost,
        "total_cost": h_cost + s_cost,
        "service_level": 1 - s_days / n,
        "average_inventory": h_cost / n,
        "stockout_days": s_days, "stockout_quantity": float(sum(d["shortage"] for d in days)),
        "reorder_count": int(reorders),
        "days": pd.DataFrame(days),
    }


# ---------------------------------------------------------------------------
# Policy grid (research 27-cell definition; custom cells welcome)
# ---------------------------------------------------------------------------


@st.cache_data(show_spinner="Simulating policies…")
def policy_grid(actual_hash: str, fc_by_model_json: str,
                actual: np.ndarray, policies: tuple[tuple, ...]) -> pd.DataFrame:
    """Run every (model × policy) cell.

    policies: tuple of policy dicts (as tuples of items for hashability).
    """
    fc_by_model = {name: np.asarray(vals) for name, vals in _json_to_arrays(fc_by_model_json).items()}
    pols = [dict(p) for p in policies]
    rows = []
    for pname, fc in fc_by_model.items():
        for pi, pol in enumerate(pols):
            r = _inventory_policy.simulate_series(fc, np.asarray(actual, dtype=float), pol)
            rows.append({"model": pname, "policy_id": pi, **{k: pol[k] for k in ("lead_time", "service_target", "P", "H")},
                         **r})
    return pd.DataFrame(rows)


def _json_to_arrays(s: str) -> dict:
    import json

    return json.loads(s)


def arrays_to_json(fc_by_model: dict[str, np.ndarray]) -> str:
    import json

    return json.dumps({k: [round(float(x), 6) for x in v] for k, v in fc_by_model.items()})


def default_policy_grid() -> tuple[tuple, ...]:
    """The frozen 27-cell research grid (L × service × P, H=1)."""
    cells = []
    for L in GRID_LEADS:
        for sv in GRID_TARGETS:
            for P in GRID_P:
                pol = _inventory_policy.make_policy(L, sv, P)
                cells.append(tuple(sorted(pol.items())))
    return tuple(cells)


def custom_policy_cells(lead_times, service_targets, p_over_h) -> tuple[tuple, ...]:
    cells = []
    for L in lead_times:
        for sv in service_targets:
            for P in p_over_h:
                cells.append(tuple(sorted(_inventory_policy.make_policy(int(L), float(sv), float(P)).items())))
    return tuple(cells)
