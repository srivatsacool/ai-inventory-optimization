# PHASE 1 — METHODOLOGY SUMMARY

## Datasets

| Dataset | Source | Series | Common Window | Test Period |
|---|---|---|---|---|
| M5 | Kaggle M5 Forecasting Accuracy | 500 (stratified) | 2013-01-01 → 2016-05-22 | 2016-03-01 → 2016-05-22 |
| Store Item Demand | Kaggle Store Item Demand Forecasting | 500 (all) | 2013-01-01 → 2016-05-22 | 2016-03-01 → 2016-05-22 |

## Preprocessing

- **M5:** Evaluation set used (d_1 to d_1941). Calendar mapped to dates. 500 series selected via stratified sampling across archetypes (Intermittent, Highly Intermittent, Variable, Moderate, Smooth) and departments.
- **Store Item Demand:** train.csv filtered to common window. Pivoted to wide format (dates × series). Series ID format: store_X_item_Y.
- **No imputation, no feature engineering, no covariates.** Univariate demand only.

## Experimental Design

- **Protocol:** 8 weekly rolling origins, 28-day forecast horizon
- **Origins:** 2016-03-01, 03-08, 03-15, 03-22, 03-29, 04-05, 04-12, 04-19
- **Leakage prevention:** Each model sees only data strictly before its origin date
- **Metrics:** MAE, RMSE, sMAPE, WAPE
- **Seed:** 42

## Model Configurations

| Model | Configuration |
|---|---|
| Naive | Last value repeated 28 times |
| Seasonal Naive | Last 7 values repeated 4 times |
| Moving Average | W=14 (M5), W=7 (Store Item) — selected on validation only |
| SES | α=0.1 (global per dataset) |
| DES/Holt | α=0.2, β=0.2 |
| TES/Holt-Winters | α=0.3, β=0.3, γ=0.3, m=7, additive |
| ARIMA | (1,1,0), statsmodels |
| SARIMA | (1,1,0)(0,1,1,7), 100-series subset (Store Item only) |
| Global LSTM | 1-layer, hidden=32, L=28, H=28, batch=256, Adam lr=0.01, max 5 epochs, early stopping patience 2, direct 28-day output, per-series StandardScaler on history only |

## Inventory Policy

- **Type:** Daily-review order-up-to (R, S)
- **Lead time:** L = 7 days
- **Service level target:** 95% (z = 1.645)
- **Holding cost:** h = 1.0 per unit per day
- **Stockout cost:** p = 5.0 per unit (lost sale)
- **Safety stock:** SS = z × σ_error × √L
- **Order-up-to level:** S = Σ(forecast over L days) + SS

## Cost Parameters

| Parameter | Value | Unit |
|---|---|---|
| Holding cost | 1.0 | per unit per day |
| Stockout cost | 5.0 | per unit (lost sale) |
| Lead time | 7 | days |
| Service level | 95% | — |

## Evaluation Protocol

1. For each model × dataset × origin × series:
   - Compute 28-day forecast
   - Compute forecast error against actual
   - Run daily inventory simulation (83 test days)
   - Record: total cost, service level, average inventory, stockout frequency

2. Aggregate per model × dataset: mean across all series and origins

3. Compare across models on both forecast metrics and inventory outcomes
