"""Figure audit: classify all 94 figures, write audit CSV, stage main-text set."""
import csv, os, shutil

DST = '09_reports/final/figures'
os.makedirs(DST, exist_ok=True)

# path -> (class, use, section, caption)
M_RAW = {
 # inventory (shared-policy regen 22:52) — A, main
 '07_figures/inventory/01_total_cost_comparison.png': ('A', 'main', '4.7/4.8', 'Total inventory cost by model and dataset under the shared order-up-to policy (L7, 95%, H1, P5).'),
 '07_figures/inventory/02_service_level_comparison.png': ('A', 'main', '4.7/4.8', 'Cycle service level by model and dataset under the shared policy.'),
 '07_figures/inventory/03_cost_breakdown_stacked.png': ('A', 'main', '4.7/4.8', 'Holding vs stockout cost composition by model and dataset.'),
 '07_figures/inventory/04_inventory_levels_by_model.png': ('A', 'main', '4.7/4.8', 'Average inventory and reorder frequency by model (overstocking diagnosis, esp. DES/TES).'),
 '07_figures/inventory/05_forecast_vs_inventory_scatter.png': ('A', 'main', '4.9', 'Forecast error vs inventory cost: the Store paradox (best forecaster not cheapest).'),
 '07_figures/inventory/06_cost_by_archetype_m5.png': ('A', 'main', '4.11/4.17', 'M5 inventory cost by demand archetype and model.'),
 # sensitivity — A, main
 '07_figures/sensitivity/rank_heatmap_m5.png': ('A', 'main', '4.16', 'M5 model ranks across the 27-policy sensitivity grid (LSTM robust).'),
 '07_figures/sensitivity/rank_heatmap_store_item_demand.png': ('A', 'main', '4.16', 'Store model ranks across the 27-policy grid (fragile leadership).'),
 # archetype pooled — A, main
 '07_figures/archetype_comparison/mae_by_archetype.png': ('A', 'main', '4.11', 'M5 MAE by demand archetype (pooled WAPE/sMAPE companion).'),
 '07_figures/archetype_comparison/wape_by_archetype.png': ('A', 'main', '4.11', 'M5 pooled WAPE by demand archetype (mean-of-ratios fix applied).'),
 # lstm hardened 18:00 — A, main
 '07_figures/lstm/01_comparison_MAE.png': ('A', 'main', '4.2/4.3', 'Full-ladder MAE comparison incl. LSTM (hardened chronological split).'),
 '07_figures/lstm/01_comparison_WAPE.png': ('A', 'main', '4.2/4.3', 'Full-ladder WAPE comparison incl. LSTM.'),
 '07_figures/lstm/02_wape_by_origin.png': ('C', 'appendix', '4.2/4.3', 'WAPE stability across the 8 rolling origins (LSTM ladder).'),
 '07_figures/lstm/03_lstm_by_archetype_m5.png': ('C', 'appendix', '4.11/4.12', 'LSTM error by M5 archetype.'),
 # croston 15:42 — A, main
 '07_figures/croston/01_comparison_MAE_with_croston.png': ('A', 'main', '4.10', 'M5 MAE with Croston/SBA/TSB family (TSB best of family).'),
 '07_figures/croston/01_comparison_WAPE_with_croston.png': ('C', 'appendix', '4.10', 'M5 WAPE with Croston family.'),
 '07_figures/croston/02_mae_by_origin.png': ('C', 'appendix', '4.10', 'Croston-family MAE stability across origins.'),
 # arima 15:55 — M5 panels valid, Store SARIMA panels STALE (subset)
 '07_figures/arima/01_comparison_MAE.png': ('E', 'reject', '4.13/4.14', 'STALE Store panel (subset SARIMA 8.31); M5 panel numerically valid but superseded by F-NEW-02/L-01. DO NOT USE.'),
 '07_figures/arima/01_comparison_WAPE.png': ('E', 'reject', '4.13/4.14', 'STALE Store panel (subset SARIMA); DO NOT USE.'),
 '07_figures/arima/02_wape_by_origin.png': ('E', 'reject', '4.13/4.14', 'STALE Store SARIMA origin curves (subset); DO NOT USE.'),
 '07_figures/arima/03_arima_by_archetype_m5.png': ('A', 'main', '4.11/4.13', 'M5 ARIMA error by archetype (fallback concentration context).'),
 # baselines 15:35 — values verified identical to hardened files — A/C
 '07_figures/baselines/01_naive_vs_actual_representative.png': ('C', 'appendix', '3', 'Naive mechanism illustration on representative series.'),
 '07_figures/baselines/02_snaive_vs_actual_representative.png': ('C', 'appendix', '3', 'Seasonal Naive (corrected repeat-last-7) illustration.'),
 '07_figures/baselines/03_ma_vs_actual_representative.png': ('C', 'appendix', '3', 'Moving Average smoothing illustration.'),
 '07_figures/baselines/04_model_comparison_metrics.png': ('C', 'appendix', '4.2/4.3', 'Baseline metric comparison (values verified vs hardened files).'),
 '07_figures/baselines/05_error_distributions.png': ('C', 'appendix', '4.2/4.3', 'Baseline error distributions.'),
 '07_figures/baselines/06_performance_by_origin.png': ('C', 'appendix', '4.2/4.3', 'Baseline stability across origins.'),
 '07_figures/baselines/07_performance_by_archetype_m5.png': ('C', 'appendix', '4.11', 'Baseline error by M5 archetype.'),
 # smoothing 15:36 — verified identical — A/C
 '07_figures/exponential_smoothing/01_model_comparison.png': ('C', 'appendix', '4.2/4.3', 'SES/DES/TES comparison (values verified vs hardened files; SES best).'),
 '07_figures/exponential_smoothing/02_error_distributions.png': ('C', 'appendix', '4.2/4.3', 'Smoothing error distributions.'),
 '07_figures/exponential_smoothing/03_performance_by_origin.png': ('C', 'appendix', '4.2/4.3', 'Smoothing stability across origins.'),
 '07_figures/exponential_smoothing/04_m5_performance_by_archetype.png': ('C', 'appendix', '4.11', 'Smoothing error by M5 archetype.'),
 '07_figures/exponential_smoothing/05_representative_forecasts.png': ('C', 'appendix', '3', 'Representative SES/DES/TES forecast trajectories.'),
 # EDA — A main selections
 '07_figures/eda/02_intermittency_quadrants.png': ('A', 'main', '2.5', 'ADI/CV2 intermittency quadrants motivating archetypes and the Croston rung.'),
 '07_figures/eda/03_weekly_seasonality.png': ('A', 'main', '2.8', 'Weekly retail seasonality (justifies seasonal period m=7 everywhere).'),
 '07_figures/eda/04_acf_pacf.png': ('A', 'main', '2.7', 'Autocorrelation structure (ARIMA premise).'),
 '07_figures/eda/m5/04_representative_series.png': ('A', 'main', '1.7', 'Representative sparse M5 series (zero-inflation visible).'),
 '07_figures/eda/store_item_demand/08_representative_series.png': ('A', 'main', '1.7', 'Representative dense Store series (sparse-vs-dense contrast).'),
 '07_figures/eda/store_item_demand/11_series_diversity_panel.png': ('A', 'main', '1.7', 'Store demand diversity panel.'),
 '07_figures/experimental_design/01_m5_representativeness.png': ('A', 'main', '2.4', 'Stratified M5 500-series selection representativeness.'),
 # teaching — D limited main
 '07_figures/model_explanations/time_series_components/11_forecasting_model_ladder.png': ('D', 'main', '2.6/3', 'Model ladder schematic (teaching figure, main-text allowed).'),
 '07_figures/model_explanations/time_series_components/12_inventory_connection.png': ('D', 'main', '2.10', 'Forecast-to-inventory connection schematic (teaching, main-text allowed).'),
 '07_figures/model_explanations/croston/01_croston_intuition.png': ('D', 'main', '4.10', 'Croston two-sequence intuition (teaching, main-text allowed).'),
 '07_figures/model_explanations/lstm/02_lstm_cell_gates.png': ('D', 'main', '3', 'LSTM cell and gates (teaching, main-text allowed).'),
}

