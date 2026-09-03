# Decision Log

This file is the living methodological decision register for the AI Inventory Optimization research project.

**Recording template**

```text
Decision:
Why:
Alternatives considered:
Evidence:
Date:
Impact:
Status:
```

**Rules**
- Every significant research decision is recorded here.
- Previous decisions are never silently replaced.
- If a decision changes: record `Status: Reversed` on the old entry and record the new decision separately.
- "Provisional" = set but may be revisited; "Confirmed" = locked; "Reversed" = superseded.

---

## Initial locked decisions (from planning baseline)

### Title
**Decision:** From Traditional Forecasting to Large Language Models: Evaluating AI-Based Inventory Optimization
**Why:** Identifies both the model progression and the application domain.
**Alternatives considered:** none at this stage (planning-baseline lock).
**Evidence:** Planning pack — README, product.md, research.md.
**Date:** 2026-08-22
**Impact:** Naming for the repository, website, and report.
**Status:** Confirmed

### Research question
**Decision:** How does the effectiveness of AI-based inventory optimization change from traditional forecasting models to large language model–based approaches?
**Why:** Frames the study as an evaluation across forecasting generations with inventory optimization as the target outcome.
**Alternatives considered:** accuracy-only framing (rejected — inventory is the business endpoint).
**Evidence:** Planning pack — research.md, README.md.
**Date:** 2026-08-22
**Impact:** All experiments, metrics, and website content serve this question.
**Status:** Confirmed

### Model progression
**Decision:** MA → SES → DES → TES → ARIMA → SARIMA → LSTM → LLM.
**Why:** Moves from traditional smoothing to statistical to neural to LLM-based approaches, capturing the full evolution of forecasting complexity.
**Alternatives considered:** including XGBoost / gradient boosting (not in the current ladder); naive benchmark as an explicit reference line (candidate for later addition).
**Evidence:** Planning pack — README.md, methodology.md, product.md.
**Date:** 2026-08-22
**Impact:** Scope of 04_forecasting; website model-evolution narrative.
**Status:** Confirmed

### Datasets
**Decision:** Walmart M5 (primary) + Store Item Demand Forecasting (secondary robustness environment).
**Why:** M5 is an established retail benchmark; Store Item Demand provides a second retail demand environment for robustness with comparable structure (daily frequency, store-item panel).
**Alternatives considered:** single-dataset study (rejected — weaker cross-dataset robustness); Favorita (rejected — structural comparability problems, archived 2026-08-27).
**Evidence:** Planning pack — data.md, README.md; Store Item Demand verification (2026-08-27).
**Date:** 2026-08-22 (updated 2026-08-27)
**Impact:** 02_data structure; dataset documentation; cross-dataset analysis.
**Status:** Confirmed (updated 2026-08-27: Favorita replaced by Store Item Demand Forecasting)

### Primary target
**Decision:** Inventory optimization is the business-level endpoint; forecasting accuracy is a means, not the final objective.
**Why:** Better forecasts do not automatically produce better inventory decisions.
**Evidence:** Planning pack — product.md, inventory.md, research_principles.md.
**Date:** 2026-08-22
**Impact:** Inventory simulation, metrics, and interpretation.
**Status:** Confirmed

### Evaluation philosophy
**Decision:** Evaluate on three dimensions: forecast accuracy, inventory outcomes, practicality.
**Why:** A model may be strong in one dimension and weak in another; one-dimensional evaluation is misleading.
**Evidence:** Planning pack — README.md, methodology.md, product.md.
**Date:** 2026-08-22
**Impact:** 06_evaluation structure; final comparison; website section design.
**Status:** Confirmed

### Research principle
**Decision:** Do not assume that the most sophisticated model is the best model.
**Why:** The study is neutral by design; the LLM is not expected to win.
**Evidence:** Planning pack — research_principles.md, llm.md.
**Date:** 2026-08-22
**Impact:** Statistical treatment, interpretation, website messaging.
**Status:** Confirmed

---

## Freeze of the research proposal at the conceptual level

### Decision
Freeze the research proposal at the conceptual level (v0.1), while keeping every experimental parameter open and subject to an explicit decision framework (documented in 01_research/research_proposal.md Section 7).

