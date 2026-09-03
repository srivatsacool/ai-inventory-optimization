#!/usr/bin/env python
"""Phase 1 Inventory Simulation — loads existing forecasts, runs lost-sales simulation, generates comparison tables and figures."""
import sys, pathlib, warnings, time
warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from plotting import apply_style
from inventory_policy import POLICY_DEFAULT, simulate_group, load_all_forecasts

PROJ = pathlib.Path(__file__).resolve().parents[1]
RES = PROJ / "06_results"
INV = RES / "inventory"
FIG = PROJ / "07_figures" / "inventory"
INV.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

SEED = 42
np.random.seed(SEED)
apply_style()
C1, C2, C3, C4, C5, CN = '#0072B2', '#D55E00', '#009E73', '#CC79A7', '#E69F00', '#999999'

# === 1. Load all forecasts ===
print("=" * 70)
print("PHASE 1 INVENTORY SIMULATION")
print("=" * 70)
# Single common policy for ALL models/families (see inventory_policy.py):
# lead_time=7, service_target=0.95 (z=1.645), H=1.0, P=5.0 (P/H = 5).
POLICY = POLICY_DEFAULT
print(f"  POLICY (common to every model): lead_time={POLICY['lead_time']}, "
      f"service_target={POLICY['service_target']}, z={POLICY['z']}, "
      f"H={POLICY['H']}, P={POLICY['P']} (P/H={POLICY['P'] / POLICY['H']})")
all_fc = load_all_forecasts()
print(f"  families loaded: {sorted(all_fc['family'].unique().tolist())}")
print(f"  TOTAL: {len(all_fc):,} rows, datasets: {all_fc['dataset'].unique().tolist()}, "
      f"models: {sorted(all_fc['model'].unique().tolist())}")

# === 2. Consolidate forecast metrics ===
print("\n--- Consolidating forecast metrics ---")
metric_files = [
    (RES / 'baselines' / 'metrics_by_model.csv', 'Baseline'),
    (RES / 'exponential_smoothing' / 'metrics_by_model.csv', 'Smoothing'),
    (RES / 'arima' / 'metrics_by_model.csv', 'ARIMA/SARIMA'),
    (RES / 'lstm' / 'metrics_by_model.csv', 'LSTM'),
    (RES / 'croston' / 'metrics_by_model.csv', 'Croston-family'),
]
fm_parts = []
for path, family in metric_files:
    m = pd.read_csv(path)
    m['family'] = family
    fm_parts.append(m)
fm = pd.concat(fm_parts, ignore_index=True)
fm.to_csv(INV / 'phase1_forecast_comparison.csv', index=False)
print(fm[['dataset', 'model', 'family', 'MAE', 'RMSE', 'WAPE']].round(4).to_string(index=False))

# === 3. Inventory simulation (shared module = single source of truth) ===
print("\n--- Running inventory simulation ---")
# simulate_group() from inventory_policy.py implements the canonical
# order-up-to / lost-sales math; verified bit-identical to the legacy
# inline simulate_one via 11_src/test_inventory_policy.py parity checks.

t0 = time.time()
results = []
for (ds, model, sid, origin), grp in all_fc.groupby(['dataset', 'model', 'series_id', 'origin']):
    r = simulate_group(grp, POLICY)
    r.update({'dataset': ds, 'model': model, 'series_id': sid, 'origin': origin})
    results.append(r)
inv_df = pd.DataFrame(results)
inv_df.to_csv(INV / 'inventory_by_series.csv', index=False)
print(f"  {len(inv_df):,} simulations in {time.time()-t0:.0f}s")

# Aggregate
inv_agg = inv_df.groupby(['dataset', 'model']).agg({
    'total_holding_cost': 'mean', 'total_stockout_cost': 'mean', 'total_cost': 'mean',
    'service_level': 'mean', 'average_inventory': 'mean', 'stockout_frequency': 'mean',
    'stockout_quantity': 'sum', 'reorder_count': 'mean',
}).reset_index()
fm_family = fm[['dataset', 'model', 'family']].drop_duplicates()
inv_agg = inv_agg.merge(fm_family, on=['dataset', 'model'], how='left')
inv_agg.to_csv(INV / 'inventory_by_model.csv', index=False)

# Merge with forecast metrics
fc_cols = fm[['dataset', 'model', 'MAE', 'RMSE', 'sMAPE', 'WAPE']].copy()
inv_comp = inv_agg.merge(fc_cols, on=['dataset', 'model'], how='left')
inv_comp.to_csv(INV / 'inventory_comparison_with_forecasting.csv', index=False)

# Bias
bias = all_fc.groupby(['dataset', 'model']).agg(bias=('error', 'mean')).reset_index()
final = inv_comp.merge(bias, on=['dataset', 'model'], how='left')
final = final.sort_values(['dataset', 'total_cost'])
final.to_csv(INV / 'phase1_final_comparison.csv', index=False)

print("\n" + "=" * 70)
print("INVENTORY RESULTS BY MODEL")
print("=" * 70)
for ds in ['m5', 'store_item_demand']:
    print(f"\n--- {ds} ---")
    sub = final[final['dataset'] == ds].sort_values('total_cost')
    print(sub[['model', 'MAE', 'WAPE', 'service_level', 'total_cost', 'total_holding_cost', 'total_stockout_cost', 'average_inventory']].round(4).to_string(index=False))

# === 4. Figures ===
print("\n--- Generating figures ---")
def fc_for(ds): return final[final['dataset'] == ds]

