> ⚠️ **SUPERSEDED FOR NUMERIC FIXATIONS (2026-08-27 reset).** This document's *principles*
> (temporal integrity, fair comparison, one common inventory policy, neutral reporting) remain
> valid and are carried forward into the notebook-first research. However, its v1.0 numeric
> lockings (h = 28, n = 50 series, L = 7 d, α = 95 %, holding cost 1.0, stockout penalty 5.0,
> two-origin test, RMSSE as a prematurely-locked metric) were set *before* any EDA or validation
> and are **voided** by the 2026-08-27 clean research reset. Those parameters are reopened and
> will be re-decided through EDA → literature → validation → feasibility, recorded in
> `00_project/decisions.md`. See `RESET_LOG.md`.
>
> # Experiment Protocol — v1.0 (historical; superseded)

> **Status:** Active — experimental design locked at the operational level. Changes follow §13 (Change control).
> **Date:** 2026-08-22
> **Authority:** Implements `01_research/research_proposal.md` (conceptual freeze v0.1). Where the proposal declares a parameter *open*, this protocol fixes either (a) the value, or (b) the decision procedure that produces the value. Every deviation from this document requires an entry in `00_project/decisions.md` **before** the deviation is used in any reported experiment.
> **Documentation principle:** This is the experiment's constitution, not its diary. Execution state lives in notebooks/scripts outputs; decisions live in the decision log; only the rules live here.

---

## 1. Purpose

This document makes the comparison fair and the experiments reproducible. It exists because the most likely way this study fails is silently: a horizon changed mid-experiment, a policy tuned per model, a test period drifting — none of which look like cheating but all of which make the comparison meaningless.

Two kinds of content live here:

| Kind | Examples | May change |
| --- | --- | --- |
| **Locked design** | models, datasets, split logic, metrics, policy structure | only via decision log (§13) |
| **Provisional values** | horizon default, cost ratios, sample size | confirmed/revised at gates, evidence recorded |

---

## 2. Frozen design summary

| Component | Decision | Status |
| --- | --- | --- |
| Research question | How does effectiveness change from traditional forecasting → LLM-based approaches, measured at the inventory-outcome level? | Locked |
| Models | MA, SES, DES, TES, ARIMA, SARIMA, LSTM, LLM (local via Ollama) — plus Naïve as reference line | Locked |
| Datasets | Walmart M5 (primary) + Store Item Demand Forecasting (secondary robustness) | Locked |
| Forecast horizon | Default **h = 28 days** both datasets (M5-aligned; supports lead-time scenarios ≤ 28 d) | Provisional — confirmed at Gate G0 |
| Train/test method | Time-based split only; final holdout + optional rolling-origin extension (§8) | Locked (method), provisional (rolling) |
| Forecast metrics | MAE, RMSE, **RMSSE** (the single scale-independent metric) | Locked |
| Inventory metrics | Total cost (holding + stockout), stockout rate, service level (+ avg. inventory, order frequency as diagnostics) | Locked |
| Inventory policy | One standardized policy applied identically to every model: daily-review order-up-to (§10) | Structure locked; numeric defaults provisional |
| Evaluation | Same test periods, same input history, same policy, same assumptions for all models | Locked |
| Result principle | **Do not assume the LLM wins.** Report outcomes in whichever direction they fall | Locked |

---

## 3. Hypotheses (neutral framing)

The study tests claims, it does not defend one. Stated so that *any* outcome is informative:

- **H1:** Forecast accuracy differs significantly across model generations on the same series and horizons.
- **H2:** Forecast-accuracy differences translate into measurable inventory-outcome differences under a common policy.
- **H3:** Increasing model sophistication yields monotonically improving inventory outcomes. *(This is the claim under test — H3 may well be rejected; rejection is a publishable finding, not a failure.)*
- **H4:** Observed patterns are consistent across the two retail environments (M5, Store Item Demand).

No hypothesis is privileged. The analysis plan (§12) is fixed before test-set results are generated.

---

## 4. Models and build phases

```text
Phase 1   Traditional      MA → SES → DES → TES        (statsmodels)
Phase 2   Statistical      ARIMA → SARIMA              (statsmodels; order selection on validation only)
Phase 3   Neural           LSTM                        (PyTorch; architecture per proposal §7.6)
Phase 4   LLM              Local model via Ollama      (prompt artifact versioned in 08_llm/prompts/)
```

Rules that hold in every phase:

1. **Reference line:** Seasonal-Naïve (repeat last seasonal period) runs alongside every phase. It is not one of the eight ladder models; it guards against complexity beating a trivial baseline by accident.
2. **Identical inputs:** every model receives the same training history (same start date, same end date), the same covariates where covariates are used at all (default: **none** — univariate demand only, for v1; covariates are a possible extension recorded via decision log).
3. **Phases gate on the previous one:** Phase N work begins only after Phase N−1 produces end-to-end forecasts through the inventory simulation. The LLM (Phase 4) is built strictly last, against a frozen benchmark.

---

## 5. Data environments and audit plan

### 5.1 Known facts (public documentation — verified programmatically at audit)

| Property | Walmart M5 | Store Item Demand Forecasting |
| --- | --- | --- |
| Source | Kaggle “M5 Forecasting — Accuracy” | Kaggle “Store Item Demand Forecasting Challenge” |
| Unit of demand | Units sold per item × store × day | Units sold per item × store × day |
| Frequency | Daily | Daily |
| Files | `sales_train_[validation/evaluation].csv`, `sell_prices.csv`, `calendar.csv` | `train.csv`, `test.csv`, `sample_submission.csv` |
| Approx. scale | 3,049 items × 10 stores ≈ 30 k series; ~5 years (2011‑01‑29 → 2016‑06‑19) | 50 items × 10 stores = 500 series; 5 years (2013‑01‑01 → 2017‑12‑31); 913k rows |
| Covariates available | Calendar events, SNAP flags, sell prices | None (univariate demand only) |
| Intermittency | High zero-inflation at item-store level | Very low (only 1 zero-demand day in entire dataset) |
| Panel structure | Wide format (d_1..d_1913 columns) | Long format (date, store, item, sales) |
| Access | Kaggle account required (license terms accepted at download) | Kaggle account required (same) |

Items marked “approx.” are documentation-level figures; the audit (§5.3) replaces every approximated number with a computed one before Gate G0 closes.

### 5.2 Unknowns to resolve at audit (never guessed)