NEW_RAW = {
 '09_reports/final/figures_new/F-NEW-01-combined-mase-leaderboard.png': ('A', 'main', '4.1', 'Combined M5 vs Store MASE leaderboard (SARIMA full-500; deterministic rebuild).'),
 '09_reports/final/figures_new/F-NEW-02-store-mae-full500-sarima.png': ('A', 'main', '4.3/4.14', 'Store MAE incl. full-500 SARIMA 8.45 (replaces stale subset panels; deterministic rebuild).'),
 '09_reports/final/figures_new/F-NEW-03-sensitivity-winner-share.png': ('A', 'main', '4.16', 'Sensitivity winner-share bars (M5 LSTM 25/27; Store split; deterministic rebuild).'),
}

def norm(p):
    return p.replace(os.sep, '/')

M = {norm(k): v for k, v in M_RAW.items()}
NEW = {norm(k): v for k, v in NEW_RAW.items()}

import glob
allfigs = sorted(norm(p) for p in glob.glob('07_figures/**/*.png', recursive=True))
for k, v in NEW.items():
    allfigs.append(k)

def default_class(p):
    if 'model_explanations' in p:
        return ('D', 'appendix' if any(s in p for s in ['arima/', 'croston/']) else 'omit',
                '3/App', 'Teaching figure; appendix-only or omitted (main-text quota: ladder, inventory link, Croston intuition, LSTM cell).')
    if 'eda' in p:
        return ('C', 'appendix', '2', 'EDA supporting panel (overflow from main-text EDA selection).')
    return ('F', 'omit', '', 'Redundant with selected main-text figure.')

