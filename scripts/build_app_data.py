"""Build the small tracked app_data/ extracts. Reproducible, capped, documented.

Reads local (possibly git-ignored) sources, writes only small CSVs:
  datasets.csv, models.csv, representative_series.csv,
  forecasts_sample.csv, sensitivity_compact.csv

Sample: 2 M5 + 2 Store series, origin 1, H28. All forecast families that have
a local all_forecasts file contribute their cached rows for those series.
No training, no refitting, no evidence changes.

Usage (repo root):
  python scripts/build_app_data.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
APP_DATA = ROOT / "app_data"

M5_SERIES = ["FOODS_1_098_CA_3_evaluation", "FOODS_1_133_TX_3_evaluation"]
STORE_SERIES = ["S01_I01", "S01_I02"]
FORECAST_SOURCES = {
    "baselines": "06_results/baselines/all_forecasts.csv",
    "smoothing": "06_results/exponential_smoothing/all_forecasts.csv",
    "croston": "06_results/croston/all_forecasts.csv",
    "arima": "06_results/arima/all_forecasts.csv",
    "lstm": "06_results/lstm/all_forecasts.csv",
}


def _first_existing(series: list, available: set, fallback: list) -> list:
    chosen = [s for s in series if s in available]
    if chosen:
        return chosen[:2]
    return fallback[:2]


def main() -> None:
    APP_DATA.mkdir(exist_ok=True)

    pd.DataFrame(
        [
            {"dataset": "m5", "label": "M5 - sparse / intermittent", "n_series": 500,
             "origins": 8, "horizon": 28, "seed": 42},
            {"dataset": "store_item_demand", "label": "Store Item Demand - dense",
             "n_series": 500, "origins": 8, "horizon": 28, "seed": 42},
        ]
    ).to_csv(APP_DATA / "datasets.csv", index=False)

    pd.DataFrame(
        [
            {"model": "Naive", "family": "Baseline", "applies": "both"},
            {"model": "Seasonal Naive", "family": "Baseline", "applies": "both"},
            {"model": "Moving Average", "family": "Baseline", "applies": "both"},
            {"model": "SES", "family": "Smoothing", "applies": "both"},
            {"model": "DES", "family": "Smoothing", "applies": "both"},
            {"model": "TES", "family": "Smoothing", "applies": "both"},
            {"model": "ARIMA", "family": "Statistical", "applies": "both"},
            {"model": "SARIMA", "family": "Statistical", "applies": "store-only"},
            {"model": "CROSTON", "family": "Intermittent", "applies": "m5-only"},
            {"model": "SBA", "family": "Intermittent", "applies": "m5-only"},
            {"model": "TSB", "family": "Intermittent", "applies": "m5-only"},
            {"model": "LSTM", "family": "Neural", "applies": "both"},
        ]
    ).to_csv(APP_DATA / "models.csv", index=False)

    # Sensitivity grid: already small (540 rows), copy as-is.
    sens = pd.read_csv(ROOT / "06_results/sensitivity/sensitivity_grid.csv")
    sens.to_csv(APP_DATA / "sensitivity_compact.csv", index=False)

    # Forecast samples across families for 2+2 series, origin 1.
    frames = []
    for name, rel in FORECAST_SOURCES.items():
        p = ROOT / rel
        if not p.exists():
            print(f"skip {name}: {rel} not present")
            continue
        usecols = ["dataset", "series_id", "origin_id", "origin_date",
                   "forecast_date", "actual", "forecast", "model"]
        df = pd.read_csv(p, usecols=lambda c: c in usecols or c == "origin")
        if "origin" in df.columns and "origin_id" not in df.columns:
            df = df.rename(columns={"origin": "origin_id"})
        df = df[df["origin_id"] == 1]
        m5ok = _first_existing(M5_SERIES, set(df.loc[df["dataset"] == "m5", "series_id"]), sorted(df.loc[df["dataset"] == "m5", "series_id"].unique().tolist()))
        stkey = "store_item_demand" if "store_item_demand" in set(df["dataset"]) else None
        store_ids = sorted(df.loc[df["dataset"] == stkey, "series_id"].unique().tolist()) if stkey else []
        st_ok = _first_existing(STORE_SERIES, set(store_ids), store_ids)
        df = df[df["series_id"].isin(m5ok + st_ok)]
        frames.append(df)
        print(f"{name}: {len(df)} rows for {m5ok + st_ok}")

    sample = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    sample.to_csv(APP_DATA / "forecasts_sample.csv", index=False)

    rep = (sample[["dataset", "series_id", "origin_id", "origin_date",
                   "forecast_date", "actual"]].drop_duplicates().sort_values(["series_id", "forecast_date"]))
    rep.to_csv(APP_DATA / "representative_series.csv", index=False)

    total = sum((APP_DATA / f).stat().st_size for f in
                ["datasets.csv", "models.csv", "representative_series.csv",
                 "forecasts_sample.csv", "sensitivity_compact.csv"])
    print(f"app_data rows: sens={len(sens)} sample={len(sample)} rep={len(rep)} total_bytes={total}")
    assert total < 2_000_000, f"app_data budget exceeded: {total} bytes"


if __name__ == "__main__":
    main()
