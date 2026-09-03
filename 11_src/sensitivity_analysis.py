#!/usr/bin/env python
"""Sensitivity / robustness analysis — compact, defensible grid.

Grid:
  lead_time      [3, 7, 14] days (short / baseline / long)
  service_target [0.90, 0.95, 0.99] -> z [1.2816, 1.6449, 2.3263]
  P/H cost ratio [3, 5, 10] with H=1.0 fixed (P in [3,5,10]) -> 3*3*3=27 policies
  plus per-archetype M5 breakdown at baseline policy (5 archetypes)

For each policy, runs the same order-up-to lost-sales simulation as inventory_policy
via simulate_batch (vectorized, bit-for-bit with scalar).  For each (dataset, model)
reports mean total_cost, holding, shortage, service_level (1 - stockout_days/28),
stockout_rate and reorder_count, with baseline policy highlighted.

Outputs:
  06_results/sensitivity/sensitivity_grid.csv  (dataset,model,lead_time,service_target,z,P,total_cost,holding,shortage,service_level,stockout_rate,avg_inventory)
  06_results/sensitivity/sensitivity_by_archetype_m5.csv (baseline policy, per archetype)
  07_figures/sensitivity/ (heatmaps / rank-stability plots)

The grid is deliberately small (27 policies * 11 models * 2 datasets avg 1.1k rows) — enough
to test whether conclusions (LSTM best on M5? Moving Average on Store? DES overstocking?) are
fragile to reasonable parameter shifts, without an exhaustive sweep.
"""
from __future__ import annotations
import pathlib, sys, itertools, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "11_src"))
import numpy as np, pandas as pd, matplotlib.pyplot as plt, seaborn as sns
from inventory_policy import POLICY_DEFAULT, simulate_batch
from plotting import apply_style
apply_style()
ROOT = pathlib.Path(__file__).resolve().parents[1]
RES = ROOT / "06_results" / "sensitivity"
FIG = ROOT / "07_figures" / "sensitivity"
RES.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

# Load forecasts via shared loader
from inventory_policy import load_all_forecasts
all_fc = load_all_forecasts(ROOT / "06_results")
print(f"Loaded {len(all_fc):,} forecast rows across {all_fc['model'].nunique()} models")

# Normalize IDs: baselines use S01_I01, LSTM uses store_10_item_1 — both already canonical in loader
# M5 archetype map
prof = pd.read_csv(ROOT / "02_data/dataset_01_m5/processed/m5_series_profile.csv")
prof["id_eval"] = prof["item_id"].astype(str) + "_" + prof["store_id"].astype(str) + "_evaluation"
amap = prof.set_index("id_eval")["archetype"].to_dict()

LEADS = [3,7,14]
TARGETS = [0.90,0.95,0.99]
ZS = {0.90:1.2816, 0.95:1.6449, 0.99:2.3263}
COSTS = [3,5,10]  # P values, H=1

rows=[]
# Pre-group forecasts: (dataset,model,series,origin) -> (fc 28, act 28)
groups = list(all_fc.groupby(["dataset","model","series_id","origin"]))
print(f"Groups: {len(groups)}")
# For each policy, simulate all groups
for lt, tgt, P in itertools.product(LEADS, TARGETS, COSTS):
    pol = dict(POLICY_DEFAULT); pol["lead_time"]=lt; pol["service_target"]=tgt; pol["z"]=ZS[tgt]; pol["P"]=float(P); pol["H"]=1.0
    # Batch per dataset/model for vectorization
    for (ds, model), sub in all_fc.groupby(["dataset","model"]):
        # Build batch arrays: one row per group instance within this ds/model
        # Collect groups for this ds/model
        g_list = [g for keys,g in groups if keys[0]==ds and keys[1]==model]
        if not g_list: continue
        Fs = np.stack([gg.sort_values("forecast_date")["forecast"].values for gg in g_list])
        As = np.stack([gg.sort_values("forecast_date")["actual"].values for gg in g_list])
        # Fs,As shape (n_instances, 28)
        out = simulate_batch(Fs, As, pol)
        # out has total_cost etc per instance; average across instances
        rows.append({
            "dataset":ds,"model":model,"lead_time":lt,"service_target":tgt,"z":ZS[tgt],"P":P,"H":1,
            "total_cost": float(np.mean(out["total_cost"])),
            "holding_cost": float(np.mean(out["total_holding_cost"])),
            "shortage_cost": float(np.mean(out["total_stockout_cost"])),
            "service_level": float(np.mean(out["service_level"])),
            "stockout_rate": float(np.mean(out["stockout_frequency"])) / 28.0,
            "avg_inventory": float(np.mean(out["average_inventory"])),
            "reorder_count": float(np.mean(out["reorder_count"])),
            "n_instances": len(g_list)
        })

grid = pd.DataFrame(rows)
grid.to_csv(RES / "sensitivity_grid.csv", index=False)
print(f"Saved {RES/'sensitivity_grid.csv'} {len(grid)} rows (27 policies * ~11 models *2)")

# Rank stability at baseline
base = grid[(grid["lead_time"]==7)&(grid["service_target"]==0.95)&(grid["P"]==5)]
for ds in ["m5","store_item_demand"]:
    sub=base[base["dataset"]==ds].sort_values("total_cost")
    print(f"\nBaseline ranking {ds}:")
    print(sub[["model","total_cost","service_level"]].to_string(index=False))

# Archetype breakdown at baseline
arch_rows=[]
pol = dict(POLICY_DEFAULT)
for (ds, model), sub in all_fc[all_fc["dataset"]=="m5"].groupby(["dataset","model"]):
    # per archetype
    for arch, grp in sub.groupby(sub["series_id"].map(amap)):
        # batch
        g_list = [gg for _,gg in grp.groupby(["series_id","origin"])]
        if not g_list: continue
        Fs = np.stack([gg.sort_values("forecast_date")["forecast"].values for gg in g_list])
        As = np.stack([gg.sort_values("forecast_date")["actual"].values for gg in g_list])
        out = simulate_batch(Fs, As, pol)
        arch_rows.append({"dataset":ds,"model":model,"archetype":arch,"total_cost":float(np.mean(out["total_cost"])),"service_level":float(np.mean(out["service_level"])),"n":len(g_list)})
arch_df = pd.DataFrame(arch_rows)
arch_df.to_csv(RES / "sensitivity_by_archetype_m5.csv", index=False)
print(f"Saved archetype {len(arch_df)} rows")

# Figures: rank heatmap per policy
for ds in ["m5","store_item_demand"]:
    sub = grid[grid["dataset"]==ds]
    # Pivot: model vs policy string, value rank
    sub["policy"] = sub.apply(lambda r: f"L{r.lead_time}-S{int(r.service_target*100)}-P{r.P}", axis=1)
    # Compute rank per policy (1=best lowest cost)
    sub["rank"] = sub.groupby("policy")["total_cost"].rank(method="min")
    piv = sub.pivot(index="model", columns="policy", values="rank")
    plt.figure(figsize=(14,6))
    sns.heatmap(piv, annot=True, fmt=".0f", cmap="Blues_r", cbar_kws={"label":"Rank (1=best)"})
    plt.title(f"{ds} — rank stability across lead_time/service/P (lower is better)")
    plt.tight_layout()
    plt.savefig(FIG / f"rank_heatmap_{ds}.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved rank heatmap {ds}")

print("Sensitivity analysis complete.")
