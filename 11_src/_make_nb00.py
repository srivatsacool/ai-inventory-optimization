"""Generate the 00_research_map.ipynb notebook."""
import nbformat as nbf
nb = nbf.v4.new_notebook()
nb.metadata["kernelspec"] = {
    "display_name": "AI Inventory (venv)",
    "language": "python",
    "name": "ai-inventory"
}
nb.metadata["language_info"] = {"name": "python", "version": "3.12.3"}

cells = []

# ── Title ────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""# 00 — Research Map

**From Traditional Forecasting to Large Language Models: Evaluating AI-Based Inventory Optimization**

---

## Central research question

> **How does the effectiveness of AI-based inventory optimization change from traditional forecasting models to large language model–based approaches?**

This notebook is the *dashboard* for the entire investigation. It is readable
without running every experiment: it records the question, hypotheses, model
ladder, datasets, evaluation framework, key decisions, and current progress.
"""))

# ── Hypotheses ───────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## Hypotheses (neutral framing)

| # | Statement | Interpretation if rejected |
|---|-----------|--------------------------|
| H1 | Forecast accuracy differs significantly across model generations on the same series and horizons. | Simple methods already capture the signal; added complexity doesn't improve accuracy. |
| H2 | Forecast-accuracy differences translate into measurable inventory-outcome differences under a common policy. | Inventory outcomes are robust to forecast quality; policy design matters more than forecast precision. |
| H3 | Increasing model sophistication yields *monotonically* improving inventory outcomes. | A simpler model may outperform a complex one in inventory terms — a publishable finding. |
| H4 | Observed patterns are consistent across the two retail environments (M5 and Favorita). | The findings are dataset-specific and may not generalise. |

No hypothesis is privileged. A negative finding is as valuable as a positive one.
"""))

# ── Model ladder ─────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## The model ladder

The models progress from traditional smoothing → statistical → neural → LLM-based
approaches. Complexity increases along the ladder; whether *value* increases with
complexity is the empirical question this study answers.

```text
┌─────────────────────┐
│  Naive / Seasonal    │  ← baselines
│  Naive               │
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│  Moving Average      │  ← traditional
│  SES                 │
│  DES                 │
│  TES                 │
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│  ARIMA               │  ← statistical
│  SARIMA              │
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│  LSTM                │  ← neural
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│  LLM                 │  ← large language model
└─────────────────────┘
```

Every model feeds the **same** inventory simulation — differences in outcomes are
attributable to differences in forecasts, not in policy design.
"""))

# ── Datasets ─────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## Datasets

| Dataset | Role | Source | What it allows |
|---------|------|--------|---------------|
| Walmart M5 | Primary | Kaggle M5 Forecasting — Accuracy | 30,490 item-store series; daily; ~5 years; hierarchical retail demand; established benchmark |
| Corporación Favorita | Robustness (RQ4/H4) | Kaggle Grocery Sales Forecasting | Multiple stores/items; promotions; oil prices; holidays |

**Status (2026-08-27):** Favorita data is severely truncated — only 198 days of sales are
available (2013-01-01 to 2013-07-17) with a corrupted archive. The full dataset would cover
~4.5 years. This limits cross-dataset robustness analysis to a **planned** but **currently
infeasible** second environment.

**Common calendar window (user constraint, 2026-08-27):** Both datasets must share the same
primary date window with equal observations per experimental series, established from the
actual temporal overlap. See `02_data_acquisition_and_audit.ipynb` for the evidence.
"""))

# ── Evaluation framework ─────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## Evaluation framework

Three distinct dimensions, none reducible to the others:

```text
            MODEL
              │
      ┌───────┼────────┐
      ↓       ↓        ↓
 Forecast   Inventory  Practicality
 Accuracy   Outcomes   & Complexity
```

**Forecast accuracy** — MAE, RMSE, RMSSE (scale-independent), sMAPE, MASE.

**Inventory outcomes** — total cost (holding + stockout), stockout rate, service level,
average inventory, order frequency. A common order-up-to (R, S) policy with identical
parameters for every model.

**Practicality** — runtime, RAM, complexity, interpretability, reproducibility, latency.

**Critical insight:** better forecast accuracy does not automatically yield better
inventory outcomes. A model with *worse* MAE can produce *better* inventory cost if its
error structure is less harmful. This is one of the most important business findings the
study may produce.
"""))

# ── Key design principles ────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## Key design principles

| Principle | What it means in practice |
|-----------|--------------------------|
| **Neutrality** | The LLM is not expected to win. Any outcome is informative. |
| **Time integrity** | No future information enters training, preprocessing, features, prompts, or inventory decisions. |
| **Fair comparison** | Same demand data, horizons, test periods, policy, cost assumptions, and metrics for every model. |
| **Complexity earns its place** | Models are added to the ladder only because they represent a methodological generation, not because they are fashionable. |
| **No fabricated completeness** | Unfinished analysis is marked unfinished. Invented values are never substituted. |
| **Literature verified** | Published claims are verified before use as evidence; not assumed true because they appear in a paper. |

For the full research proposal: `01_research/research_proposal.md`
For operational decisions and their rationale: `00_project/decisions.md`
"""))

