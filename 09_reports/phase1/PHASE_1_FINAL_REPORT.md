# PHASE 1 — FINAL REPORT

## Executive Summary

Phase 1 establishes the **Traditional Forecasting Baseline** for the AI Inventory Optimization research project. Eight models — Naive, Seasonal Naive, Moving Average, SES, DES/Holt, TES/Holt-Winters, ARIMA(1,1,0), SARIMA(1,1,0)(0,1,1,7), and Global LSTM — are evaluated on two retail demand datasets under identical experimental conditions.

**Key finding:** On sparse intermittent M5 demand, the Global LSTM achieves the lowest forecast error (MAE 0.99) and lowest total inventory cost ($153 per series). On dense Store Item demand, the simpler Moving Average achieves the lowest inventory cost ($2,084 per series) despite having higher forecast error than LSTM — demonstrating that **forecast accuracy does not automatically translate to better inventory decisions**.

---

## 1. Research Objective

> "How does the effectiveness of AI-based inventory optimization change from traditional forecasting models to large language model-based approaches?"

Phase 1 answers the first half: how do traditional statistical and neural models compare, and does forecast accuracy translate into inventory outcomes?

---

## 2. Datasets

| Property | M5 | Store Item Demand |
|---|---|---|
| Source | Kaggle M5 Forecasting Accuracy | Kaggle Store Item Demand Forecasting |
| Selected series | 500 (stratified by archetype/department) | 500 (all 50 items × 10 stores) |
| Common window | 2013-01-01 → 2016-05-22 (1,238 days) | 2013-01-01 → 2016-05-22 (1,238 days) |
| Training | 2013-01-01 → 2015-10-31 (1,005 days) | Same |
| Validation | 2015-11-01 → 2016-02-28 (120 days) | Same |
| Test | 2016-03-01 → 2016-05-22 (83 days) | Same |
| Demand structure | Sparse/intermittent (68% zeros) | Dense/smooth (~0% zeros) |

---

## 3. Models Evaluated

| # | Model | Family | Key Characteristic |
|---|---|---|---|
| 1 | Naive | Baseline | Last observed value repeated |
| 2 | Seasonal Naive | Baseline | Last weekly cycle repeated (m=7) |
| 3 | Moving Average (W=14/7) | Baseline | Average of recent observations |
| 4 | SES (α=0.1) | Smoothing | Exponential level tracking |
| 5 | DES/Holt (α=0.2, β=0.2) | Smoothing | Level + trend |
| 6 | TES/Holt-Winters (α=0.3, β=0.3, γ=0.3) | Smoothing | Level + trend + weekly seasonality |
| 7 | ARIMA(1,1,0) | Statistical | Differenced AR(1) |
| 8 | SARIMA(1,1,0)(0,1,1,7) | Statistical | Seasonal MA on 100-series subset |
| 9 | Global LSTM | Neural | Pooled 500-series, direct 28-day, L=28, hidden=32 |

All models evaluated under rolling-origin protocol: 8 weekly origins, 28-day horizon, 112,000 forecast points per dataset.

---

## 4. Forecasting Results

### M5 (500 series, sparse/intermittent)

| Model | MAE | RMSE | WAPE | Bias |
|---|---|---|---|---|
| LSTM | 0.992 | 1.960 | 0.775 | +0.076 |
| SES | 0.998 | 2.003 | 0.780 | +0.017 |
| Moving Average | 1.000 | 1.304 | 1.310 | +0.040 |
| ARIMA | 1.132 | 2.317 | 0.885 | — |
| Naive | 1.184 | 1.598 | 1.434 | — |
| Seasonal Naive | 1.187 | 1.674 | 1.454 | +0.034 |
| TES | 1.922 | 4.394 | 1.502 | — |
| DES | 1.514 | 3.434 | 1.183 | — |

### Store Item Demand (500 series, dense/smooth)

| Model | MAE | RMSE | WAPE | Bias |
|---|---|---|---|---|
| LSTM | 7.884 | — | 0.138 | — |
| SARIMA | 8.306 | 10.914 | 0.153 | — |
| Seasonal Naive | 9.451 | 11.642 | 0.182 | — |
| Moving Average | 9.708 | 12.075 | 0.180 | — |
| SES | 9.922 | 13.412 | 0.173 | — |
| ARIMA | 11.900 | 15.981 | 0.208 | — |
| DES | 13.631 | 18.443 | 0.238 | — |
| Naive | 16.291 | 18.947 | 0.293 | — |
| TES | 16.868 | 23.388 | 0.295 | — |

---

## 5. Inventory Optimization Methodology

### Policy
Daily-review order-up-to (R, S) with lost sales.

### Parameters
| Parameter | Value | Unit |
|---|---|---|
| Lead time | 7 | days |
| Target service level | 95% (z = 1.645) | — |
| Holding cost | 1.0 | per unit per day |
| Stockout cost (lost sale) | 5.0 | per unit |
| Review period | Daily | — |

### Formulas

- **Safety stock:** SS = z × σ_error × √L
- **Order-up-to level:** S = Σ(forecast over lead time) + SS
- **Reorder quantity:** Q = max(0, S - inventory position)
- **Service level:** 1 - (stockout days / total days)
- **Total cost:** Holding cost + Stockout cost

---

## 6. Inventory Results

### M5

