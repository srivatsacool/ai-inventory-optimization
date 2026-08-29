# Research Progress Tracker

> **Last updated:** 2026-08-29 (Notebook 05a+05b+06 complete)
> **Current phase:** Foundation + baselines + smoothing complete (05a, 05b, 06). Notebook 07 is pending review.

---

## Overall story

```
WHAT IS THE PROBLEM?           → 00_research_map
        ↓
WHAT DOES THE DATA LOOK LIKE?  → 02_data_acquisition_and_audit + 03_exploratory_data_analysis
        ↓
WHAT SIMPLE METHODS CAN DO     → 05a_components + 05b_baselines + 06_smoothing
        ↓
WHAT DOES STATISTICAL MODELING ADD? → 08_des + 09_tes + 10_arima + 11_sarima + 12_classical_comparison
        ↓
WHAT DOES NEURAL MODELING ADD? → 13_lstm
        ↓
WHAT DOES AN LLM ADD?          → 14_llm_forecasting
        ↓
DO FORECASTING GAINS IMPROVE INVENTORY? → 15_forecast_comparison + 16_inventory_simulation + 17_inventory_results
        ↓
DOES MORE COMPLEXITY CREATE BUSINESS VALUE? → 18_sensitivity + 19_statistical_analysis
        ↓
DO RESULTS GENERALIZE?         → 20_cross_dataset_robustness
        ↓
WHAT SHOULD A BUSINESS CHOOSE? → 21_final_research_findings
```

---

## Notebook ladder

| # | Notebook | Objective | Status | Output |
|---|----------|-----------|--------|--------|
| 00 | `00_research_map.ipynb` | Dashboard: question, ladder, datasets, evaluation, progress | ✅ Complete | Dashboard (no data) |
| 01 | `01_environment_and_reproducibility.ipynb` | Env audit, seeds, versions, reproducibility contract | ✅ Complete | `05_experiments/manifests/environment.json` |
|| 02 | `02_data_acquisition_and_audit.ipynb` | Dataset audit, common window, equality of observations | ✅ Complete | `02_data/audit_summary.json` |
|| 02b | `02b_store_item_demand_acquisition_and_audit.ipynb` | Dataset 02 (Store Item Demand) audit, EDA, M5 comparison | ✅ Complete | `02_data/dataset_02_store_item_demand/processed/`, `07_figures/eda/store_item_demand/` |
| 03 | `03_exploratory_data_analysis.ipynb` | Demand character, intermittency, seasonality, selection criteria | ✅ Complete | `07_figures/eda/` (5 figures) |
|| 04 | `04_series_selection_and_experimental_design.ipynb` | Representative sample, feasibility, train/val/test design | ✅ Complete | `05_experiments/config.json` |
| 05a | `05a_time_series_components.ipynb` | **Foundation:** level, trend, seasonality, noise, additive vs multiplicative, M5 vs Store Item structure | ✅ Complete | `07_figures/model_explanations/time_series_components/` (19 figures) |
| 05b | `05b_baseline_forecasting.ipynb` | Naïve + Seasonal Naïve + Moving Average baselines (frozen experiment) | ✅ Complete | `06_results/baselines/` |
| 06 | `06_exponential_smoothing.ipynb` | SES + Holt/DES + Holt–Winters/TES | ✅ Complete | `06_results/exponential_smoothing/` |
| 07 | `07_simple_exponential_smoothing.ipynb` | SES | ⬜ Not started | `06_results/ses/` |
| 08 | `08_double_exponential_smoothing.ipynb` | DES (Holt) | ⬜ Not started | `06_results/des/` |
| 09 | `09_triple_exponential_smoothing.ipynb` | TES (Holt-Winters) | ⬜ Not started | `06_results/tes/` |
| 10 | `10_arima.ipynb` | ARIMA | ⬜ Not started | `06_results/arima/` |
| 11 | `11_sarima.ipynb` | SARIMA | ⬜ Not started | `06_results/sarima/` |
| 12 | `12_classical_models_comparison.ipynb` | Classical comparison | ⬜ Not started | `07_figures/classical_comparison/` |
| 13 | `13_lstm.ipynb` | LSTM | ⬜ Not started | `06_results/lstm/` |
| 14 | `14_llm_forecasting.ipynb` | LLM | ⬜ Not started | `06_results/llm/` |
| 15 | `15_forecast_comparison.ipynb` | All-model forecast comparison | ⬜ Not started | `07_figures/forecast_comparison/` |
| 16 | `16_inventory_simulation.ipynb` | Common inventory simulator | ⬜ Not started | `11_src/inventory/` |
| 17 | `17_inventory_results.ipynb` | Inventory outcomes per model | ⬜ Not started | `06_results/inventory/` |
| 18 | `18_sensitivity_analysis.ipynb` | Sensitivity to L, h, p, α | ⬜ Not started | `07_figures/sensitivity/` |
| 19 | `19_statistical_analysis.ipynb` | Paired tests, effect sizes | ⬜ Not started | `06_results/statistical/` |
|| 20 | `20_cross_dataset_robustness.ipynb` | M5 vs Store Item Demand | ⬜ Not started | `07_figures/robustness/` |
| 21 | `21_final_research_findings.ipynb` | Business recommendation | ⬜ Not started | `09_reports/` |