### Why
The research direction must be stable enough to build the communication layer (proposal website) from, but the exact experimental values (series, horizon, costs, architecture, prompt design, etc.) must not be artificially fixed before EDA, literature review, and validation justify them.

### Alternatives considered
1. Fix all parameters now — rejected: would lock choices that should be evidence-driven and risk biasing the study.
2. Build the website with no frozen proposal — rejected: the planning pack alone is not the stable single source of truth the website needs.

### Evidence
Planning pack (methodology.md, experiment_protocol.md, data.md, decisions.md) explicitly keeps these parameters flexible; user direction (2026-08-22) requested the conceptual freeze + decision framework.

### Date
2026-08-22

### Impact
- 01_research/research_proposal.md created as the single source of truth for the website.
- Website content (12_website) will present experimental parameters as intentionally open, decided through EDA → literature → validation → feasibility → evidence.
- Any future parameter decision must be recorded via the decision template above before use in experiments.

### Status
Confirmed

---

## Explicitly not locked (governed by the decision framework)

- exact M5 series / subset size
- exact Store Item Demand series / subset size
- forecasting horizon
- train/validation/test periods
- rolling-origin evaluation (candidate only)
- seasonal frequency
- LSTM architecture and hyperparameters
- Ollama model and version
- LLM prompt design
- LLM generation parameters
- lead time
- holding cost
- stockout cost
- service-level definition/target
- inventory policy parameters
- order quantity
- statistical testing procedure
- sensitivity-analysis design/ranges
- final visualizations and website result sections

---

## Experiment protocol adopted (operational freeze v1.0)

**Decision:** Adopt `docs/research/experiment-protocol.md` (v1.0) as the binding operational experiment design. Key fixations it makes on top of this log:

- Forecast horizon **h = 28 days** for both datasets (provisional; confirmed at Gate G0 against dataset/business context).
- Scale-independent forecast metric: **RMSSE** (alongside locked MAE + RMSE).
- Train/validation/test: time-based only; test = two consecutive 28-day horizons; rolling-origin remains an optional extension.
- Inventory policy: standardized daily-review order-up-to (R,S) applied identically to every model; primary scenario L = 7 d, service target 95 %, normalized holding cost 1.0/unit/day, stockout penalty 5.0/unit (p/h = 5); lost-sales assumption.
- Controlled research sample: stratified n = 50 series/dataset for Milestone 01 (strata: volume, variability, ADI²/CV² intermittency quadrant, category coverage); scaling deferred until the full ladder runs end-to-end.
- Seasonal-Naïve added as reference line in every phase; univariate demand only for v1 (no covariates).
- Phased build with gates G0–G4; LLM phase strictly last, benchmark frozen before any LLM test scoring (freeze-before-look neutrality safeguard).

**Why:** The proposal froze the conceptual design but left experimental parameters governed by the Section 7 framework. Building requires concrete values; fixing them through one versioned protocol document prevents silent mid-experiment drift that would make the model comparison unfair. All fixations above are marked provisional-vs-locked inside the protocol and remain revisable through this log.

**Alternatives considered:** keeping all parameters open until after ad-hoc experimentation (rejected — invites unfair comparison and irreproducibility); locking everything permanently now (rejected — several values genuinely need EDA evidence first, so the protocol distinguishes locked design from provisional values).

**Evidence:** `01_research/research_proposal.md` §7 decision framework; local environment scan 2026-08-22 (statsmodels/scipy/sklearn present; torch 2.2 CPU has NumPy 2.x ABI conflict → isolated venv required before Phase 3); M5/Kaggle public documentation for horizon feasibility.

**Date:** 2026-08-22

**Impact:** All experiments must conform to the protocol or record a deviation here first. Next work item was Gate G0 — the programmatic dataset audit of M5 and Favorita (`audit_summary.json` per dataset), which confirms/adjusts horizon, sample size, splits, and cost parameters with computed evidence.

**Status:** Confirmed

---

## 2026-08-27 Clean Research Reset — reversal of the operational freeze