- Exact usable series counts after quality filters (min history length, missingness thresholds).
- Real missing-value structure (M5 documents none in sales; Dataset 02 verified complete — count, don't assume).
- Price coverage for M5 (`sell_prices` sparsity affects any price-based extension).
- Store Item Demand date-range edges and store/item coverage.
- Local feasibility: memory ceiling for row-level operations, per-model runtime per series.

### 5.3 Audit procedure (Gate G0)

For **each** dataset, produce one notebook/script + one machine-readable summary (`02_data/<dataset>/audit_summary.json`) answering, with computed evidence:

1. **Target definition** — what one row means; how demand relates to sales (stockout-censoring caveat noted).
2. **Frequency & calendar** — confirm daily; identify gaps; establish date bounds.
3. **Usable-series count** — apply quality filters (§6.1); report survivors.
4. **Covariate inventory** — which auxiliary files join cleanly; which are ignored in v1.
5. **Missing values** — count by series; distribution of gap lengths; imputation policy for the *pipeline* (v1: missing days = 0 demand only if store closed is verifiable; otherwise series excluded — record choice).
6. **Intermittency profile** — zero-demand share; ADI²/CV² quadrant classification per series (feeds §6 stratification).
7. **Horizon fit** — confirm h = 28 feasible (enough post-history for test + lead time); else trigger horizon revision via decision log.
8. **Feasibility** — load time, peak memory, projected per-model runtime; confirm or revise the controlled-sample size (§6.2).

Audit outputs feed exactly two places: Gate G0 closure and the dataset sections of the thesis data chapter. Nothing enters the website from the audit except facts already in the frozen proposal.

---

## 6. Controlled research sample

### 6.1 Quality filters (applied identically to both datasets)

A series is usable when it has: ≥ 3 full years of daily history (≥ 1,095 observed days after gap handling), ≤ 1 % missing days, non-zero cumulative demand, and full covariate alignment where covariates are used (v1: not applicable).

### 6.2 Stratified sample (method locked; size provisional)

Selection is **stratified by demand character**, never by model-friendliness:

| Stratum axis | Levels |
| --- | --- |
| Volume | low / medium / high terciles |
| Variability | CV terciles |
| Intermittency | ADI²/CV² quadrants (smooth / intermittent / erratic / lumpy) |
| Category/dept | proportional coverage of dataset's own hierarchy |

Provisional size: **n = 50 series per dataset** for Milestone 01 and all methodology-validation work; scaling (n = 100–300) only after Gate G2 confirms the full ladder runs end-to-end. Final counts recorded at G0 with evidence.

---

## 7. Temporal integrity (locked)

- Time-based splits only. No shuffle, no random folds, ever.
- Split boundaries are chosen once per dataset at G0 and never move afterwards.
- Any statistic fitted from data (residual variance, scaler, seasonal indices, ARIMA order, LSTM weights) is fitted on training/validation data only.
- The LLM prompt contains only information timestamped before the forecast origin. Prompt templates are diffed against a leak-checklist before first use.
- Rolling-origin extension (if adopted): origins advance by a fixed step (default 28 days), retraining permitted per origin, same holdout logic inside each origin.

---

## 8. Train / validation / test design

Default shape (boundaries fixed at G0):

```text
|<—————— TRAIN ——————>|<— VALIDATION —>|<—— TEST ——>|
     model fitting        model selection,   final scoring,
     (per model class)    hyperparams, σ̂    never seen before
                          estimation          the analysis freeze
```

- Validation window: last ~10 % of pre-test history (multiple 28-day blocks preferred, to stabilize residual estimates).
- Test window: final **two consecutive 28-day horizons** (56 days) per dataset — enough for two independent forecast origins without exploding compute.
- Rolling-origin upgrade remains a candidate per proposal §7.4; adopt only with a feasibility note in the decision log.

---

## 9. Forecast metrics (locked)

| Metric | Role | Aggregation |
| --- | --- | --- |
| MAE | primary magnitude error | mean over series; per-stratum breakdown |
| RMSE | large-error sensitivity | mean over series |
| **RMSSE** | the scale-independent metric | mean over series (unweighted); WRMSSE-style weighting reported as diagnostic only |

Why RMSSE: it is the M5 benchmark's native scaled metric, defined per series as RMSE of the model ÷ RMSE of the seasonal-naïve in-sample one-step errors; unlike sMAPE it behaves sensibly with intermittent demand, and unlike MASE it does not degenerate when the naïve denominator approaches zero. Computed per series, then averaged — never pooled across series before scaling.

Practicality metrics (runtime, peak RAM, lines of configuration) are logged automatically by the pipeline harness in every run — they cost nothing to collect and feed proposal dimension 3.

---

## 10. Inventory simulation (structure locked)

> This is the heart of the study: every model's forecast feeds the **identical** decision mechanism. Differences in outcomes are attributable to differences in forecasts — nothing else.

### 10.1 Policy — daily-review order-up-to (R, S)

Per series, simulated day by day over the test window:

```text
each day t:
  1. observe on-hand inventory
  2. place order to raise position up to S_t   (arrives after lead time L)
  3. demand occurs: satisfied from stock; unmet demand = LOST (counted, penalized)
  4. holding cost charged on end-of-day on-hand
  5. log: stockout event, service level contribution, inventory level, orders
```

- **Review period** R = 1 day (daily review).
- **Order-up-to level** `S_t = round( μ̂_{t:t+L} + z_α · σ̂ )` where `μ̂` = sum of the model's forecasts over the lead-time window, `z_α` = normal quantile of the service target, `σ̂` = forecast-error standard deviation estimated on **validation data only**, floored at `√(max(μ̂,1))` for stability on intermittent series.
- Every model supplies `μ̂` and `σ̂` through the same interface. No model may tune policy internals.

### 10.2 Scenario grid

One **primary scenario** carries the headline comparison; sensitivity varies one factor at a time around it.

| Parameter | Primary | Sensitivity |
| --- | --- | --- |
| Lead time L | 7 days | {3, 14} |
| Service target α | 95 % | {90 %, 98 %} |
| Holding cost h | 1.0 per unit per day (normalized currency) | — |
| Stockout penalty p | 5.0 per unit of unmet demand (p/h = 5) | {2, 10} |

All values provisional until G0 records dataset-grounded justification (proposal §§7.10–7.13); the **structure** — one policy, one grid, every model through it — is locked now.

### 10.3 Simulation assumptions (explicit, documented)

- Lost sales, no backorders (retail-plausible; backorder variant = possible extension).
- Initial inventory = S₀ at simulation start; first L days treated as warm-up and excluded from reported metrics.
- Unlimited supplier capacity, no order-size constraints, no fixed ordering cost (limitation acknowledged; fixed ordering cost would push toward (s,Q) — candidate extension via decision log).
- Demand during stockout is observable (lost-demand counter), sidestepping censoring ambiguity inside the simulation. Real-data censoring is a *dataset* caveat, noted in interpretation.
- Results labeled **simulated under stated assumptions** everywhere they appear — never as reconstruction of actual retailer operations.

### 10.4 Inventory metrics (locked)

| Metric | Definition |
| --- | --- |
| Total inventory cost | Σ holding cost + Σ stockout penalty over scored days |
| Stockout rate | fraction of (series, day) pairs with unmet demand > 0 |
| Service level | satisfied demand ÷ total demand (unit-fill rate), per series then averaged |
| Diagnostics | average on-hand inventory; order frequency |

---

## 11. Evaluation workflow and gates

```text
G0  Dataset audit closed          both audits complete; sample + splits + horizon confirmed
G1  Milestone 01                  M5 → [Naïve + MA + SES] → forecasts → simulation → cost/stockout/service
G2  Benchmark ladder stable       Phases 1–2 end-to-end on both datasets; harness logs practicality metrics
G3  Neural integrated             LSTM through the same interface; tuning confined to validation
G4  LLM integrated                Phase 4 through the same interface; benchmark FROZEN before first LLM score
```

Gate rule: a gate closes only when its artifact exists, runs from a clean checkout, and its numbers regenerate. The next phase's modeling work does not start early.

**Freeze-before-look (neutrality safeguard):** before any model scores the test window beyond Milestone-01 smoke-testing, the analysis script (metric aggregation, tables, figure skeletons, planned comparisons) is written and committed. Results are reported in whatever direction they fall; negative or null findings are preserved, not polished.

---

## 12. Analysis plan (fixed before test results)

1. Descriptive: per-metric distributions by model and stratum.
2. Paired comparisons: models see identical series/windows → per-series pairing supports Wilcoxon signed-rank (pairwise) and Friedman + post-hoc Nemenyi (across the ladder). Exact battery confirmed at G2 per proposal §7.15.
3. Effect framing: report effect sizes alongside p-values; with n = 50 series, emphasize magnitude and consistency, not bare significance.
4. Robustness: winner stability across the §10.2 sensitivity grid (does the ranking survive assumption changes?).
5. Cross-dataset: same tables recomputed on Store Item Demand; concordance reported per H4.

---

## 13. Change control

- This document is versioned. Material changes → bump version, add a dated changelog line below, and record a decision-log entry **before** running affected experiments.
- The decision log (`00_project/decisions.md`) remains the only register of *why* something changed; this file states only *what currently holds*.
- Provisional values confirmed at a gate are promoted here with their evidence pointer — silently editing a number without a log entry is a protocol violation.

**Changelog**

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-22 | Initial operational freeze: design table, audit plan, sample strategy, metrics, policy structure, gates, analysis plan. |

---

## 14. Milestone 01 — End-to-end baseline (next concrete work)

Scope: prove the architecture with minimum moving parts.

```text
Walmart M5 (audit subset, n = 50 stratified series)
   ↓
Seasonal-Naïve + Moving Average + SES        ← three models, one harness
   ↓
Forecasts, h = 28, two test origins
   ↓
Order-up-to policy (L = 7, α = 95 %, h = 1, p = 5)
   ↓
Simulation (lost sales, warm-up excluded)
   ↓
Total cost · stockout rate · service level (+ MAE/RMSE/RMSSE)
```

Done when: `11_src` pipeline runs from a clean checkout with pinned dependencies, emits per-series forecast files, per-run simulation ledgers, and one summary table comparing the three models on all six metrics — with runtime logged. If Milestone 01 reproduces, adding DES/TES is a config change, not a research problem; the remaining ladder inherits a proven skeleton.

---

## 15. Reproducibility contract (applies to every run)

1. Dependencies pinned (`requirements.txt` via uv; torch stack isolated in a dedicated venv — host NumPy 2.x vs torch 2.2 ABI conflict is a known hazard, resolved before Phase 3).
2. Seeds fixed and logged: numpy, random, torch (CPU-deterministic flags on), sampled at run start, written into every output manifest.
3. Environment manifest per run: package versions, dataset file hashes, config hash, git commit.
4. LLM determinism: temperature 0 where supported; model name + version + quantization logged; prompt template hash recorded per response; invalid outputs logged verbatim, never repaired.
5. Every experiment writes an output manifest (`07_results/model_outputs/<run_id>/manifest.json`) sufficient to re-plot the run's figures without re-training anything.
