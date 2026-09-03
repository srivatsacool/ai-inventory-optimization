# LLM Experiment Protocol — Fair Comparison Design

**Version 1.0 — 2026-09-03 — Research Hardening pre-report**
**Seed 42, same frozen design as other models: M5 500 / Store 500, window 2013-01-01→2016-05-22, H28, 8 origins**

## 1. Conditions (within-subject)

| Condition | Information allowed | Rationale |
|---|---|---|
| **A. Controlled (primary, fair)** | For each forecast window: univariate history only — the same 28-day lookback + past dates that LSTM/ARIMA see. Plus the forecast horizon dates (so model knows "you are forecasting 2016-03-01→2016-03-28"). No calendar features (snap, event, price), no cross-series info, no future. Prompt is a numeric time series + "predict next 28 values". | Isolates architecture advantage. Any win is from LLM reasoning, not extra data. This is the condition reported in the main comparison tables. |
| **B. Context-enhanced (secondary, exploratory)** | Same as A plus *known* calendar context that is legitimately known before the origin: weekday, month, and for M5: snap_CA/TX/WI flags and event_name/type (if non-null for dates in lookback+horizon), both historically determinable. No actual future demand, no price (price is not known ahead). | Tests whether LLM can exploit known seasonality drivers that univariate models ignore. Reported separately as "LLM-context" and never averaged with A. |

*Prohibited in both:* actual future y, any series' future, cross-series future, or any data with timestamp ≥ origin. The prompt builder asserts `max(history_date) < origin`.

## 2. Prompt template (controlled)

```
You are a retail demand forecaster.
History (28 days, daily demand, univariate):
2016-02-02: 0
2016-02-03: 2
...
2016-02-29: 1   <- last observed before origin 2016-03-01

Forecast horizon: 2016-03-01 to 2016-03-28 (28 days)
Task: Predict the next 28 daily values as a JSON array of 28 non-negative numbers (integers allowed, decimals allowed for Store Item if needed). No explanation.

History: [0,2,...,1]
```

Context-enhanced adds after history:
```
Context for lookback: snap_CA: [0,0,1,...], event: [null, null, "…", ...]
Context for horizon: weekday: [Tue, Wed, ...], snap: [...]
```

## 3. Model / version / settings

- Model: to be locked at execution (e.g., `gpt-4o-mini-2024-07-18` or `gemini-2.0-flash`). Record exact `model` string and `system_fingerprint` per call.
- Temperature 0 (deterministic), top_p 1, seed 42 where API supports, max_tokens ≈ 200 (28 numbers).
- Batch via API, not chat UI; one call per series×origin (500*8=4000 per dataset per condition = 8000 calls total). With rate limits, expect ~2–4 h per condition.

## 4. Recording (per call)

A single `06_results/llm/llm_log.csv` row per series×origin:
`dataset, series_id, origin, origin_date, model, prompt_tokens, completion_tokens, latency_ms, forecast_json, parse_ok, fallback, error, cost_usd`

Plus
- `06_results/llm/all_forecasts.csv` long format same schema as other models (dataset, series_id, origin, forecast_date, actual, forecast, model)
- `06_results/llm/invalid_forecasts.csv` — any non-JSON, wrong length, negative, or NaN, with handling: clamp to 0, pad with Naive last value, and flag `parse_ok=False`.

## 5. Leakage guardrails

- Builder function `build_llm_window(history, horizon_dates, context)` takes `origin` and asserts all dates < origin for history/context-horizon known flags.
- No scaling on LLM side that uses future; LLM sees raw integers (M5) or floats (Store).
- Same expanding-window rolling evaluation; LLM never sees test actuals.
- Validation period not used for LLM tuning; temperature not tuned on test.

## 6. Failures & cost

- On API error / timeout / invalid JSON after 1 retry: fallback to Naive (last observed) for that window, logged as `fallback=naive`.
- On rate-limit: exponential backoff, logged.
- Cost estimated: 8000 calls * ( ~400 prompt + 50 completion) ≈ 3.6M tokens → at 0.15/0.60 per 1k, ~$0.60–$2.20 per condition (to be recorded actual).

## 7. Metrics & reporting

Same as other models: MAE, RMSE, WAPE, sMAPE, MASE (with train denominator seasonal 7 for M5, 1 for Store) — computed by shared `metrics.py`. LLM appears in same `metrics_with_history.csv` but condition A is the primary row `LLM-controlled`; condition B is `LLM-context` in a separate table/appendix, never merged into primary ranking.

## 8. What would make LLM unfair?

If B were presented as beating MA "because LLM is better" without noting the extra calendar info. The protocol prevents this by separating A and B and requiring the claim "LLM-controlled significantly outperforms X (Wilcoxon p Holm, dz)" to be backed by Condition A data.
