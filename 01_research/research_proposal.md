# Research Proposal — Conceptual Freeze (v0.1)

> **Status:** Conceptual freeze — research design locked at the conceptual level; all experimental parameters remain open and are governed by the decision framework defined in Section 7.
> **Date:** 2026-08-22
> **Source of truth:** The project planning pack (`AI_Inventory_Optimization_Project_Pack/`). This document is the proposal-level synthesis; it does not replace or alter the planning pack. Decisions recorded later in `00_project/decisions.md`.
> **Documentation principle:** This proposal supports the research communication layer (website). It is not the experiment itself.

---

## 1. Title and research question (locked)

**Title**
From Traditional Forecasting to Large Language Models: Evaluating AI-Based Inventory Optimization

**Central research question**
How does the effectiveness of AI-based inventory optimization change from traditional forecasting models to large language model–based approaches?

**Research position**
The study must not assume that the LLM wins. A simple method, a statistical model, an LSTM, or an LLM can be the final best approach depending on evidence.

---

## 2. What the study is (locked)

A controlled, reproducible experimental framework in which:

1. Multiple forecasting approaches receive comparable demand histories,
2. generate forecasts for the same evaluation periods,
3. and feed those forecasts into a **common inventory simulation**,
4. so that forecast accuracy, inventory outcomes, and practicality can be compared fairly.

**Evaluation philosophy**
Forecast accuracy + inventory outcomes + practicality.

**Core research principle**
Do not assume that the most sophisticated model is the best model.

---

## 3. Model progression (locked)

```text
MA
↓
SES
↓
DES
↓
TES
↓
ARIMA
↓
SARIMA
↓
LSTM
↓
LLM
```

The ladder moves from traditional smoothing methods → statistical ARIMA/SARIMA → a neural network → an LLM-based approach. Complexity increases along the ladder; whether value increases with complexity is the empirical question.

---

## 4. Datasets (locked at dataset level)

| Dataset | Role | What it allows the study to examine |
| --- | --- | --- |
| Walmart M5 | Primary benchmark environment | Hierarchical retail unit-sales; multiple products/stores; seasonality; intermittent/variable demand; established benchmark literature |
| Grocery / Corporación Favorita | Secondary environment (robustness) | Grocery retail demand; multiple stores/items; promotions; contextual variables |

The second dataset tests robustness across different retail demand environments — it is **not** added merely to increase data volume.

**Important distinction**
Sales/demand observations are not the same as actual inventory records. M5/Favorita do not provide a complete real-world inventory ledger (on-hand stock, supplier lead times, holding costs, stockout costs). Inventory results will therefore be **simulated under explicit, documented assumptions** — never presented as a reconstruction of the retailers' actual inventory systems.

---

## 5. Evaluation philosophy (locked)

Three evaluation dimensions, kept conceptually distinct:

```text
             MODEL
               │
       ┌───────┼────────┐
       ↓       ↓        ↓
 Forecast   Inventory  Practicality
 Accuracy   Outcomes   & Complexity
```

**Forecast accuracy** — MAE, MSE, RMSE, sMAPE, MASE/RMSSE where justified (final metric set confirmed later).
**Inventory outcomes** — total inventory cost, holding cost, stockout cost, stockout frequency/rate, service level, average inventory, order frequency.
**Practicality** — runtime, computational requirements, complexity, interpretability, reproducibility.

A model may be strong in one dimension and weak in another. The research distinguishes all three.

---

## 6. Master research framework (locked)

```text
                    RETAIL DEMAND
                         │
                         ▼
                  DATA EXPLORATION
                         │
                         ▼
              ┌─────────────────────┐
              │ FORECASTING MODELS  │
              └─────────────────────┘
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
 Traditional        Statistical         AI/LLM
       │                 │                 │
 MA → SES → DES     ARIMA → SARIMA       LSTM → LLM
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ▼
                  FORECAST QUALITY
                         │
                         ▼
               INVENTORY SIMULATION
                         │
                         ▼
        ┌────────────────────────────────┐
        │ Cost │ Stockouts │ Service     │
        │ Level│ Inventory │ Orders      │
        └────────────────────────────────┘
                         │
                         ▼
                    ROBUSTNESS
                         │
                         ▼
                 FINAL COMPARISON
                         │
                         ▼
        "Does more advanced AI actually
             improve inventory decisions?"
```

**Temporal integrity (locked principle):** no future information may enter training, preprocessing, LLM prompts, or inventory decisions. Time-based validation only — no random train/test splits for the main experiment. Rolling-origin evaluation is a candidate methodology, pending computational feasibility.

