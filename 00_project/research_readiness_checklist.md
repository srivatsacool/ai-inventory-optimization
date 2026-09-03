# Research Readiness Checklist — Pre-Report Gate
**Hardening complete 2026-09-04. Gate statuses verified by executed code, not intent.**

## Methodology — PASS
- [x] PASS Frozen design locked: M5 500 stratified / Store 500 all / 2013-01-01→2016-05-22 (1238d) / H28 / 8 origins / seed 42 (config.json + all _make_nb*.py)
- [x] PASS Temporal protocol corrected: Train 1034 + Val 121 (incl. 2016-02-29) + Test 83 = 1238; asserts pass; no gap day. All notebooks 05b/06/06c/07/08 audited: contain 2016-02-29, no 2016-02-28/1237 text. Results re-executed post-patch (baselines 15:35, smoothing 15:36-37 with 121d manifests, croston 15:42, arima 15:55, lstm 18:00 hardened validation).
- [x] PASS Expanding-window rolling-origin evaluation, history strictly < origin asserted in every notebook (leakage audit PASS; validator re-checks forecast_date >= origin_date and test-window containment: 0 FAIL).
- [x] PASS Croston-family specialist added — 06c executed (Croston/SBA/TSB, M5 full 500x8x28 each; TSB MAE 1.010 best of family). Store Item intentionally excluded with documented justification (dense demand, no intermittency premise).
- [x] PASS ARIMA/SARIMA convergence quantified — convergence_details_all.csv (per-fit) + convergence_report.csv with scope column (subset100_exploratory vs full500_primary). M5 ARIMA: 3094 fits ok / 906 pre-check skips (22.65% Naive fallback, 0 optimizer failures, all skips Highly Intermittent-driven). Store ARIMA 4000/4000. SARIMA full500 4000/4000, 0 fallbacks.
- [x] PASS LSTM validation hardened to chronological per-series split (last-k-windows block, no overlapping train/val windows); rerun Sep 3 18:00.
- [x] PASS SARIMA comparability resolved — full-500 Store run FEASIBLE (probe 0.62s/fit, full run 2382s, 4000/4000 ok) and EXECUTED. Primary comparison now identical populations (500 series) on both datasets. 100-series subset retained as labelled exploratory artifact (sarima_store_item_subset.csv + backup of subset-based all_forecasts.csv).

## Data — PASS
- [x] PASS Datasets versioned: M5 sales_train_evaluation.csv + calendar.csv, Store train.csv, selection via 05_experiments/m5_series_selection.json.
- [x] PASS Common window reindexed to dates_common for both datasets (validator: cross-family actuals identical, max spread 0.0).
- [x] PASS Archetype profile at 02_data/dataset_01_m5/processed/m5_series_profile.csv; unified archetype table 06_results/archetype_comparison/archetype_metrics.csv (55 rows, pooled WAPE/sMAPE — mean-of-ratios fixed).
- [x] PASS Zero-rate documented: M5 64.5% vs Store 0.02%.

## Leakage — PASS
- [x] PASS History strictly < origin asserted in every notebook + validator gate.
- [x] PASS Scalers per-series fit on history only (fit_scalers_and_scale).
- [x] PASS Validation (2015-11-01→2016-02-29) never uses test; all selection on validation only.
- [x] PASS LLM prompt builder guards max(history_date) < origin (11_src/llm_experiment_design.md; LLM NOT yet executed — separate future phase).

## Model Fairness — PASS
- [x] PASS Same 500x8x28 per dataset for all full-population models (112000 rows; validator row-count gates PASS for all 5 families).
- [x] PASS Same window/L/H/metrics/origins across ladder; loader test 28/28 (11_src/test_inventory_policy.py).
- [x] PASS Croston flat-forecast limitation noted; M5-only scope by design (intermittent specialist).
- [x] PASS SARIMA now full-population; subset never presented as equivalent (scope column + backup).
- [x] PASS LLM controlled vs context-enhanced separated (design doc only; no LLM results exist yet, so no contamination possible).

## Metrics — PASS
- [x] PASS Primary: MAE (+ MASE scale-free m=7 train-only denominator); secondary RMSE, WAPE, sMAPE, RMSSE in metrics.py + wired into every metrics_by_model/series.csv (validator: present, 0 unexpected NaN; n_nan_mase=0 everywhere).
- [x] PASS sMAPE/WAPE zero limitations documented AND demonstrated: per-series WAPE averaging exploded (2e9) on near-zero-test-demand series → archetype table uses pooled WAPE/sMAPE. Honest NaN behavior preserved (no epsilon guards).
- [x] PASS No metric cherry-picking — all six reported together (scale_free_metrics/summary.csv).

## Statistical Testing — PASS (with interpretation guardrail)
- [x] PASS Paired Wilcoxon (normal approx) + DM + Holm + 500-rep bootstrap CI + Cohen dz + rank-biserial r in 06_results/statistical_tests/pairwise_tests.csv (91 pairs: 55 M5 + 36 Store).
- [x] PASS Significance vs practical significance distinguished: M5 top-cluster gaps significant-but-tiny (LSTM vs TSB dz -0.031, p 2e-10); Store gaps large (LSTM vs MA dz -0.29, p 0).

## Inventory Simulation — PASS
- [x] PASS Shared policy module 11_src/inventory_policy.py (POLICY_DEFAULT: L7, 95%, z=norm.ppf, H1 P5); inventory_simulation.py unified onto simulate_group (z 1.645→1.6449 documented micro-change); scalar/batch parity 0.0.
- [x] PASS All 21 model-datasets feed same policy; reorder_count captured; 6 figures regenerated.
- [x] PASS Croston-family included (SBA 160.66 / TSB 165.13 / CROSTON 174.82 on M5).

## Robustness — PASS
- [x] PASS Sensitivity grid 27 policies executed → 06_results/sensitivity/ (540 rows + 55 archetype rows + 2 rank heatmaps).
- [x] PASS Per-archetype M5 analysis for every model (archetype_metrics.csv, pooled).
- [x] PASS Rank-stability verdict: M5 LSTM #1 in 25/27 (ROBUST); Store winner FRAGILE (MA 9 / SES 7 / Naive 6 / DES 5) — must be reported as policy-sensitive.
- [x] PASS Negative findings preserved (TES worst everywhere, DES overstocking, ARIMA-on-sparse, LSTM Store forecast-vs-inventory paradox, Store winner fragility).

## Reproducibility — PASS
- [x] PASS Seeds 42 in config, notebooks, torch+numpy, SARIMA scripts, validator sampling.
- [x] PASS Execution manifests: smoothing metadata (121d), croston validation_selection (121d + seed), SARIMA run_log_full500.json (2382s), feasibility probe JSON, validation_report.json (0 FAIL), backup manifest.json.
- [x] PASS Pre-hardening originals preserved in 06_results/_pre_hardening_backup/ (10 metrics files + manifest + subset-based arima all_forecasts).
- [x] PASS Figure paths consistent (07_figures/* + sensitivity + archetype_comparison).

## Reporting
- [x] PASS Hardening Report complete (conversation record 2026-09-03/04).
- [ ] HELD Final report NOT written — gate held per instructions. GO for report writing once this checklist is committed.