# ── Current progress ─────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## Current progress

| Phase | Status | Notebook(s) |
|-------|--------|-------------|
| 0 — Repository reset | ✅ Complete | `RESET_LOG.md` |
| Foundation — Environment | ✅ Complete | `01_environment_and_reproducibility.ipynb` |
| Foundation — Data audit | ✅ Complete | `02_data_acquisition_and_audit.ipynb` |
| Foundation — EDA | ✅ Complete | `03_exploratory_data_analysis.ipynb` |
| Series selection | ⬜ Pending | `04_series_selection_and_experimental_design.ipynb` |
| Baseline — Naïve / Seasonal Naïve | ⬜ Pending | `05_baseline_seasonal_naive.ipynb` |
| Traditional — MA | ⬜ Pending | `06_moving_average.ipynb` |
| Traditional — SES | ⬜ Pending | `07_simple_exponential_smoothing.ipynb` |
| Traditional — DES | ⬜ Pending | `08_double_exponential_smoothing.ipynb` |
| Traditional — TES | ⬜ Pending | `09_triple_exponential_smoothing.ipynb` |
| Statistical — ARIMA | ⬜ Pending | `10_arima.ipynb` |
| Statistical — SARIMA | ⬜ Pending | `11_sarima.ipynb` |
| Classical comparison | ⬜ Pending | `12_classical_models_comparison.ipynb` |
| Neural — LSTM | ⬜ Pending | `13_lstm.ipynb` |
| LLM — Forecasting | ⬜ Pending | `14_llm_forecasting.ipynb` |
| Forecast comparison | ⬜ Pending | `15_forecast_comparison.ipynb` |
| Inventory simulation | ⬜ Pending | `16_inventory_simulation.ipynb` |
| Inventory results | ⬜ Pending | `17_inventory_results.ipynb` |
| Sensitivity analysis | ⬜ Pending | `18_sensitivity_analysis.ipynb` |
| Statistical analysis | ⬜ Pending | `19_statistical_analysis.ipynb` |
| Cross-dataset robustness | ⬜ Pending | `20_cross_dataset_robustness.ipynb` |
| Final research findings | ⬜ Pending | `21_final_research_findings.ipynb` |

**Legend:** ✅ Complete · 🔄 In progress · ⬜ Not started · ⏸ Blocked
"""))

# ── Key decisions so far ─────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## Key decisions so far

| Date | Decision | Status |
|------|----------|--------|
| 2026-08-22 | Research question, model ladder, datasets, neutrality | Confirmed |
| 2026-08-22 | Conceptual freeze (proposal v0.1) | Confirmed |
| 2026-08-22 | Operational freeze v1.0 (h=28, n=50, L=7, α=95%, costs) | **Reversed** |
| 2026-08-27 | Clean research restart — notebook-first | Confirmed |
| 2026-08-27 | Cross-dataset comparability constraint (shared window, equal observations, evidence-driven sample size) | Confirmed |

All experimental parameters (horizon, sample size, splits, costs, policy) are **open** and
will be decided through EDA → literature → validation → feasibility → evidence, each
recorded in `00_project/decisions.md` *before* use.

For the full decision log: `00_project/decisions.md`
"""))

# ── Open questions ───────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## Unresolved questions

1. **Favorita feasibility** — with only 198 days available, can the second dataset support meaningful cross-dataset robustness analysis?
2. **Common window** — what is the optimal training window length given the dataset constraints?
3. **Series sample size** — how many series should be in the experimental sample? (Evidence-driven, not pre-fixed.)
4. **Rolling origin** — is rolling-origin evaluation computationally feasible given the dataset sizes and model complexity?
5. **Intermittent demand** — should a Croston/TSB-type model be added to the ladder given the high zero-demand share?
6. **LLM feasibility** — can a local LLM produce structured, valid numerical forecasts for this task?
"""))

# ── References ────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## References and documentation

| Document | Location | Purpose |
|----------|----------|---------|
| Research proposal (v0.1) | `01_research/research_proposal.md` | Conceptual source of truth |
| Experiment protocol (v1.0, superseded) | `docs/research/experiment-protocol.md` | Historical operational design |
| Decision log | `00_project/decisions.md` | All methodological decisions |
| Progress tracker | `00_project/research_progress.md` | Current status |
| Reset log | `RESET_LOG.md` | Record of the clean restart |
| Supporting code | `11_src/` | Config, metrics, plotting, data utilities |

---

*This notebook is the dashboard. It does not produce experimental results.*
*Updated: 2026-08-27*
"""))

nb.cells = cells
nbf.write(nb, "08_notebooks/00_research_map.ipynb")
print("Created 00_research_map.ipynb")
