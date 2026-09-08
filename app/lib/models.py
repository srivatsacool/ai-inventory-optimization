"""Model registry for the Interactive Experiment sandbox.

The forecasting functions in this module are lifted VERBATIM from the frozen
research pipeline (11_src/_make_nb05/06/06c/07/08.py -> 08_notebooks/*) so the
sandbox runs the exact same math as the benchmark. Only two things were added:

1. per-series wrappers for the baselines (row-wise equivalents of the research
   `baseline_forecasts` matrix code — same arithmetic);
2. a per-series variant of the research *global* LSTM (same architecture,
   scaling, lookback, optimizer; trained on one series instead of pooled 500).
   This is clearly labelled in outputs as a sandbox variant.
"""
from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Research-frozen hyperparameters (06_results/*/…selection.json + config.json)
# ---------------------------------------------------------------------------
HORIZON = 28
SEASON = 7
MA_WINDOW = {"m5": 14, "store_item_demand": 7}  # moving_average_window_selection.json
SES_ALPHA = 0.1          # exponential_smoothing/model_parameters.json
DES_ALPHA, DES_BETA = 0.2, 0.2
TES_ALPHA, TES_BETA, TES_GAMMA = 0.3, 0.3, 0.3
CROSTON_ALPHA = 0.1      # croston/validation_selection.json
SBA_ALPHA = 0.5
TSB_ALPHA, TSB_BETA = 0.1, 0.3
ARIMA_ORDER = (1, 1, 0)              # arima/run_log_full500.json
SARIMA_ORDER = (1, 1, 0)
SARIMA_SEASONAL = (0, 1, 1, 7)
LSTM_LOOKBACK, LSTM_HIDDEN, LSTM_EPOCHS, LSTM_PATIENCE = 28, 32, 5, 2  # nb08

# ---------------------------------------------------------------------------
# torch availability probe (LSTM needs a NumPy-2 compatible torch build)
# ---------------------------------------------------------------------------
try:
    import warnings as _warnings

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        import torch
        import torch.nn as nn

    (torch.from_numpy(np.zeros(1, dtype=np.float32)) + 1.0).item()  # ABI probe (fails on torch<2.4 + numpy>=2); must be 1-element for .item()
    TORCH_AVAILABLE = True
except Exception:  # pragma: no cover
    TORCH_AVAILABLE = False


# ---------------------------------------------------------------------------
# Level 1 — baselines (verbatim arithmetic from _make_nb05.py)
# ---------------------------------------------------------------------------
def naive_forecast(history, horizon=HORIZON):
    history = np.asarray(history, dtype=float)
    return np.repeat(history[-1], horizon)


def seasonal_naive_forecast(history, horizon=HORIZON):
    history = np.asarray(history, dtype=float)
    return np.tile(history[-7:], (1, int(np.ceil(horizon / 7))))[:, :horizon].ravel()


def moving_average_forecast(history, horizon=HORIZON, window=14):
    history = np.asarray(history, dtype=float)
    return np.repeat(history[-window:].mean(), horizon)


def _ma_forecast(history, horizon=HORIZON, dataset=None, **_):
    return moving_average_forecast(history, horizon, MA_WINDOW.get(dataset, 14))


# ---------------------------------------------------------------------------
# Level 2 — exponential smoothing (verbatim from _make_nb06.py)
# ---------------------------------------------------------------------------
def ses_forecast(history, horizon, alpha):
    history = np.asarray(history, dtype=float)
    if len(history) == 0:
        return np.zeros(horizon)
    level = history[0]
    for value in history[1:]:
        level = alpha * value + (1 - alpha) * level
    return np.repeat(max(level, 0.0), horizon)


def holt_forecast(history, horizon, alpha, beta):
    history = np.asarray(history, dtype=float)
    if len(history) == 0:
        return np.zeros(horizon)
    if len(history) == 1:
        return np.repeat(max(history[0], 0.0), horizon)
    level = history[0]
    trend = history[1] - history[0]
    for value in history[1:]:
        old_level = level
        level = alpha * value + (1 - alpha) * (level + trend)
        trend = beta * (level - old_level) + (1 - beta) * trend
    return np.maximum(level + trend * np.arange(1, horizon + 1), 0.0)


def holt_winters_forecast(history, horizon, alpha, beta, gamma, period=7):
    history = np.asarray(history, dtype=float)
    if len(history) == 0:
        return np.zeros(horizon)
    if len(history) < 2 * period:
        # A short-history fallback is explicit and deterministic.
        return holt_forecast(history, horizon, alpha, beta)
    level = float(np.mean(history[:period]))
    trend = float((np.mean(history[period:2*period]) - level) / period)
    seasonals = list((history[:period] - level).astype(float))
    for t in range(period, len(history)):
        old_level = level
        old_season = seasonals[t - period]
        level = alpha * (history[t] - old_season) + (1 - alpha) * (level + trend)
        trend = beta * (level - old_level) + (1 - beta) * trend
        new_season = gamma * (history[t] - level) + (1 - gamma) * old_season
        seasonals.append(float(new_season))
    future = []
    start = len(seasonals) - period
    for j in range(horizon):
        seasonal_value = seasonals[start + (j % period)]
        future.append(level + (j + 1) * trend + seasonal_value)
    return np.maximum(np.asarray(future), 0.0)


# ---------------------------------------------------------------------------
# Level 3 — ARIMA / SARIMA (verbatim from _make_nb07.py)
# ---------------------------------------------------------------------------
def arima_forecast(history, horizon=HORIZON, order=ARIMA_ORDER, conv=None):
    from statsmodels.tsa.arima.model import ARIMA

    if len(history) < 10 or np.all(history == 0) or (history == 0).mean() > 0.85:
        if conv is not None:
            conv.update(status="fallback_skip", reason="precheck: short history / all-zero / >85% zeros")
        return np.repeat(history[-1] if len(history) > 0 else 0, horizon)
    try:
        m = ARIMA(history, order=order).fit()
        fc = m.get_forecast(steps=horizon).predicted_mean
        fc = np.asarray(fc, dtype=float)
        fc = np.where(np.isfinite(fc), fc, history[-1])
        fc = np.maximum(fc, 0)  # demand non-negative
        if conv is not None:
            conv.update(status="fit_ok", reason="")
        return fc
    except Exception as e:
        if conv is not None:
            conv.update(status="fallback_fail", reason=f"{type(e).__name__}: {e}")
        return np.repeat(float(history[-1]), horizon)


def sarima_forecast(history, horizon=HORIZON, order=SARIMA_ORDER, sorder=SARIMA_SEASONAL, conv=None):
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    if len(history) < 30 or np.all(history == 0):
        if conv is not None:
            conv.update(status="fallback_skip", reason="precheck: short history / all-zero")
        return np.repeat(history[-1] if len(history) > 0 else 0, horizon)
    try:
        m = SARIMAX(history, order=order, seasonal_order=sorder,
                    enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
        fc = m.get_forecast(steps=horizon).predicted_mean
        fc = np.asarray(fc, dtype=float)
        fc = np.where(np.isfinite(fc), fc, history[-1])
        fc = np.maximum(fc, 0)
        if conv is not None:
            conv.update(status="fit_ok", reason="")
        return fc
    except Exception as e:
        if conv is not None:
            conv.update(status="fallback_fail", reason=f"{type(e).__name__}: {e}")
        return np.repeat(float(history[-1]), horizon)


# ---------------------------------------------------------------------------
# Level 5 — Croston family (verbatim from _make_nb06c_croston.py)
# ---------------------------------------------------------------------------
def croston_forecast(history, horizon=HORIZON, alpha=0.1, variant="croston"):
    hist = np.asarray(history, dtype=float)
    nz = hist[hist > 0]
    if len(nz) == 0:
        return np.zeros(horizon)
    z_hat = nz[0]
    nz_idx = np.where(hist > 0)[0]
    if len(nz_idx) >= 2:
        p_hat = np.mean(np.diff(nz_idx)) if len(nz_idx) > 1 else 1
        p_hat = max(p_hat, 1)
    else:
        p_hat = 1
    p_prob = np.mean(hist > 0)
    if p_prob == 0:
        p_prob = 0.1
    z_prob = z_hat
    q = 0
    beta = 0.1
    if isinstance(variant, tuple):
        variant, beta = variant
    last_interval = 0
    for i, val in enumerate(hist):
        if val > 0:
            z_hat = alpha * val + (1 - alpha) * z_hat
            if variant in ("croston", "sba"):
                interval = q + 1 if q > 0 else 1
                p_hat = alpha * interval + (1 - alpha) * p_hat
            q = 0
        else:
            q += 1
        if variant == "tsb":
            d = 1 if val > 0 else 0
            p_prob = beta * d + (1 - beta) * p_prob
            if val > 0:
                z_prob = alpha * val + (1 - alpha) * z_prob
    if variant == "croston":
        fc = z_hat / max(p_hat, 1)
    elif variant == "sba":
        fc = (1 - alpha / 2) * z_hat / max(p_hat, 1)
    elif variant == "tsb":
        fc = p_prob * z_prob
    else:
        raise ValueError(variant)
    return np.full(horizon, max(fc, 0))


# ---------------------------------------------------------------------------
# Level 4 — LSTM (sandbox per-series variant of the research global LSTM,
# architecture/scaling/optimizer identical to _make_nb08.py GlobalLSTM)
# ---------------------------------------------------------------------------
def lstm_forecast(history, horizon=HORIZON, seed=42):
    history = np.asarray(history, dtype=float)
    torch.manual_seed(seed)
    L, hidden = LSTM_LOOKBACK, LSTM_HIDDEN
    if len(history) < L + horizon + 1 or history.std() < 1e-9:
        return np.repeat(max(float(history[-1]), 0.0), horizon)
    # per-series scaling fit on history only (fit_scalers_and_scale, nb08)
    mean, std = history.mean(), history.std() + 1e-6
    scaled = (history - mean) / std
    # pooled windows from the single series (make_global_windows_pooled, nb08)
    xs, ys = [], []
    for i in range(len(scaled) - L - horizon + 1):
        xs.append(scaled[i:i + L])
        ys.append(scaled[i + L:i + L + horizon])
    X = torch.tensor(np.array(xs, dtype=np.float32)).unsqueeze(-1)
    Y = torch.tensor(np.array(ys, dtype=np.float32))
    k = min(4, max(1, int(0.05 * len(xs))))  # chronological val split (nb08 hardening)
    Xtr, Ytr, Xva, Yva = X[:-k], Y[:-k], X[-k:], Y[-k:]

    class GlobalLSTM(nn.Module):
        def __init__(self, hidden=32, horizon=28):
            super().__init__()
            self.lstm = nn.LSTM(input_size=1, hidden_size=hidden, num_layers=1, batch_first=True)
            self.fc = nn.Linear(hidden, horizon)

        def forward(self, x):
            out, _ = self.lstm(x)
            return self.fc(out[:, -1, :])

    model = GlobalLSTM(hidden=hidden, horizon=horizon)
    opt = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_fn = nn.MSELoss()
    best_state, best_val, patience = None, float("inf"), 0
    for _ in range(LSTM_EPOCHS):
        model.train()
        for i in range(0, len(Xtr), 256):
            xb, yb = Xtr[i:i + 256], Ytr[i:i + 256]
            opt.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            vloss = loss_fn(model(Xva), Yva).item()
        if vloss < best_val - 1e-6:
            best_val, best_state, patience = vloss, {k: v.clone() for k, v in model.state_dict().items()}, 0
        else:
            patience += 1
            if patience >= LSTM_PATIENCE:
                break
    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        x = torch.tensor(scaled[-L:], dtype=torch.float32).view(1, L, 1)
        pred = model(x).numpy().flatten() * std + mean
    return np.maximum(pred, 0.0)


# ---------------------------------------------------------------------------
# Registry — the research model ladder
# ---------------------------------------------------------------------------
MODEL_LADDER = {
    "Naive": {"family": "baseline", "func": naive_forecast},
    "Seasonal Naive": {"family": "baseline", "func": seasonal_naive_forecast},
    "Moving Average": {"family": "baseline", "func": _ma_forecast},
    "SES": {"family": "smoothing", "func": lambda h, horizon=HORIZON: ses_forecast(h, horizon, SES_ALPHA)},
    "DES": {"family": "smoothing", "func": lambda h, horizon=HORIZON: holt_forecast(h, horizon, DES_ALPHA, DES_BETA)},
    "TES": {"family": "smoothing", "func": lambda h, horizon=HORIZON: holt_winters_forecast(h, horizon, TES_ALPHA, TES_BETA, TES_GAMMA)},
    "ARIMA": {"family": "statistical", "func": arima_forecast},
    "SARIMA": {"family": "statistical", "func": sarima_forecast},
    "LSTM": {"family": "neural", "func": lstm_forecast},
    "Croston": {"family": "intermittent", "func": lambda h, horizon=HORIZON: croston_forecast(h, horizon, CROSTON_ALPHA, "croston")},
    "SBA": {"family": "intermittent", "func": lambda h, horizon=HORIZON: croston_forecast(h, horizon, SBA_ALPHA, "sba")},
    "TSB": {"family": "intermittent", "func": lambda h, horizon=HORIZON: croston_forecast(h, horizon, TSB_ALPHA, ("tsb", TSB_BETA))},
}

MODEL_ORDER = list(MODEL_LADDER)
BENCHMARK_DATASETS = {  # applicability from 05_experiments/config.json / app_data/models.csv
    "Naive": ["m5", "store_item_demand"],
    "Seasonal Naive": ["m5", "store_item_demand"],
    "Moving Average": ["m5", "store_item_demand"],
    "SES": ["m5", "store_item_demand"],
    "DES": ["m5", "store_item_demand"],
    "TES": ["m5", "store_item_demand"],
    "ARIMA": ["m5", "store_item_demand"],
    "SARIMA": ["store_item_demand"],
    "LSTM": ["m5", "store_item_demand"],
    "Croston": ["m5"],
    "SBA": ["m5"],
    "TSB": ["m5"],
}


def moving_average_window(dataset: str) -> int:
    return MA_WINDOW.get(dataset, 14)


def model_available(name: str) -> tuple[bool, str]:
    """Runtime availability (as opposed to research-scope applicability)."""
    if name == "LSTM" and not TORCH_AVAILABLE:
        return False, "torch not runnable in this environment (needs a NumPy-2 compatible torch build; works on Streamlit Cloud)"
    return True, ""


def compatibility(name: str, demand: np.ndarray) -> tuple[str, str]:
    """Dynamic compatibility report for a concrete demand series.

    Returns (status, reason) with status in {"suitable", "degraded", "unsuitable"}.
    Scope rules mirror the benchmark; data rules mirror each model's prechecks.
    """
    demand = np.asarray(demand, dtype=float)
    n = len(demand)
    zero_rate = float((demand == 0).mean()) if n else 1.0
    if name == "SARIMA" and n < 30:
        return "unsuitable", "needs >= 30 history points"
    if name in ("Croston", "SBA", "TSB"):
        if n and np.all(demand == 0):
            return "unsuitable", "all-zero history (no demand intervals to model)"
        if zero_rate < 0.2:
            return "degraded", "designed for intermittent demand; this series is dense (models the rate, not the shape)"
    if name == "ARIMA" and (n < 10 or zero_rate > 0.85):
        return "degraded", "falls back to repeating the last value (short history / sparse)"
    if name == "LSTM" and n < LSTM_LOOKBACK + HORIZON + 1:
        return "unsuitable", "needs more history than the 28-day lookback + 28-day horizon"
    if name in ("Naive", "Seasonal Naive", "Moving Average", "SES", "DES", "TES") and n < SEASON:
        return "unsuitable", "needs at least a week of history"
    if name == "LSTM" and not TORCH_AVAILABLE:
        return "unsuitable", model_available("LSTM")[1]
    return "suitable", ""