**Fair comparison (locked principle):** keep constant where possible — data history, forecast horizon, evaluation period, inventory policy, inventory assumptions, evaluation metrics. Forecasting models should primarily differ in the forecasts they provide; downstream inventory decision rules remain standardized wherever practical.

---

## 7. Open experimental parameters and decision framework

> **Status:** The following parameters are **intentionally not fixed**. They are controlled research decisions that will be finalized through EDA → literature → validation → feasibility → experimental evidence. When each is decided, the decision is recorded in `00_project/decisions.md` using the project's decision template (Decision / Why / Alternatives considered / Evidence / Date / Impact / Status).

### 7.1 Series / SKU selection
**What it means:** the datasets contain many product/store series; which demand series will actually be forecast must be decided.
**Guiding rule:** do not arbitrarily select products. Perform exploratory analysis first; identify representative series on demand volume, demand variability, seasonality, intermittency, historical length, missing values, and business relevance; then select a manageable experimental sample.
**Proposal wording:** *"Product series will be selected after exploratory data analysis using predefined representativeness criteria. Selection will aim to capture different demand characteristics rather than optimizing for any particular forecasting model."*
**Why it matters:** arbitrary or model-friendly selection could accidentally favor one model class.

### 7.2 Forecasting horizon
**What it means:** how far ahead each model must forecast (candidate: 1 / 7 / 14 / 28 days).
**Guiding rule:** the horizon is linked to the inventory decision problem, not chosen for forecasting convenience. If the inventory policy assumes a lead time of L days, forecasts must support demand estimation over that decision horizon. Exact horizon determined after the datasets and inventory setup are understood.

### 7.3 Train / validation / test periods
**Guiding rule:** time-based splitting — historical demand → training → validation/model selection → final test. No random shuffling. The model must only see information that would have been available at that point in time. Exact boundaries decided after EDA.

### 7.4 Rolling evaluation
**What it means:** repeated train → forecast → advance → retrain cycles instead of a single evaluation point.
**Status:** candidate methodology, not mandatory until computational feasibility is known. Purpose: test consistency of model performance across different demand periods.

### 7.5 Seasonality
**Guiding rule:** seasonality is identified through EDA, not assumed. Candidate patterns: daily, weekly, monthly, yearly (weekly may be especially relevant for retail). Affects TES, SARIMA, LSTM input design, LLM prompt context, and the inventory forecasting horizon.

### 7.6 LSTM architecture and hyperparameters
**Guiding rule:** no premature specification (e.g. "two layers with 64 neurons"). Design path: EDA → baseline performance → define reasonable architecture range → validation → select configuration → final test.
**Key principle:** *LSTM complexity must earn its place through evidence.*
Open dimensions: number of layers, hidden units, lookback window (based on temporal structure), dropout (validation/tuning), batch size, epochs (early stopping/validation), optimizer (standard candidate), learning rate (tuned if required).

### 7.7 LLM / Ollama model
**Position:** the experiment does *not* claim an LLM is inherently a time-series forecasting model. It asks: *can a general-purpose, locally hosted language model be used as a practical demand forecasting mechanism when provided with structured historical demand information?*
**Selection criteria:** local hardware, context length, numerical reasoning capability, inference speed, reproducibility, output consistency. The selected model and version must be logged.

### 7.8 LLM prompt design
**Status:** a controlled experimental artifact, versioned and fixed during a comparison.
**Conceptual structure:** SYSTEM INSTRUCTIONS → ROLE → FORECASTING TASK → HISTORICAL DEMAND → TIME INFORMATION → FORECAST HORIZON → OUTPUT FORMAT. The LLM returns structured numerical output, not prose (conceptual schema: `{"forecast": [x1, x2, ...]}`).
**Critical rule:** the prompt must never expose future demand — data leakage control. Invalid outputs are logged, not silently repaired.

### 7.9 Inventory policy
**Guiding rule (locked principle):** a common inventory policy is applied across all models so comparisons are interpretable — not Model A + Policy A vs Model B + Policy B.
**Proposal wording:** *"Forecasting models should primarily differ in the forecasts they provide, while downstream inventory decision rules should remain standardized wherever practical."*
**Candidate components:** lead time, safety stock, reorder point, order quantity, review frequency, initial inventory, holding cost, stockout cost, service target. Exact values remain open until justified.

### 7.10 Lead time
**Guiding rule:** determined from dataset characteristics, literature, realistic retail assumptions, and sensitivity analysis. The study will not pretend M5/Favorita provide complete real-world supplier lead-time information when they do not.