| Model | Total Cost | Holding | Stockout | Service Level | Avg Inventory |
|---|---|---|---|---|---|
| LSTM | **153.2** | 130.0 | 23.1 | 92.8% | 4.6 |
| Moving Average | 158.8 | 136.3 | 22.5 | 93.0% | 4.9 |
| SES | 159.3 | 138.3 | 21.0 | 93.6% | 4.9 |
| Seasonal Naive | 192.6 | 170.7 | 21.8 | 93.8% | 6.1 |
| Naive | 164.9 | 141.4 | 23.5 | 93.2% | 5.0 |
| DES | 221.5 | 200.0 | 21.5 | 93.8% | 7.1 |
| ARIMA | 258.7 | 216.3 | 42.4 | 91.2% | 7.7 |
| TES | 280.2 | 252.8 | 27.4 | 92.9% | 9.0 |

### Store Item Demand

| Model | Total Cost | Holding | Stockout | Service Level | Avg Inventory |
|---|---|---|---|---|---|
| Moving Average | **2,084** | 1,276 | 808 | 61.7% | 45.6 |
| SES | 2,114 | 1,156 | 958 | 56.1% | 41.3 |
| Seasonal Naive | 2,128 | 1,281 | 847 | 62.0% | 45.8 |
| SARIMA | 2,175 | 1,233 | 942 | 59.1% | 44.0 |
| LSTM | 2,246 | 1,159 | 1,087 | 53.0% | 41.4 |
| ARIMA | 2,321 | 1,076 | 1,244 | 52.4% | 38.4 |
| Naive | 2,700 | 795 | 1,906 | 43.2% | 28.4 |
| DES | 2,780 | 2,130 | 650 | 73.5% | 76.1 |
| TES | 3,420 | 2,486 | 934 | 69.1% | 88.8 |

---

## 7. Key Findings

### Finding 1: Forecast accuracy ≠ Inventory optimality

On Store Item Demand, LSTM has the lowest forecast error (MAE 7.88) but Moving Average achieves the lowest inventory cost ($2,084). This is because the inventory policy's safety stock and order-up-to calculations depend on forecast *distribution*, not just mean error. LSTM's global pooling averages out extreme values, creating a flatter forecast profile that underperforms the simpler MA's conservative averaging in the inventory simulation.

### Finding 2: Model complexity helps on sparse demand but hurts on dense demand

- **M5 (sparse):** LSTM and SES perform best on both forecast and inventory metrics. Nonlinear learning and smoothing help navigate intermittent bursts.
- **Store Item (dense):** Simple models (MA, SNaive) perform best on inventory. Complex models (TES, DES) over-order because they overfit weekly patterns.

### Finding 3: Service level is inversely correlated with inventory cost on Store Item

The highest service level (DES 73.5%) corresponds to the second-highest cost. Higher service levels require more safety stock, which increases holding cost. The trade-off between service level and cost is explicit.

### Finding 4: M5 intermittency remains the hardest challenge

All models achieve relatively low error on M5 in absolute terms, but high WAPE (78–150%) because the demand is very small (mean 0.5–1.5 units/day). The intermittent structure means even "small" errors are proportionally large. The inventory simulation shows this translates to meaningful stockout risk.

---

## 8. Limitations

1. **Single inventory policy:** Only one (R,S) policy tested. Different policies (e.g., (s,Q) or base-stock) may change the ranking.
2. **Univariate only:** No price, promotion, or calendar covariates used.
3. **Global LSTM scope:** One pooled model per dataset/origin, not per-series. Series-specific LSTMs would be more expensive but potentially better on M5.
4. **SARIMA on subset only:** Due to compute constraints, SARIMA was evaluated on 100 Store Item series, not 500. Full-scale SARIMA deferred.
5. **No lost-sales adjustment:** True lost-sales censored demand is not modelled — actual demand is always observed.
6. **Single test window:** 83-day test period with 8 overlapping origins provides robust but not exhaustive evidence.

---

## 9. Reproducibility

- **Random seed:** 42 (Python, NumPy, PyTorch)
- **Dataset versions:** M5 evaluation set, Kaggle Store Item Demand train.csv
- **Dependencies:** pandas, numpy, scipy 1.14.1, statsmodels 0.14.6, torch 2.13.0+cpu, seaborn, matplotlib
- **Git tag:** `phase-1-complete` (commit `3aae494`)
- **All forecasts:** saved in CSV long format under `06_results/*/all_forecasts.csv`
- **All metrics:** saved in `06_results/*/metrics_by_model.csv`

---

## 10. Phase 1 Conclusion

Phase 1 establishes a rigorous, reproducible traditional forecasting baseline. The key insight is that **model ranking changes between forecast error and inventory cost** — the "best" forecast is not always the "best" inventory decision. This finding is critical for the research question: any Phase 2 (SLM/LLM) model must be evaluated on inventory outcomes, not just forecast accuracy.

**Phase 1 complete. All forecasts, metrics, inventory simulations, figures, and documentation produced.**

---

## 11. Phase 2 Research Direction

- **SLM:** Small language model approaches for demand forecasting
- **LLM:** Large language model approaches using natural-language reasoning
- **Fine-tuning:** Domain-adapted models
- **Cross-paradigm comparison:** Traditional vs SLM vs LLM vs Fine-tuned under identical evaluation framework