### Decision
Void the numeric fixings of "Experiment Protocol operational freeze v1.0" (h = 28, n = 50 series, L = 7 d, α = 95 %, holding cost 1.0, stockout penalty 5.0, two-consecutive-28-day test, RMSSE as a prematurely-locked metric, Milestone-01 three-model pipeline). Re-architect the project as notebook-first, evidence-driven research. All experimental parameters are reopened and must be decided through EDA → literature → validation → feasibility, each recorded here before use.

### Why
The previous implementation locked parameters before any EDA/validation, built a premature website presenting those locked assumptions as findings, and ran only 3 of the 8 ladder models. The master research instruction requires a clean restart prioritizing understanding and documentation over "getting models to run," with parameters decided by evidence rather than convenience.

### Alternatives considered
1. Keep the v1.0 protocol and continue the ladder from Milestone 01 — rejected: it entrenches premature, unvalidated choices that the reset explicitly forbids.
2. Partial reset (keep `11_src` pipeline, remove only website) — rejected: the pipeline itself was built on the voided parameters and encodes the same premature-lock thinking.

### Evidence
Master instruction "Complete Research Reset" (2026-08-27); `01_research/research_proposal.md` §7 (open parameters governed by decision framework); `RESET_LOG.md`.

### Date
2026-08-27

### Impact
- `11_src/` (old pipeline), `07_results/milestone_01/`, and the old Astro website moved to `_ARCHIVE_2026-08-27_RESET/`.
- New directory structure established: `03_processed_data/ 04_models/ 05_experiments/ 06_results/ 07_figures/ 08_notebooks/ 09_reports/ 10_references/ 11_src/`.
- Foundation notebooks `00_research_map` → `03_exploratory_data_analysis` built first; model ladder begins only after they are complete.
- Each rung's parameters (horizon, sample, splits, costs, policy) will be logged here as decided, not assumed.

### Status
Confirmed (supersedes the v1.0 operational freeze for all numeric values; principles retained)

---

## 2026-08-28 Experimental design frozen (Notebook 04)

### Decision
Freeze the experimental design as documented in `08_notebooks/04_series_selection_and_experimental_design.ipynb` and `05_experiments/config.json`. All model implementation must conform to this design.

### Key fixations
- **Common window:** 2013-01-01 to 2016-05-22 (1,238 days)
- **Periods:** Train 1,005d / Validation 120d / Test 83d
- **Forecast horizon:** h = 28 days
- **Origins:** 8 weekly rolling origins in test period
- **M5 sample:** 500 series (stratified by archetype × department)
- **Dataset 02:** All 500 series (no sampling)
- **Common N:** 500 series per dataset (balanced design)
- **Metrics:** MAE, RMSE, sMAPE, WAPE (forecasting); stockout, fill, cost (inventory)
- **Model ladder:** 5 levels — baselines → smoothing → statistical → neural → LLM
- **Random seed:** 42

### Why
The previous v1.0 protocol was voided by the 2026-08-27 reset. This design was built from EDA evidence: the common window comes from verified temporal overlap, the periods respect seasonality requirements, the sample size was assessed against computational feasibility, and the M5 selection was stratified to represent all demand archetypes.

### Alternatives considered
1. Use all 30,490 M5 series — rejected: LSTM/LLM computational cost prohibitive
2. Use h=7 — rejected: too short for monthly planning; limits inventory simulation
3. Single evaluation point — rejected: unreliable; rolling origins needed
4. Random M5 sampling — rejected: may miss rare archetypes (Smooth, Lumpy)

### Evidence
- Notebook 02b audit (verified data dimensions)
- Notebook 04 analysis (archetype classification, feasibility assessment)
- `05_experiments/config.json` (machine-readable source of truth)

### Date
2026-08-28

### Impact
- All downstream notebooks (05–21) must conform to this design
- No model implementation may deviate without a recorded decision
- The config.json file is the single source of truth for experimental parameters

### Status
LOCKED (verified 2026-08-28: all 8 rolling origins confirmed to have 28 valid future observations; no mathematical inconsistency found)

---

## 2026-08-29 Exponential smoothing results and baseline leakage correction

