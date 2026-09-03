#!/usr/bin/env python
"""Unified M5 demand-archetype comparison across ALL models (Step 7).

Joins every family's metrics_by_series (M5 rows) to the frozen archetype
profile (02_data/dataset_01_m5/processed/m5_series_profile.csv) on series_id,
so archetype labels are identical for every model (no per-notebook drift).

Outputs:
  06_results/archetype_comparison/archetype_metrics.csv
    (model, archetype, n_series, MAE, RMSE, sMAPE, WAPE, MASE, RMSSE)
  07_figures/archetype_comparison/mae_by_archetype.png
  07_figures/archetype_comparison/wape_by_archetype.png
"""
from __future__ import annotations

import pathlib
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "11_src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from plotting import apply_style

apply_style()
ROOT = pathlib.Path(__file__).resolve().parents[1]
RES = ROOT / "06_results" / "archetype_comparison"
FIG = ROOT / "07_figures" / "archetype_comparison"
RES.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

prof = pd.read_csv(ROOT / "02_data" / "dataset_01_m5" / "processed" / "m5_series_profile.csv")
prof["id_eval"] = prof["item_id"].astype(str) + "_" + prof["store_id"].astype(str) + "_evaluation"
amap = dict(zip(prof["id_eval"], prof["archetype"]))
print("archetype distribution in profile:")
print(prof["archetype"].value_counts().to_string())

frames = []
for fam in ["baselines", "exponential_smoothing", "arima", "lstm", "croston"]:
    ms = pd.read_csv(ROOT / "06_results" / fam / "metrics_by_series.csv")
    ms = ms[ms["dataset"] == "m5"].copy()
    ms["archetype"] = ms["series_id"].map(amap)
    missing = int(ms["archetype"].isna().sum())
    assert missing == 0, f"{fam}: {missing} series without archetype"
    frames.append(ms)
all_m = pd.concat(frames, ignore_index=True)

agg = (all_m.groupby(["model", "archetype"])
       .agg(n_series=("series_id", "size"), MAE=("MAE", "mean"), RMSE=("RMSE", "mean"),
            MASE=("MASE", "mean"), RMSSE=("RMSSE", "mean"))
       .reset_index())

# WAPE/sMAPE are pooled (ratio/sum over all rows in the cell), NOT means of
# per-series ratios: a Highly Intermittent series can have near-zero total
# test actuals, making its per-series WAPE arbitrarily large and the mean of
# ratios meaningless. Pooled = sum|a-f|/sum|a| over the cell.
fc_frames = []
for fam in ["baselines", "exponential_smoothing", "arima", "lstm", "croston"]:
    fc = pd.read_csv(ROOT / "06_results" / fam / "all_forecasts.csv",
                     usecols=["dataset", "model", "series_id", "actual", "forecast"])
    fc = fc[fc["dataset"] == "m5"].copy()
    fc["archetype"] = fc["series_id"].map(amap)
    fc_frames.append(fc)
all_fc = pd.concat(fc_frames, ignore_index=True)
all_fc["ae"] = (all_fc["actual"] - all_fc["forecast"]).abs()
all_fc["smape_num"] = (all_fc["actual"] - all_fc["forecast"]).abs()
all_fc["smape_den"] = (all_fc["actual"].abs() + all_fc["forecast"].abs()) / 2
def _pooled(g: pd.DataFrame) -> pd.Series:
    wape = g["ae"].sum() / g["actual"].abs().sum()
    nz = g[g["smape_den"] != 0]
    sm = 100 * float((nz["smape_num"] / nz["smape_den"]).mean()) if len(nz) else float("nan")
    return pd.Series({"WAPE": float(wape), "sMAPE": sm})


pooled = (all_fc.groupby(["model", "archetype"])
          .apply(_pooled, include_groups=False)
          .reset_index())
agg = agg.merge(pooled, on=["model", "archetype"], how="left")
agg = agg[["model", "archetype", "n_series", "MAE", "RMSE", "sMAPE", "WAPE", "MASE", "RMSSE"]]
agg.to_csv(RES / "archetype_metrics.csv", index=False)
print(f"saved {RES / 'archetype_metrics.csv'} ({len(agg)} rows)")
print(agg.round(4).to_string(index=False))

for metric in ["MAE", "WAPE"]:
    piv = agg.pivot(index="model", columns="archetype", values=metric)
    plt.figure(figsize=(12, 6))
    sns.heatmap(piv, annot=True, fmt=".3f", cmap="Blues_r")
    plt.title(f"M5 — {metric} by demand archetype (lower is better)")
    plt.tight_layout()
    plt.savefig(FIG / f"{metric.lower()}_by_archetype.png", dpi=150, bbox_inches="tight")
    plt.close()
print(f"figures in {FIG}")