def get_colors(sub):
    return [C1 if f == 'Baseline' else C2 if f == 'Smoothing' else C3 if f == 'ARIMA/SARIMA' else C5 if f == 'Croston-family' else C4 for f in sub['family']]

# 01 Total cost
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, ds in zip(axes, ['m5', 'store_item_demand']):
    s = fc_for(ds).sort_values('total_cost')
    ax.barh(s['model'], s['total_cost'], color=get_colors(s), edgecolor='white')
    ax.set_title(f"{ds} — Total Inventory Cost (lower is better)")
    ax.set_xlabel("Total cost (units)")
plt.tight_layout(); plt.savefig(FIG / '01_total_cost_comparison.png', dpi=150, bbox_inches='tight'); plt.close()

# 02 Service level
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, ds in zip(axes, ['m5', 'store_item_demand']):
    s = fc_for(ds).sort_values('service_level', ascending=False)
    ax.barh(s['model'], s['service_level'] * 100, color=get_colors(s), edgecolor='white')
    ax.set_title(f"{ds} — Service Level % (higher is better)")
    ax.set_xlabel("Service level (%)"); ax.axvline(95, color='red', ls='--', alpha=0.5, label='Target 95%'); ax.legend()
plt.tight_layout(); plt.savefig(FIG / '02_service_level_comparison.png', dpi=150, bbox_inches='tight'); plt.close()

# 03 Cost breakdown
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, ds in zip(axes, ['m5', 'store_item_demand']):
    s = fc_for(ds).sort_values('total_cost')
    ax.barh(s['model'], s['total_holding_cost'], color=C1, label='Holding', edgecolor='white')
    ax.barh(s['model'], s['total_stockout_cost'], left=s['total_holding_cost'], color=C2, label='Stockout', edgecolor='white')
    ax.set_title(f"{ds} — Cost Breakdown"); ax.set_xlabel("Cost"); ax.legend()
plt.tight_layout(); plt.savefig(FIG / '03_cost_breakdown_stacked.png', dpi=150, bbox_inches='tight'); plt.close()

# 04 Inventory levels
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, ds in zip(axes, ['m5', 'store_item_demand']):
    s = fc_for(ds).sort_values('average_inventory')
    ax.barh(s['model'], s['average_inventory'], color=get_colors(s), edgecolor='white')
    ax.set_title(f"{ds} — Average Inventory Level"); ax.set_xlabel("Units")
plt.tight_layout(); plt.savefig(FIG / '04_inventory_levels_by_model.png', dpi=150, bbox_inches='tight'); plt.close()

# 05 MAE vs Cost scatter
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, ds in zip(axes, ['m5', 'store_item_demand']):
    s = fc_for(ds)
    ax.scatter(s['MAE'], s['total_cost'], c=get_colors(s), s=120, edgecolors='black', zorder=5)
    for _, row in s.iterrows():
        ax.annotate(row['model'], (row['MAE'], row['total_cost']), fontsize=7)
    ax.set_title(f"{ds} — Forecast Error vs Inventory Cost")
    ax.set_xlabel("MAE"); ax.set_ylabel("Total cost")
plt.tight_layout(); plt.savefig(FIG / '05_forecast_vs_inventory_scatter.png', dpi=150, bbox_inches='tight'); plt.close()

# 06 M5 archetype cost
m5p = pd.read_csv(PROJ / '02_data/dataset_01_m5/processed/m5_series_profile.csv')
m5p['id_eval'] = m5p['item_id'].astype(str) + '_' + m5p['store_id'].astype(str) + '_evaluation'
amap = m5p.set_index('id_eval')['archetype'].to_dict()
im = inv_df[inv_df['dataset'] == 'm5'].copy()
im['archetype'] = im['series_id'].map(amap)
top3 = fc_for('m5').sort_values('total_cost').head(3)['model'].tolist()
ac = im[im['model'].isin(top3)].groupby(['model', 'archetype'])['total_cost'].mean().reset_index()
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=ac, x='archetype', y='total_cost', hue='model', ax=ax, palette=[C1, C2, C3][:3])
ax.set_title("M5 — Total Cost by Archetype (top 3 models)")
ax.set_ylabel("Mean total cost"); ax.set_xlabel("Archetype"); ax.tick_params(axis='x', rotation=15)
plt.tight_layout(); plt.savefig(FIG / '06_cost_by_archetype_m5.png', dpi=150, bbox_inches='tight'); plt.close()
print(f"Saved 6 figures to {FIG}")

# === 5. Summary ===
print("\n" + "=" * 70)
print("PHASE 1 FINAL SUMMARY")
print("=" * 70)
for ds in ['m5', 'store_item_demand']:
    s = fc_for(ds).sort_values('total_cost')
    best_inv = s.iloc[0]['model']
    best_fc = fc_for(ds).sort_values('MAE').iloc[0]['model']
    best_sl = fc_for(ds).sort_values('service_level', ascending=False).iloc[0]['model']
    print(f"\n{ds}:")
    print(f"  Best forecast (MAE): {best_fc}")
    print(f"  Best inventory (cost): {best_inv}")
    print(f"  Best service level: {best_sl}")
    if best_fc != best_inv:
        print(f"  NOTE: forecast winner != inventory winner (cost ≠ error)")

print(f"\nFiles saved: {INV}")
print(f"Figures saved: {FIG}")
print(f"Total time: {time.time()-t0:.0f}s")