### 7.11 Holding cost
**Guiding rule:** product-specific costs are unlikely to be available; the study may use normalized or assumed costs, explicitly documented. May represent storage, capital tied up, handling, and deterioration/obsolescence where relevant.

### 7.12 Stockout cost
**Guiding rule:** actual commercial stockout costs are unlikely to come from the public datasets. *"The inventory simulation will use transparent assumed/normalized cost parameters rather than claiming to reconstruct the actual retailer's cost structure."*

### 7.13 Service level
**What it means:** how often the system satisfies demand without stocking out (conceptually: satisfied demand / total demand). A formal definition is adopted once the inventory simulation design is finalized.

### 7.14 Additional metrics
**Forecasting:** MAE, RMSE, MSE, sMAPE, MASE/RMSSE where justified.
**Inventory:** total inventory cost, holding cost, stockout cost, stockout frequency/rate, service level, average inventory, order frequency.
**Practicality:** runtime, computational requirements, model complexity, interpretability, reproducibility.
Final metric set confirmed based on experimental structure and dataset characteristics — nothing is pre-locked.

### 7.15 Statistical testing
**Guiding rule (locked principle):** tests are selected after the experimental structure is finalized (number of series, evaluation windows, experimental unit, metric distributions), rather than imposed beforehand. The research question is: *are the differences between approaches large and consistent enough to matter?* Candidate strategies (Friedman, Nemenyi, Wilcoxon, ANOVA, FDR procedures) remain uncommitted.

### 7.16 Sensitivity analysis
**What it means:** does the winning model change when assumptions change? Vary major assumptions (lead time, holding cost, stockout cost: low → medium → high; also service target where relevant).
**Interpretation:** a model that wins under every reasonable assumption is stronger evidence; a frequently changing winner is also an important research finding.

---

## 8. How open parameters become decisions

```text
EDA → Literature → Validation → Feasibility → Experimental evidence
                            │
                            ▼
                 Recorded in 00_project/decisions.md
                 (Decision / Why / Alternatives / Evidence / Date / Impact / Status)
```

Every important methodological decision is recorded. Previous decisions are never silently replaced — reversals are recorded as `Status: Reversed` with a new entry.

---

## 9. Research questions the website communicates

| # | Question |
| --- | --- |
| RQ1 | How do traditional, statistical, neural-network, and LLM-based approaches differ in demand forecasting performance? |
| RQ2 | How do forecasting differences translate into inventory-management outcomes? |
| RQ3 | Does increasing model sophistication consistently improve inventory performance? |
| RQ4 | Are model-performance patterns consistent across different retail demand environments? |
| RQ5 | What trade-offs exist between accuracy, inventory performance, computational requirements, and complexity? |

---

## 10. Expected contribution (categories, no fabricated conclusions)

- **Academic:** comparison across forecasting generations (smoothing → statistical → neural → LLM).
- **Methodological:** connecting forecast evaluation with inventory outcomes in one framework.
- **Practical:** understanding whether additional model complexity produces meaningful operational benefits.
- **AI perspective:** evaluating whether LLM-based forecasting adds value relative to established forecasting approaches.

---

## 11. Non-goals (locked scope boundary)

Excluded from the initial study: full supply-chain optimization, multi-echelon optimization, real-time ERP integration, supplier negotiation, routing, dynamic pricing, reinforcement-learning inventory control, and actual Walmart/Favorita inventory reconstruction.

---

## 12. Research principles (locked)

1. **Neutrality** — never design experiments to prove LLMs are better.
2. **Question-first scope** — every model/metric/dataset/experiment must justify how it helps answer the central research question.
3. **Forecasting is not the final objective** — inventory outcomes are the business-level endpoint.
4. **Fair comparison** — comparable data, horizons, test periods, policies, and metrics.
5. **Time integrity** — no future information in training, preprocessing, prompting, or decisions.
6. **Reproducibility** — versions, assumptions, configurations, prompts, seeds, and outputs recorded.
7. **Explicit assumptions** — simulation assumptions documented and sensitivity-tested where material.
8. **No fake completeness** — unfinished research marked unfinished; never filled with invented values.
9. **Complexity must earn its place** — no models added merely because they are fashionable.
10. **Results can change the plan** — EDA/experiment findings revise the plan through the decision log.
11. **Literature claims verified** — the initial bibliography is a starting point, verified before use as formal evidence.
12. **Website follows research** — the website communicates the research; it does not drive methodological decisions.