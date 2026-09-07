#!/usr/bin/env python
"""Build app_data/interactive_series.parquet for the Interactive Experiment sandbox.

READ-ONLY with respect to every frozen research artifact: this script only ever
*reads* 02_data/ files and *writes* one new derived file in app_data/.

Extract contents
----------------
- M5: the 500 research-selected series (05_experiments/m5_series_selection.json)
  from 02_data/dataset_01_m5/raw/sales_train_evaluation.csv, common window
  2013-01-01 .. 2016-05-22 (1,238 days, same as the research common window).
- Store Item Demand: the 500 series from
  02_data/dataset_02_store_item_demand/processed/store_item_demand_daily.parquet,
  same common window.

Output schema (long format): dataset, series_id, date, demand.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
WIN_START = pd.Timestamp("2013-01-01")
WIN_END = pd.Timestamp("2016-05-22")
OUT = ROOT / "app_data" / "interactive_series.parquet"


def build_m5() -> pd.DataFrame:
    sel = json.loads((ROOT / "05_experiments" / "m5_series_selection.json").read_text())
    ids_val = sel["m5_series"]
    ids_eval = [s.replace("_validation", "_evaluation") for s in ids_val]

    raw = pd.read_csv(ROOT / "02_data" / "dataset_01_m5" / "raw" / "sales_train_evaluation.csv")
    raw = raw.set_index("id").loc[ids_eval]

    d_cols = [c for c in raw.columns if c.startswith("d_")]
    d_to_date = pd.Timestamp("2011-01-29") + pd.to_timedelta(
        [int(c[2:]) - 1 for c in d_cols], unit="D"
    )
    keep = [c for c, dt in zip(d_cols, d_to_date) if WIN_START <= dt <= WIN_END]
    keep_dates = [dt for dt in d_to_date if WIN_START <= dt <= WIN_END]
    assert len(keep) == 1238, f"M5 window is {len(keep)} days, expected 1238"

    wide = raw[keep]
    wide.columns = pd.DatetimeIndex(keep_dates, name="date")
    long = (
        wide.stack(future_stack=True)
        .rename("demand")
        .rename_axis(index=["series_id", "date"])
        .reset_index()
    )
    long["dataset"] = "m5"
    return long[["dataset", "date", "series_id", "demand"]]


def build_store() -> pd.DataFrame:
    daily = pd.read_parquet(
        ROOT / "02_data" / "dataset_02_store_item_demand" / "processed" / "store_item_demand_daily.parquet"
    )
    daily["date"] = pd.to_datetime(daily["date"])
    m = daily[(daily["date"] >= WIN_START) & (daily["date"] <= WIN_END)].copy()
    m["series_id"] = (
        "S" + m["store"].astype(int).astype(str).str.zfill(2)
        + "_I" + m["item"].astype(int).astype(str).str.zfill(2)
    )  # benchmark id convention used by 06_results forecast CSVs
    m["dataset"] = "store_item_demand"
    return m.rename(columns={"sales": "demand"})[["dataset", "date", "series_id", "demand"]]


def main() -> None:
    m5 = build_m5()
    store = build_store()
    out = pd.concat([m5, store], ignore_index=True)
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    out.to_parquet(OUT, index=False)
    print(f"wrote {OUT} rows={len(out):,} series={out.series_id.nunique():,}")
    print(out.groupby("dataset")["series_id"].nunique())


if __name__ == "__main__":
    main()
