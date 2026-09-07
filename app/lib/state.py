"""Experiment session state + run orchestration for the sandbox views.

Contract: every interactive page reads `st.session_state["exp"]` (a dict or
None). Data Studio builds it; Forecast Lab / Model Arena / Inventory Simulator
/ Policy Lab / Decision Center / Diagnostics / Experiments consume it.

Nothing here touches the frozen research artifacts — sandbox only.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from . import engine as E
from . import models as M
from . import scenarios as S
from .lab import FROZEN, INTERACTIVE, badges

POLICY_KEYS = ("lead_time", "service_target", "H", "P", "sigma_floor")


def exp() -> dict | None:
    return st.session_state.get("exp")


def has_run() -> bool:
    e = exp()
    return bool(e and e.get("fc_long") is not None)


def default_policy() -> dict:
    return dict(E.POLICY_DEFAULT)


def snapshot_winners(e: dict) -> dict:
    """Winners of the current run — used by the scenario log."""
    out = {}
    mets = e.get("metrics_df")
    inv = e.get("inventory_df")
    if mets is not None and len(mets):
        out["best_forecaster"] = str(mets.iloc[mets["MAE"].idxmin()]["model"])
        out["best_MASE"] = str(mets.iloc[mets["MASE"].idxmin()]["model"])
    if inv is not None and len(inv):
        out["lowest_cost"] = str(inv.iloc[inv["total_cost"].idxmin()]["model"])
        out["highest_service"] = str(inv.iloc[inv["service_level"].idxmax()]["model"])
        out["lowest_inventory"] = str(inv.iloc[inv["average_inventory"].idxmin()]["model"])
        out["total_cost"] = round(float(inv["total_cost"].min()), 2)
    return out


def run_models(e: dict) -> None:
    """Forecast + metric stages (cached by streamlit on content hashes)."""
    hist_hash = E.hash_series(e["history"])
    model_list = tuple(e["models"])
    e["fc_long"] = E.run_forecasts(hist_hash, e["history"], e["horizon"], model_list, e["dataset_kind"])
    e["fc_by_model"] = E.pivot_forecasts(e["fc_long"], e["horizon"])
    e["statuses"] = {r.model: r.status for r in E.model_status_table(e["fc_long"]).itertuples()}
    e["metrics_df"] = E.forecast_metrics(hist_hash, E.hash_series(e["actual"]),
                                         e["history"], e["actual"], e["fc_long"])
    e["hist_hash"] = hist_hash


def run_inventory(e: dict) -> None:
    """Inventory stage under the current policy."""
    policy = e["policy"]
    e["inventory_df"] = E.inventory_table(e["fc_by_model"], e["actual"], policy, e["statuses"])


def build_experiment(source: str, dataset: str, dataset_kind: str, series_id: str,
                     series_df: pd.DataFrame, horizon: int, scenario_cfg: dict,
                     model_list: list[str], policy: dict) -> dict:
    """Create/refresh the experiment dict from a (possibly modified) series."""
    demand = series_df["demand"].to_numpy(dtype=float)
    if scenario_cfg:
        demand = S.apply_all(demand, scenario_cfg)
    history, actual = E.split_history_actual(demand, horizon)
    origin_date = series_df["date"].iloc[-horizon]
    e = {
        "source": source,
        "dataset": dataset,
        "dataset_kind": dataset_kind,  # m5 | store_item_demand | custom
        "series_id": series_id,
        "series_df": series_df.assign(demand=demand),
        "horizon": horizon,
        "origin_date": origin_date,
        "scenario_cfg": scenario_cfg,
        "scenario_name": scenario_cfg.get("_name", ""),
        "models": model_list,
        "policy": dict(policy),
        "history": history,
        "actual": actual,
        "exp_id": E.new_experiment_id(),
    }
    run_models(e)
    run_inventory(e)
    e["winners"] = snapshot_winners(e)
    return e


def log_experiment(e: dict) -> None:
    """Append a provenance-stamped sandbox run to the session run log."""
    prov = E.provenance(e["exp_id"], e["dataset"], e["series_id"], e["origin_date"],
                        e["horizon"], e["policy"], e["models"],
                        {"scenario": e["scenario_name"], "source": e["source"]})
    e["provenance"] = prov
    log = st.session_state.setdefault("run_log", [])
    entry = {
        "experiment_id": prov["experiment_id"],
        "mode": "SANDBOX",
        "timestamp": prov["timestamp"],
        "dataset": prov["dataset"],
        "series_id": prov["series_id"],
        "origin_date": prov["origin_date"],
        "horizon": prov["horizon"],
        "policy": prov["policy"],
        "models": prov["models"],
        "scenario": e["scenario_name"],
        "winners": e["winners"],
    }
    log.insert(0, entry)
    st.session_state["log"] = log


def rerun_with(e: dict, new_series_df: pd.DataFrame | None = None,
               scenario_cfg: dict | None = None,
               model_list: list[str] | None = None,
               policy: dict | None = None) -> dict:
    """Rebuild the experiment after any change (data, scenario, models, policy)."""
    e = dict(e)
    if new_series_df is not None:
        e["series_df"] = new_series_df
    if scenario_cfg is not None:
        e["scenario_cfg"] = scenario_cfg
        e["scenario_name"] = scenario_cfg.get("_name", "")
    if model_list is not None:
        e["models"] = model_list
    if policy is not None:
        e["policy"] = dict(policy)
    demand = e["series_df"]["demand"].to_numpy(dtype=float)
    if e["scenario_cfg"]:
        demand = S.apply_all(demand, e["scenario_cfg"])
    e["series_df"] = e["series_df"].assign(demand=demand)
    e["history"], e["actual"] = E.split_history_actual(demand, e["horizon"])
    e["exp_id"] = E.new_experiment_id()
    run_models(e)
    run_inventory(e)
    e["winners"] = snapshot_winners(e)
    return e


def sandbox_badges() -> None:
    badges(("SANDBOX — not research evidence", "live"),
           ("frozen benchmark untouched", "frozen"))


def sandbox_gate(page_title: str) -> dict:
    """Every sandbox page calls this first: stops with a CTA if no experiment."""
    e = exp()
    if not has_run():
        st.markdown('<div class="empty">No experiment yet — open <b>Data Studio</b>, '
                    'pick a series (or upload a CSV), and apply a configuration. '
                    f'Then <b>{page_title}</b> fills in automatically.</div>', unsafe_allow_html=True)
        st.stop()
    return e


# ---------------------------------------------------------------------------
# Winner logic — never collapsed; each objective is its own answer
# ---------------------------------------------------------------------------

WINNER_OBJECTIVES = {
    "Best Forecaster": ("metrics_df", "MAE", "min"),
    "Lowest Inventory Cost": ("inventory_df", "total_cost", "min"),
    "Highest Service": ("inventory_df", "service_level", "max"),
    "Lowest Inventory": ("inventory_df", "average_inventory", "min"),
}


def objective_winner(e: dict, objective: str) -> tuple[str | None, float | None]:
    table, col, mode = WINNER_OBJECTIVES[objective]
    df = e.get(table)
    if df is None or not len(df) or col not in df.columns:
        return None, None
    r = df[col].idxmin() if mode == "min" else df[col].idxmax()
    return str(df.loc[r, "model"]), float(df.loc[r, col])


def constraints_winner(e: dict, cons: dict) -> tuple[str | None, pd.DataFrame]:
    """Best model under user pass/fail constraints.

    cons keys (all optional, None = not used):
      max_cost, min_service, max_mase, max_avg_inventory, max_runtime
    Ranking within passing models: total_cost ascending (tie → service desc).
    """
    inv = e.get("inventory_df")
    mets = e.get("metrics_df")
    if inv is None or mets is None or not len(inv):
        return None, pd.DataFrame()
    df = inv.merge(mets[["model", "MASE"]], on="model", how="left")
    df["runtime_s"] = df["model"].map(
        {r.model: r.runtime_s for r in E.model_status_table(e["fc_long"]).itertuples()})
    df["PASS"] = True
    if cons.get("max_cost") is not None:
        df["PASS"] &= df["total_cost"] <= cons["max_cost"]
    if cons.get("min_service") is not None:
        df["PASS"] &= df["service_level"] >= cons["min_service"]
    if cons.get("max_mase") is not None:
        df["PASS"] &= df["MASE"].fillna(np.inf) <= cons["max_mase"]
    if cons.get("max_avg_inventory") is not None:
        df["PASS"] &= df["average_inventory"] <= cons["max_avg_inventory"]
    if cons.get("max_runtime") is not None:
        df["PASS"] &= df["runtime_s"].fillna(np.inf) <= cons["max_runtime"]
    ok = df[df["PASS"]]
    if not len(ok):
        return None, df
    best = ok.sort_values(["total_cost", "service_level"], ascending=[True, False]).iloc[0]
    return str(best["model"]), df
