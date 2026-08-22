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
**Decision:** Walmart M5 (primary) + Grocery/Corporación Favorita (secondary robustness environment).
**Why:** M5 is an established retail benchmark; Favorita provides a second retail demand environment for robustness.
**Alternatives considered:** single-dataset study (rejected — weaker cross-dataset robustness); additional datasets (postponed).
**Evidence:** Planning pack — data.md, README.md.
**Date:** 2026-08-22
**Impact:** 02_data structure; dataset documentation; cross-dataset analysis.
**Status:** Confirmed

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
- exact Favorita series / subset size
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