### Decision
Complete Notebook 06 using transparent implementations of SES, Holt/DES, and additive Holt–Winters/TES. Parameters are selected on the validation period only; the final experiment uses 500 M5 series, all 500 Store Item series, 8 origins, and a 28-day horizon.

### Implementation correction
During the Notebook 06 prerequisite review, the Seasonal Naive implementation in Notebook 05 was found to read future columns for forecast steps beyond the seven-day seasonal period. It was corrected to repeat only the last seven observed values. The frozen experimental design was unchanged; Notebook 05 was regenerated and re-executed.

### Evidence
- Notebook 06: 22/22 code cells executed, zero errors, leakage audit PASS.
- Exponential-smoothing forecasts: 672,000 rows with 112,000 rows per model/dataset and zero duplicate keys.
- Corrected Notebook 05 baseline results regenerated before comparison.
- `06_results/exponential_smoothing/metrics_with_baselines.csv` contains the combined comparison.

### Findings
- M5: SES has the lowest MAE/WAPE among the smoothing models; DES and TES do not improve the headline MAE/WAPE under this transparent additive implementation.
- Store Item Demand: SES is the strongest smoothing model by MAE/RMSE/sMAPE; the corrected Seasonal Naive baseline remains competitive.
- These are forecasting findings only; inventory impact remains untested until the inventory simulation.

### Date
2026-08-29

### Impact
- `06_results/exponential_smoothing/` contains forecasts, metrics, validation parameter selection, failure analysis, and execution metadata.
- Educational figures are separated under `07_figures/model_explanations/exponential_smoothing/`.
- Experimental figures are separated under `07_figures/exponential_smoothing/`.
- Notebook 07 remains unopened until Notebook 06 review is complete.

### Status
Complete; Notebook 06 ready for review

---

## 2026-08-29 Notebook restructuring — 05a foundation + 05b baselines

### Decision
Insert a dedicated educational foundation notebook 05a (time series components: level, trend, seasonality, noise, additive vs multiplicative, M5 vs Store Item structure) before the existing baseline experiments. Rename the existing verified baseline notebook 05_baseline_forecasting.ipynb to 05b_baseline_forecasting.ipynb without modifying its models, parameters, results, or frozen experimental design.

### Why
The modelling ladder needs an explicit conceptual foundation. Readers should understand *what* patterns (level, trend, weekly seasonality, noise, sparsity) exist in the two datasets before seeing *how* Naive / Seasonal Naive / Moving Average perform. 05a explains the components; 05b measures the baselines that try to capture them.

### Alternatives considered
- Keep single Notebook 05 mixing education + experiments — rejected: overloads one notebook and breaks the intuition→experiment progression.
- Create 05a as a separate concept note outside the notebook ladder — rejected: the ladder should be self-contained (05a → 05b → 06 → 07).