**Legend:** ⬜ Not started · 🟡 In progress · 🟢 Complete · ⏸ Blocked · ⏭ Skipped (documented)

---

## Datasets

| Dataset | Role | Raw location | Rows / series | Common window | Status |
|---------|------|-------------|---------------|---------------|--------|
| Walmart M5 | Primary benchmark | `02_data/dataset_01_m5/raw/` | ~30k series, ~1,913 days | 2013-01-01 → 2016-05-22 (1,238 days) | ✅ Complete |
| Store Item Demand Forecasting | Robustness (RQ4/H4) | `02_data/dataset_02_store_item_demand/raw/` | 500 series, 1,826 days, 913k rows | Same window, equal observations | ✅ Complete (2026-08-27) |

**Archived:** Corporación Favorita — rejected due to structural comparability problems (125M rows, implicit zeros, transactional granularity). Preserved in `_ARCHIVE_2026-08-27_FAVORITA/`.

**Cross-dataset constraint (2026-08-27):** same calendar window, equal observations per series,
reduction by representative selection, window from actual temporal overlap, sample size
evidence-driven. See `decisions.md`.

---

## Model status

| Model | Concept | Implementation | Validation | Forecast | Inventory | Business interpretation |
|-------|---------|---------------|------------|----------|-----------|------------------------|
| Naïve / Seasonal Naïve | ✅ | ✅ | — | ✅ | ✅ | ✅ |
| Moving Average | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| SES | ✅ | ✅ | ✅ | ✅ | ⬜ | ✅ |
| DES | ✅ | ✅ | ✅ | ✅ | ⬜ | ✅ |
| TES | ✅ | ✅ | ✅ | ✅ | ⬜ | ✅ |
| ARIMA | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| SARIMA | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| LSTM | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| LLM | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

---

## Decisions

| Date | Decision | Status | Notebook |
|------|----------|--------|----------|
| 2026-08-22 | Research question + model ladder + datasets + neutrality | Confirmed | — |
| 2026-08-22 | Conceptual freeze (v0.1) | Confirmed | — |
| 2026-08-22 | Operational freeze v1.0 (h=28, n=50, L=7, α=95%, costs) | **Reversed 2026-08-27** | — |
| 2026-08-27 | Clean research reset | Confirmed | RESET_LOG.md |
| 2026-08-27 | Cross-dataset comparability constraint | Confirmed | NB 02, NB 04 |

All decisions live in `00_project/decisions.md`.

---

## Blockers & next actions

| Item | Type | Owner | Status |
|------|------|-------|--------|
| Build 00–04 foundation notebooks | Next action | Agent | 🟢 Complete |
| Determine common window from data overlap | Research decision | NB 02 | ✅ Complete |
| Define series-selection criteria | Research decision | NB 04 | ✅ Complete |
| Choose horizon, splits, policy parameters | Research decision | NB 04 | ✅ Complete |
| Time-series components foundation | Completed | NB 05a |
| Implement Level 1 baselines (Naive, SNaive, MA) | Completed | NB 05b | 🟢 Complete |
| Implement Level 2 smoothing (SES, DES, TES) | Completed | NB 06 | 🟢 Complete |
| Review Notebook 06 before statistical models | Review gate | User | ⬜ Pending |

---

## How to update this file

After completing a notebook, update its row (Status → 🟢, add output path), record any new
decision in `decisions.md`, and move the "Current phase" pointer. Keep this file as the
single dashboard for "where are we?".