rows_out = []
staged = 0
for p in allfigs:
    if p in M:
        cls, use, sec, cap = M[p]
    elif p in NEW:
        cls, use, sec, cap = NEW[p]
    else:
        cls, use, sec, cap = default_class(p)
        if use == 'omit':
            cls = 'F'
    rows_out.append({'figure_id': '', 'path': p, 'class': cls, 'use': use,
                     'section': sec, 'caption': cap})
    if use == 'main':
        fn = os.path.basename(p)
        shutil.copy(p, os.path.join(DST, fn))
        staged += 1

# assign FIG numbers to main-text set in narrative order
order_key = ['eda/', 'experimental_design', 'model_explanations/time_series_components/11',
             'model_explanations/time_series_components/12', 'F-NEW-01', 'lstm/01',
             'croston/01_comparison_MAE', 'archetype', 'F-NEW-02', 'arima/03',
             'model_explanations/croston', 'model_explanations/lstm',
             'inventory/01', 'inventory/02', 'inventory/03', 'inventory/04',
             'inventory/05', 'inventory/06', 'sensitivity/rank', 'F-NEW-03']
def key(r):
    p = r['path']
    for i, k in enumerate(order_key):
        if k in p:
            return (i, p)
    return (99, p)
mains = sorted([r for r in rows_out if r['use'] == 'main'], key=key)
for i, r in enumerate(mains, 1):
    r['figure_id'] = f'FIG-{i:02d}'
rest = [r for r in rows_out if r['use'] != 'main']
for r in rest:
    r['figure_id'] = r['class'] + '-pool'

with open('09_reports/final/data/figure_audit.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['figure_id', 'path', 'class', 'use', 'section', 'caption'])
    w.writeheader()
    w.writerows(mains + sorted(rest, key=lambda r: r['path']))
print(f'audited={len(rows_out)} main={len(mains)} staged={staged}')