### Evidence
- 05a: 43 cells (16 code), 0 execution errors, 19 educational figures under 07_figures/model_explanations/time_series_components/.
- 05b: renamed via git mv, verified still 27 code cells, hashes of 06_results/baselines/* unchanged.

### Date
2026-08-29

### Impact
- Notebook order becomes 05a (components) → 05b (baselines, frozen experiment, 112k forecast points per dataset per model) → 06 (SES/DES/TES) → 07 (ARIMA) → ...
- 11_src/_make_nb05.py now builds 05b; new 11_src/_make_nb05a.py builds 05a.
- research_progress.md updated to reflect 05a/05b.

### Status
Complete

---

## 2026-08-27 Dataset 02 migration: Favorita → Store Item Demand Forecasting

### Decision
Replace Corporación Favorita as Dataset 02 with **Store Item Demand Forecasting** (Kaggle: `akshaymairal/store-item-demand-forecasting-challenge`). Favorita is archived as a rejected dataset.

### Why
The 125M-row Favorita transaction dataset created insurmountable computational and structural comparability problems with M5:
- Implicit zero-sales (missing rows vs. explicit zeros) made panel construction unreliable
- Transactional granularity (not daily store-item aggregates) required complex, error-prone preprocessing
- The 125M-row scale made iterative EDA and model development impractical
- Cross-dataset comparability with M5 was structurally compromised

Store Item Demand Forecasting provides:
- 913,000 rows (manageable scale)
- Complete panel (every store-item-date combination present)
- Daily frequency (matching M5)
- 10 stores × 50 items = 500 series (feasible for all models)
- 1,826 days (2013-01-01 to 2017-12-31)
- Clean, simple structure: date, store, item, sales

### Alternatives considered
1. Continue debugging Favorita — rejected: structural problems are inherent to the dataset, not fixable
2. Sample from Favorita — rejected: would lose the cross-dataset robustness value
3. Use a different dataset entirely — considered but Store Item Demand is the closest match to M5's structure

### Evidence
- Favorita audit: 125M rows, implicit zeros, complex preprocessing required (archived in `_ARCHIVE_2026-08-27_FAVORITA/`)
- Store Item Demand verification: 913,000 rows, complete panel, 0 missing combos, 0 duplicates, only 1 zero-sales entry
- Temporal overlap with M5: 1,238 days (2013-01-01 to 2016-05-22) — sufficient for cross-dataset experiment

### Date
2026-08-27

### Impact
- `02_data/dataset_02_grocery/` archived to `_ARCHIVE_2026-08-27_FAVORITA/`
- `02_data/dataset_02_store_item_demand/` created with raw/processed/audit structure
- `08_notebooks/02b_favorita_acquisition_and_audit.ipynb` archived, replaced by `02b_store_item_demand_acquisition_and_audit.ipynb`
- All active Favorita references in notebooks, config, and docs updated
- Cross-dataset experiment now compares M5 (30,490 series) vs Store Item Demand (500 series)
- All 500 series feasible for full model ladder — no sampling needed

### Status
Confirmed

---

## 2026-08-27 Favorita dataset acquisition — Outcome A (complete)

### Decision
Favorita dataset is now **complete and verified** (125M rows, 1,684 days, 54 stores, 4,036 items). Source: Kaggle official competition dataset (`siliconx/favoritagrocerysalesforecastingextracted`). Cross-dataset robustness (RQ4/H4) is now **feasible** with 1,207 common days (2013-01-01 → 2016-04-24).

### Why
Previous copy was truncated to 198 days with corrupted archive. Complete dataset required for cross-dataset robustness analysis per user constraint (2026-08-27).

### Evidence
`02_data/dataset_02_grocery/audit_summary.json` updated; notebook `02b_favorita_acquisition_and_audit.ipynb` documents full verification.

### Date
2026-08-27

### Impact
- `02_data/dataset_02_grocery/raw/` now contains the complete official data
- Old truncated data quarantined to `_QUARANTINE_TRUNCATED/`
- `04_series_selection_and_experimental_design.ipynb` must select series from both datasets over common window
- H4 (cross-dataset consistency) can now be tested

### Status
Confirmed

---

## 2026-08-27 User constraint — cross-dataset comparability (arrived during reset)

### Decision (constraint)
The M5 and Favorita experiments must be made comparable on a controlled common basis:
1. **Shared calendar window** — both datasets are analyzed over the *same* primary date window, with **equal number of observations per experimental series**.
2. **Reduction by selection, not by truncation** — dataset reduction happens primarily through **representative series selection**, not by arbitrarily shortening each series' temporal history.
3. **Window from real overlap** — the common window is established from the *actual temporal overlap* of M5 and Favorita and justified via EDA/research reasoning.
4. **Sample size evidence-driven** — the final number of series is determined by representativeness + computational-feasibility analysis, not fixed in advance.

### Why
Without a shared window and equal-length series, cross-dataset robustness (RQ4 / H4) and the master comparison framework would confound "model effect" with "different history lengths / different calendars." This protects the fair-comparison principle.

### Alternatives considered
- Per-dataset native windows with independent lengths — rejected: breaks cross-dataset comparability.
- Fixed n = 50 chosen a priori — rejected: contradicts "number of series determined by representativeness + feasibility."
- Truncate series to a short uniform history — rejected: contradicts "reduction by selection, not truncation."

### Evidence
Direct user instruction (2026-08-27, out-of-band). To be operationalized in `02_data_acquisition_and_audit.ipynb` (compute actual overlap) and `04_series_selection_and_experimental_design.ipynb` (stratified representative sample + feasibility).

### Date
2026-08-27

### Impact
- `02_data_acquisition_and_audit.ipynb` must compute and justify the common window (expected ≈ 2013-01-01 → 2016-06-19, the M5/Favorita overlap; verified from data).
- Series-selection criteria must require full coverage of the common window (equal observations) and stratify by demand character.
- `05_experiments/` config will record the decided window + n with evidence.

### Status
Confirmed

---

## 2026-08-31 ARIMA/SARIMA deep teaching and rolling evaluation (Notebook 07)

### Decision
Complete Notebook 07 with transparent ARIMA (1,1,0) full rolling evaluation on 500 M5 + 500 Store Item Demand series (8 weekly origins, h=28) and SARIMA (1,1,0)(0,1,1,7) as a seasonal focus on a 100-series Store Item subset. Orders fixed for speed/generalizability after a quick validation sanity check; no test data used for selection.

### Why
ARIMA provides the statistical view of autocorrelation/stationarity that smoothing does not, and SARIMA adds seasonal autocorrelation (m=7). Small orders keep per-fit time ~0.03s (ARIMA) and ~0.31s (SARIMA) and avoid over-differencing. Sparse M5 series with >85% zeros fall back to Naive to avoid fitting noise (documented).

### Evidence
- 07: 36 cells (17 code), 0 execution errors, 11 inline images, 7 educational + 4 experimental figures
- ARIMA: 224000 rows (112000 per dataset, 500×8×28) + SARIMA subset 22400 rows (100×8×28) = 246400 rows total, duplicate keys 0, non-negative forecasts
- Metrics: m5 ARIMA WAPE 0.885 (worse than SES 0.78, better than DES/TES), store_item ARIMA WAPE 0.208, SARIMA subset WAPE 0.153 vs Store Item SES 0.173 — seasonal MA helps where weekly CV is high
- Leakage audit PASS, frozen window/origins/metrics/seed unchanged, baseline hashes unchanged
- Runtime 897s (just under 900s cell budget) with scipy 1.14.1 fix and ai-inventory kernel

### Alternatives considered
- Larger p,q,P,Q grid search per series — rejected: 0.5s×9600 fits would exceed notebook budget and overfit sparse series
- Full 500×8 SARIMA on both datasets — rejected for budget; instead 100-series Store Item focus where seasonality is strong, clearly labelled as subset

### Date
2026-08-31

### Impact
- Results in 06_results/arima/ (all_forecasts.csv, arima_forecasts.csv, sarima_store_item_subset.csv, metrics_by_model/series/origin, metrics_by_archetype_m5, metrics_with_history)
- Figures: 07_figures/model_explanations/arima/ (7) and 07_figures/arima/ (4)
- Next: 08 LSTM deep teaching; SARIMA full-500 evaluation deferred to final comparison notebook if needed

### Status
Complete

---

## 2026-09-02 Phase 1 complete — traditional forecasting baseline frozen

### Decision
Phase 1 is frozen. All traditional forecasting models (Naive, Seasonal Naive, Moving Average, SES, DES, TES, ARIMA, SARIMA, Global LSTM) have been evaluated on both datasets under identical conditions. Inventory simulation complete. Baseline locked as the reference for Phase 2 SLM/LLM.

### Evidence
- 08_lstm.ipynb executed: 33 cells, 17 code, 0 errors, 7 images
- Inventory simulation: 8 models × 2 datasets, lost-sales order-up-to policy, 0 errors
- All forecast metrics: MAE, RMSE, sMAPE, WAPE per model per dataset
- All inventory metrics: total cost, service level, holding cost, stockout cost
- 6 inventory figures saved to 07_figures/inventory/
- Phase 1 final report: 09_reports/phase1/PHASE_1_FINAL_REPORT.md
- Phase 1 methodology: 09_reports/phase1/PHASE_1_METHODOLOGY.md

### Key findings
- M5 (sparse): LSTM best on both forecast and inventory
- Store Item (dense): Moving Average best on inventory despite lower forecast accuracy
- Forecast accuracy does not automatically equal better inventory decisions

### Date
2026-09-02

### Impact
- Git tag phase-1-complete created
- All Phase 1 results frozen
- Phase 2 SLM/LLM must compare against this baseline

### Status
Complete — frozen

---

## 2026-09-03 Temporal protocol correction — leap day 2016-02-29 assigned to validation

### Decision
Correct the frozen experimental calendar so every calendar day of the common window belongs to exactly one period:

- **Train:** 2013-01-01 → 2015-10-31 (1,034 days)
- **Validation:** 2015-11-01 → 2016-02-29 (121 days) — includes the 2016-02-29 leap day
- **Test:** 2016-03-01 → 2016-05-22 (83 days)
- **Common window:** 2013-01-01 → 2016-05-22 (1,238 days)

### Why
2016 is a leap year. The original Notebook 04 freeze ended validation at 2016-02-28 (120 d), leaving 2016-02-29 unassigned — a "gap day in no period" — so the split summed to 1,237 days, not the 1,238-day common window (the 2026-08-28 freeze record's "Train 1,005d" figure was likewise internally inconsistent; the true train length is 1,034 d). Ending validation on 2016-02-29 restores the exact partition: 1,034 + 121 + 83 = 1,238. Test and all 8 rolling origins are unchanged; model selection still uses validation only.

### Impact
- `05_experiments/config.json` (git-ignored; machine-readable source of truth): validation end 2016-02-28 → 2016-02-29, days 120 → 121.
- `11_src/_make_nb05.py`: protocol table and prose (`val_end`, slice comments, gap-day text), MA-window selection record, and assertions updated — VAL_S is now 121 columns, periods sum to 1,238, and a boundary assertion verifies validation ends exactly where test begins (no gap day).
- `11_src/_make_nb06.py`: protocol table + `VAL_END` constant updated.
- `11_src/_make_nb07.py`: implementation-section prose updated.
- Prior artifacts preserved: `08_notebooks/*.ipynb` and `06_results/` were NOT regenerated or rewritten. Notebooks 05–07 must be regenerated from the patched sources and results re-verified before any downstream experiment.

### Status
Confirmed — sources patched; notebook regeneration deferred by instruction.

---

## 2026-09-04 SARIMA full-500 feasibility decision (Research Hardening)

### Decision
Run SARIMA (1,1,0)(0,1,1,7) on all 500 Store Item Demand series (8 origins, H=28, identical history<origin boundary) via standalone script. Retain the 100-series subset strictly as labelled exploratory artifact.

### Why
Feasibility probe (05_experiments/sarima_feasibility.json): 16 fits, 16 ok, mean 0.62 s/fit → full 4000-fit ETA ~41 min as a background script, outside the 900 s notebook-cell budget but well within project constraints. Full run actual: 2382 s, 4000/4000 fit_ok, 0 skips, 0 failures (run_log_full500.json). 0-failure convergence is itself a finding (dense Store data vs 22.65% ARIMA pre-check fallback on sparse M5).

### Alternatives considered
1. Keep 100-series subset as primary SARIMA — rejected: directly incomparable populations (22400 vs 112000 rows) would poison the primary comparison.
2. Run SARIMA on M5 too — rejected: seasonal differencing on >85%-zero intermittent series is methodologically dubious; Croston-family already covers the M5 specialty.

### Evidence
- 06_results/arima/sarima_store_item_full500.csv (112000 rows, 0 dup keys)
- 06_results/arima/convergence_details_full500.csv + convergence_report.csv (scope column)
- Rebuilt 06_results/arima/all_forecasts.csv (336000 = 224000 ARIMA + 112000 SARIMA-full500); subset-based version preserved in 06_results/_pre_hardening_backup/06_results/arima/all_forecasts_subset_based.csv
- Full500 metrics: MAE 8.45 / WAPE 0.148 / MASE 1.055 / RMSSE 1.040 (subset was 8.31/0.153 — consistent, population shift documented, not hidden)

### Impact
- Primary comparison uses identical 500-series populations on both datasets for every model.
- Downstream inventory/stats/sensitivity rerun on rebuilt forecasts (Store SARIMA pairs change from subset to full population).

### Status
Confirmed

