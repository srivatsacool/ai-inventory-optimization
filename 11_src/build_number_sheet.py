"""Build final_number_sheet.csv programmatically from final result files only."""
import pandas as pd, numpy as np, os

R = '06_results'
rows = []
def add(mid, ds, model, metric, val, units, pop, src, col, section, dest, notes=''):
    try: v = round(float(val), 6)
    except (TypeError, ValueError): v = val
    rows.append(dict(metric_id=mid, dataset=ds, model=model, metric=metric,
        value=v, units=units, population=pop, source_file=src, source_column=col,
        status='FINAL', report_section=section, destination=dest, notes=notes))

N_SU = '500sx8ox28d=112000'
for fam in ['baselines', 'exponential_smoothing', 'croston', 'arima', 'lstm']:
    df = pd.read_csv(f'{R}/{fam}/metrics_by_model.csv')
    for _, r in df.iterrows():
        for m in ['MAE', 'RMSE', 'sMAPE', 'WAPE']:
            add(f'FC-{r["dataset"]}-{r["model"]}-{m}', r['dataset'], r['model'], m, r[m],
                'units' if m in ('MAE', 'RMSE') else ('ratio' if m == 'WAPE' else 'pct'),
                N_SU, f'{R}/{fam}/metrics_by_model.csv', m, '4.2/4.3',
                'T-03' if r['dataset'] == 'm5' else 'T-04',
                'per-series-mean; WAPE honest-NaN, no epsilon' if m == 'WAPE' else '')

sf = pd.read_csv(f'{R}/scale_free_metrics/summary.csv')
ar = pd.read_csv(f'{R}/arima/metrics_by_model.csv')
sar_full = ar[(ar.dataset == 'store_item_demand') & (ar.model == 'SARIMA')].iloc[0]
for _, r in sf.iterrows():
    if r['dataset'] == 'store_item_demand' and r['model'] == 'SARIMA':
        continue  # superseded subset row -> replaced below
    for m in ['MASE', 'RMSSE']:
        add(f'SF-{r["dataset"]}-{r["model"]}-{m}', r['dataset'], r['model'], m, r[m],
            'ratio', '500 series', f'{R}/scale_free_metrics/summary.csv', m, '4.2/4.3',
            'T-03' if r['dataset'] == 'm5' else 'T-04',
            'm=7, train-only denom (method_note.txt); n_nan_mase=0')
for m in ['MASE', 'RMSSE']:
    add(f'SF-store_item_demand-SARIMA-{m}', 'store_item_demand', 'SARIMA', m, sar_full[m],
        'ratio', N_SU, f'{R}/arima/metrics_by_model.csv', m, '4.3/4.14', 'T-04',
        'FULL500 (4000 fits, 0 fallbacks); supersedes summary.csv subset row n=100 (MASE 1.0688)')
add('SF-M5-SARIMA-notrun', 'm5', 'SARIMA', 'not-run', '', '', '', '', '', '4.14', '',
    'SARIMA never run on M5 by design (seasonal differencing dubious on intermittent demand)')

inv = pd.read_csv(f'{R}/inventory/inventory_by_model.csv')
for _, r in inv.iterrows():
    sec = '4.7' if r['dataset'] == 'm5' else '4.8'
    dst = 'T-06' if r['dataset'] == 'm5' else 'T-07'
    add(f'INV-{r["dataset"]}-{r["model"]}-cost', r['dataset'], r['model'], 'total_cost',
        r['total_cost'], 'cost-units', '4000 series-origins',
        f'{R}/inventory/inventory_by_model.csv', 'total_cost', sec, dst,
        f'POLICY_DEFAULT L7/95%/H1/P5; hold={r["total_holding_cost"]:.2f} short={r["total_stockout_cost"]:.2f}')
    add(f'INV-{r["dataset"]}-{r["model"]}-sl', r['dataset'], r['model'], 'service_level',
        r['service_level'], 'fraction', '4000 series-origins',
        f'{R}/inventory/inventory_by_model.csv', 'service_level', sec, dst,
        f'avg_inv={r["average_inventory"]:.2f} reorders={r["reorder_count"]:.2f}')

pw = pd.read_csv(f'{R}/statistical_tests/pairwise_tests.csv')
add('PW-COUNT', 'both', 'all', 'n_pairs', len(pw), 'count', 'paired forecast errors',
    f'{R}/statistical_tests/pairwise_tests.csv', '', '4.5', 'App-F',
    f'{len(pw)} pairs (55 M5 + 36 Store); Wilcoxon+DM+Holm+bootstrap500+dz+r')
