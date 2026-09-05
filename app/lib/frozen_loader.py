"""Frozen-evidence loader. READ-ONLY.

Every path here must be a file tracked at tag v1.0-evidence-freeze
(verify with: git ls-files <path>). If a file is not tracked at the frozen
head, it must NOT be added here - use app.lib.appdata_loader instead.

Locked thesis (asserted on load, tolerance 1e-3 relative):
  M5 forecast winner   : LSTM  MASE 1.3162
  Store forecast winner: LSTM  MASE 0.9776
  M5 inventory winner  : LSTM  cost 152.83 (25/27 policy wins)
  Store inventory winner: Moving Average cost 2084.50

Known local pitfall: 06_results/scale_free_metrics/summary.csv exists locally
but still carries the OLD Store SARIMA subset row (MASE 1.0688, n=100). The
frozen source of truth for SARIMA full-500 is the number sheet row
SF-store_item_demand-SARIMA-MASE = 1.0546. This loader reads the number sheet,
never summary.csv.
"""

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]

FROZEN_FILES = {
    "number_sheet": "09_reports/final/data/final_number_sheet.csv",
    "inventory_by_model": "06_results/inventory/inventory_by_model.csv",
    "forecast_vs_inventory": "06_results/inventory/inventory_comparison_with_forecasting.csv",
    "figure_audit": "09_reports/final/data/figure_audit.csv",
    "claim_traceability": "09_reports/final/traceability/claim_traceability.csv",
    "protocol_doc": "docs/research/experiment-protocol.md",
    "fig_cost": "07_figures/inventory/01_total_cost_comparison.png",
    "fig_service": "07_figures/inventory/02_service_level_comparison.png",
    "fig_leaderboard": "09_reports/final/figures/F-NEW-01-combined-mase-leaderboard.png",
}

# metric_id -> expected value in the tracked number sheet
THESIS_ROWS = {
    "SF-m5-LSTM-MASE": 1.3162,
    "SF-store_item_demand-LSTM-MASE": 0.977554,
    "SF-store_item_demand-SARIMA-MASE": 1.054558,
    "INV-m5-LSTM-cost": 152.832676,
    "INV-store_item_demand-Moving Average-cost": 2084.501383,
    "INV-store_item_demand-LSTM-cost": 2247.463483,
    "SENS-m5-LSTM-wins": 25.0,
}

THESIS_TEXT = (
    "LSTM wins forecast accuracy on both datasets "
    "(M5 MASE 1.316, Store MASE 0.978); "
    "Moving Average wins Store inventory cost (2084.50 vs LSTM 2247.46) "
    "under the default policy L7 / 95% / H=1 / P=5."
)


def frozen_path(key: str) -> Path:
    return REPO_ROOT / FROZEN_FILES[key]


def check_all_present() -> dict:
    return {k: frozen_path(k).exists() for k in FROZEN_FILES}


def load_number_sheet() -> pd.DataFrame:
    return pd.read_csv(frozen_path("number_sheet"))


def load_inventory_by_model() -> pd.DataFrame:
    return pd.read_csv(frozen_path("inventory_by_model"))


def load_forecast_vs_inventory() -> pd.DataFrame:
    return pd.read_csv(frozen_path("forecast_vs_inventory"))


def verify_thesis(df: pd.DataFrame | None = None) -> dict:
    """Compare locked thesis values against the tracked number sheet."""
    df = load_number_sheet() if df is None else df
    out = {}
    for metric_id, expected in THESIS_ROWS.items():
        hit = df.loc[df["metric_id"] == metric_id, "value"]
        if hit.empty:
            out[metric_id] = {"ok": False, "detail": "row missing"}
            continue
        got = float(hit.iloc[0])
        ok = abs(got - expected) <= max(1e-3, abs(expected) * 1e-3)
        out[metric_id] = {"ok": ok, "got": got, "expected": expected}
    return out


def thesis_ok() -> bool:
    return all(v.get("ok") for v in verify_thesis().values())
