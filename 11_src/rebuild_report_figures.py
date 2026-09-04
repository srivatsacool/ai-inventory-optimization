"""Deterministic report-figure rebuilds from FINAL result files only. No styling overreach."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import os

OUT = '09_reports/final/figures_new'
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({'font.size': 9, 'figure.dpi': 150})

# --- F-NEW-01: combined MASE leaderboard (M5 + Store), full500 SARIMA ---
sf = pd.read_csv('06_results/scale_free_metrics/summary.csv')
ar = pd.read_csv('06_results/arima/metrics_by_model.csv')
sar = ar[(ar.dataset == 'store_item_demand') & (ar.model == 'SARIMA')].iloc[0]
sf = sf[~((sf.dataset == 'store_item_demand') & (sf.model == 'SARIMA'))]
sf = pd.concat([sf, pd.DataFrame([{'family': 'arima', 'dataset': 'store_item_demand',
    'model': 'SARIMA', 'MASE': sar['MASE'], 'RMSSE': sar['RMSSE'],
    'n_series': 500, 'n_nan_mase': 0}])], ignore_index=True)
order_m5 = sf[sf.dataset == 'm5'].sort_values('MASE')['model'].tolist()
fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), sharey=False)
for ax, ds, title in zip(axes, ['m5', 'store_item_demand'],
                         ['M5 (sparse) — MASE by model', 'Store (dense) — MASE by model']):
    d = sf[sf.dataset == ds].sort_values('MASE')
    ax.barh(d['model'], d['MASE'], color='#4C78A8')
    ax.set_title(title)
    ax.set_xlabel('MASE (m=7, lower is better)')
    for i, v in enumerate(d['MASE']):
        ax.text(v, i, f' {v:.3f}', va='center', fontsize=8)
fig.suptitle('Forecast leaderboard (scale-free MASE; SARIMA = full-500 Store-only)')
fig.tight_layout()
fig.savefig(f'{OUT}/F-NEW-01-combined-mase-leaderboard.png', bbox_inches='tight')
print('F-NEW-01 ok')

# --- F-NEW-02: Store MAE comparison incl. full500 SARIMA (replaces stale subset panels) ---
frames = []
for fam in ['baselines', 'exponential_smoothing', 'arima', 'lstm']:
    frames.append(pd.read_csv(f'06_results/{fam}/metrics_by_model.csv'))
fc = pd.concat(frames, ignore_index=True)
d = fc[fc.dataset == 'store_item_demand'].sort_values('MAE')
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.barh(d['model'], d['MAE'], color='#72B66B')
ax.set_title('Store Item Demand — MAE by model (SARIMA full-500, n=112000)')
ax.set_xlabel('MAE (units, lower is better)')
for i, v in enumerate(d['MAE']):
    ax.text(v, i, f' {v:.2f}', va='center', fontsize=8)
fig.tight_layout()
fig.savefig(f'{OUT}/F-NEW-02-store-mae-full500-sarima.png', bbox_inches='tight')
print('F-NEW-02 ok')

# --- F-NEW-03: sensitivity winner-share + which M5 policies SES takes ---
g = pd.read_csv('06_results/sensitivity/sensitivity_grid.csv')
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for ax, ds, title in zip(axes, ['m5', 'store_item_demand'],
                         ['M5 — policy wins (27 policies)', 'Store — policy wins (27 policies)']):
    piv = g[g.dataset == ds].pivot_table(index=['lead_time', 'service_target', 'P', 'H'],
                                         columns='model', values='total_cost')
    w = piv.idxmin(axis=1).value_counts().sort_values(ascending=True)
    ax.barh(w.index, w.values, color='#F58518')
    ax.set_xlabel('policies won (of 27)')
    ax.set_title(title)
    for i, v in enumerate(w.values):
        ax.text(v, i, f' {int(v)}', va='center', fontsize=8)
    if ds == 'm5':
        win = piv.idxmin(axis=1)
        print('M5 non-LSTM wins:')
        print(win[win != 'LSTM'])
fig.tight_layout()
fig.savefig(f'{OUT}/F-NEW-03-sensitivity-winner-share.png', bbox_inches='tight')
print('F-NEW-03 ok')