for a, b, ds in [('LSTM', 'TSB', 'm5'), ('LSTM', 'Moving Average', 'm5'), ('LSTM', 'SES', 'm5'),
                 ('LSTM', 'Moving Average', 'store_item_demand'),
                 ('LSTM', 'SARIMA', 'store_item_demand'), ('LSTM', 'SES', 'store_item_demand'),
                 ('Moving Average', 'SES', 'm5')]:
    q = pw[(pw.dataset == ds) & (pw.model_a == a) & (pw.model_b == b)]
    s = 1
    if len(q) == 0:
        q = pw[(pw.dataset == ds) & (pw.model_a == b) & (pw.model_b == a)]
        s = -1
    r = q.iloc[0]
    add(f'SPOT-{ds}-{a}-vs-{b}-dz', ds, f'{a} vs {b}', 'cohen_dz', s * r['cohen_dz'], '',
        f'n={int(r["n_paired"])}', f'{R}/statistical_tests/pairwise_tests.csv', 'cohen_dz',
        '4.4/4.5', 'T-05',
        f'Holm p={r["wilcoxon_p_holm"]:.2e} r={r["wilcoxon_rank_biserial_r"]:.3f} '
        f'CI=[{r["ci_lo"]:.4f},{r["ci_hi"]:.4f}]')

g = pd.read_csv(f'{R}/sensitivity/sensitivity_grid.csv')
winners = {}
for ds in ['m5', 'store_item_demand']:
    piv = g[g.dataset == ds].pivot_table(index=['lead_time', 'service_target', 'P', 'H'],
                                         columns='model', values='total_cost')
    w = piv.idxmin(axis=1).value_counts()
    winners[ds] = w.to_dict()
    for model, cnt in w.items():
        add(f'SENS-{ds}-{model}-wins', ds, model, 'n_policy_wins', int(cnt), 'policies',
            '27 policies', f'{R}/sensitivity/sensitivity_grid.csv', 'total_cost', '4.16', 'T-08',
            'grid L{3,7,14}xsvc{.90,.95,.99}xP{3,5,10},H=1')
print('WINNERS:', winners)

ac = pd.read_csv(f'{R}/archetype_comparison/archetype_metrics.csv')
for arch in ac.archetype.unique():
    sub = ac[ac.archetype == arch].sort_values('MAE')
    best = sub.iloc[0]
    add(f'ARCH-{arch}-bestMAE', 'm5', best['model'], 'MAE', best['MAE'], 'units',
        f'n={int(best["n_series"])} series', f'{R}/archetype_comparison/archetype_metrics.csv',
        'MAE', '4.11', 'App-G',
        'pooled WAPE/sMAPE; Smooth n=1 ANECDOTAL' if arch == 'Smooth' else 'pooled WAPE/sMAPE')
add('ARCH-COUNT', 'm5', 'all', 'n_rows', len(ac), 'rows', '11 models x 5 archetypes',
    f'{R}/archetype_comparison/archetype_metrics.csv', '', '4.11', 'App-G', 'M5 only')

cr = pd.read_csv(f'{R}/arima/convergence_report.csv')
for _, r in cr.iterrows():
    add(f'CONV-{r["dataset"]}-{r["model"]}', r['dataset'], r['model'], 'fallback_pct',
        r['fallback_pct'], 'pct', f'n={int(r["n_fits_attempted"])} fits',
        f'{R}/arima/convergence_report.csv', 'fallback_pct', '4.18', 'T-09',
        f'scope={r["scope"]} fails={int(r["n_fit_failures"])} fb={int(r["n_fallback_naive"])}')

add('PROTO-train', '', '', 'days', 1034, 'days', 'common window',
    '05_experiments/config.json', '', '2.3', 'T-01', '2013-01-01..2015-10-31')
add('PROTO-val', '', '', 'days', 121, 'days', 'common window',
    '05_experiments/config.json', '', '2.3', 'T-01', '2015-11-01..2016-02-29 incl leap day')
add('PROTO-test', '', '', 'days', 83, 'days', 'common window',
    '05_experiments/config.json', '', '2.3', 'T-01', '2016-03-01..2016-05-22; 8 weekly origins H28 seed42')

ns = pd.DataFrame(rows)
os.makedirs('09_reports/final/data', exist_ok=True)
ns.to_csv('09_reports/final/data/final_number_sheet.csv', index=False)
print('number_sheet rows:', len(ns))
