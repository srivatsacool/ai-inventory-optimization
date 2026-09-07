"""Page 3 - DATA STUDIO. Select / upload / edit demand, apply scenarios.

Sandbox only. Never touches frozen files: built-in series come from the
derived extract app_data/interactive_series.parquet; CSV uploads live in
session state only.
"""

import io

import numpy as np
import pandas as pd
import streamlit as st

from lib import engine as E
from lib import models as M
from lib import scenarios as S
from lib import state
from lib.lab import (
    badges, chart_panel, empty_state, fig_base, hero, inject_theme, insight_panel,
    lab_footer, meta_rail, section_head, model_color,
)
from lib.diagnostics import demand_dna, fig_series_profile

inject_theme()
state.sandbox_badges()
hero("Data Studio",
     "Choose a series, reshape its demand, and launch the experiment. Everything downstream — "
     "forecasts, metrics, inventory, policy — follows this configuration.")

# ---------------------------------------------------------------------------
# 1 · Source
# ---------------------------------------------------------------------------
section_head("01 · Source", "Where the demand comes from")
source = st.segmented_control("Data source", ["Built-in series", "CSV upload"], key="ds_source")

csv_df = None
csv_name = ""
if source == "CSV upload":
    up = st.file_uploader("Upload a demand CSV (session-only — nothing is saved to disk)",
                          type=["csv"], key="ds_csv")
    if up is not None:
        raw = pd.read_csv(io.BytesIO(up.getvalue()))
        num_cols = [c for c in raw.columns if pd.api.types.is_numeric_dtype(raw[c])]
        date_cols = [c for c in raw.columns if pd.api.types.is_datetime64_any_dtype(raw[c])]
        if not date_cols:
            for c in raw.columns:
                if c in num_cols:
                    continue
                try:
                    parsed = pd.to_datetime(raw[c], errors="raise")
                    if parsed.notna().mean() > 0.9:
                        raw[c] = parsed
                        date_cols.append(c)
                except Exception:
                    pass
        if not num_cols:
            st.error("No numeric column found in the CSV.")
        else:
            schema = pd.DataFrame({
                "column": raw.columns,
                "dtype": [str(raw[c].dtype) for c in raw.columns],
                "n_unique": [raw[c].nunique() for c in raw.columns],
                "role": ["date" if c in date_cols else ("demand candidate" if c in num_cols else "ignored") for c in raw.columns],
            })
            with st.expander("Detected schema", expanded=True):
                st.dataframe(schema, hide_index=True, use_container_width=True)
            if len(num_cols) > 1:
                val_col = st.selectbox("Demand column", num_cols, key="ds_valcol")
            else:
                val_col = num_cols[0]
            demand = pd.to_numeric(raw[val_col], errors="coerce").fillna(0.0).clip(lower=0.0)
            dates = pd.to_datetime(raw[date_cols[0]]) if date_cols else pd.date_range("2000-01-01", periods=len(raw))
            csv_df = pd.DataFrame({"date": dates, "demand": demand})
            csv_name = up.name

# ---------------------------------------------------------------------------
# 2 · Series & window
# ---------------------------------------------------------------------------
section_head("02 · Series", "Which demand to study")
if source == "Built-in series":
    cat = E.load_catalog()
    ds_label = st.segmented_control("Dataset", ["M5", "Store Item Demand"], key="ds_dataset") or "M5"
    dataset = "m5" if ds_label == "M5" else "store_item_demand"
    sub = cat[cat.dataset == dataset].sort_values("series_id")
    ids = sub["series_id"].tolist()
    default_ix = ids.index("FOODS_1_098_CA_3_evaluation") if "FOODS_1_098_CA_3_evaluation" in ids else 0
    series_id = st.selectbox(f"Series ({len(sub)} available)" if dataset == "m5" else "Series",
                             ids, index=default_ix, key="ds_series")
    row = sub[sub.series_id == series_id].iloc[0]
    series_df = E.get_series(dataset, series_id)
    meta = [(dataset, "dataset"), ("series", series_id)]
else:
    if csv_df is None:
        empty_state("Upload a CSV above to continue.")
        st.stop()
    dataset = "custom"
    series_id = csv_name
    series_df = csv_df
    row = None
    meta = [("csv", series_id)]

dates_all = series_df["date"]
n_all = len(series_df)
if n_all < 60:
    st.error(f"Series too short ({n_all} points) — need at least 60 for a 28-day horizon with usable history.")
    st.stop()

# Evaluation window
with st.expander("Evaluation window & direct editing", expanded=True):
    cA, cB = st.columns([1, 2])
    with cA:
        horizon = st.select_slider("Horizon (days)", options=[7, 14, 21, 28], value=28, key="ds_horizon")
        if source == "Built-in series":
            origin_choices = [d.strftime("%Y-%m-%d") for d in
                              pd.date_range("2016-03-01", periods=8, freq="7D") if d <= dates_all.iloc[-1]]
            origin_pick = st.selectbox("Evaluation starts (origin date)", origin_choices, key="ds_origin")
            # truncate series so the last horizon days start at the origin
            cut = dates_all[dates_all == origin_pick].index[0]
            series_df = series_df.iloc[cut:].reset_index(drop=True)
            dates_all = series_df["date"]
        else:
            st.caption("Custom CSV: the last horizon days are the evaluation window.")
    with cB:
        st.caption("Edit demand directly (this overrides the stored series). Last 365 days shown; "
                   "edits apply on 'Run'.")
        edit_n = min(365, len(series_df))
        edited = st.data_editor(
            series_df.tail(edit_n).reset_index(drop=True)[["date", "demand"]],
            use_container_width=True, height=250, key=f"ds_edit_{series_id}",
            num_rows="fixed",
        )

# ---------------------------------------------------------------------------
# 03 · Scenarios
# ---------------------------------------------------------------------------
section_head("03 · Scenario", "Reshape the demand")
preset = st.selectbox("Named scenario", list(S.SCENARIOS), key="ds_preset")
with st.expander("Fine-grained controls", expanded=bool(preset != "Baseline (no change)")):
    c1, c2, c3 = st.columns(3)
    with c1:
        level = st.slider("Demand level ×", 0.2, 3.0, 1.0, 0.05, key="ds_level")
        trend_pd = st.slider("Trend (units/day, last 90 d)", -2.0, 2.0, 0.0, 0.1, key="ds_trend")
    with c2:
        season_amp = st.slider("Weekly seasonality ×", 0.0, 2.5, 1.0, 0.05, key="ds_season")
        vol = st.slider("Volatility (noise σ)", 0.0, 1.0, 0.0, 0.05, key="ds_vol")
    with c3:
        zero_rate = st.slider("Target zero-demand rate", 0.0, 0.95, 0.0, 0.05, key="ds_zero")
        shock_kind = st.select_slider("Shock", ["none", "spike", "drop"], key="ds_shockkind")
        shock_factor = st.slider("Shock factor ×", 0.2, 4.0, 1.5, 0.1, key="ds_shockf") if shock_kind != "none" else 1.0

cfg = {
    "level": level, "trend_per_day": trend_pd, "seasonality": season_amp,
    "volatility": vol, "zero_rate": zero_rate,
    "shock_kind": shock_kind if shock_kind != "none" else None,
    "shock_factor": shock_factor if shock_kind != "none" else None,
    "_name": preset if any([level != 1, trend_pd, season_amp != 1, vol, zero_rate, shock_kind != "none"]) else "",
}

# apply edits (explicit button: st.data_editor edits are detected by key change)
applied = series_df.copy()
if edited is not None:
    edit_dates = edited["date"].astype(str)
    base_dates = applied["date"].astype(str)
    changed = edited["demand"].to_numpy(dtype=float)
    tail = applied.tail(len(edited)).index
    mask = ~np.isclose(applied.loc[tail, "demand"].to_numpy(dtype=float), changed, equal_nan=True)
    if mask.any():
        applied.loc[tail[mask], "demand"] = changed[mask]

# ---------------------------------------------------------------------------
# 04 · Models & policy defaults
# ---------------------------------------------------------------------------
section_head("04 · Models & policy", "What the run includes")
available, notes = zip(*[M.model_available(m) for m in M.MODEL_ORDER])
default_models = [m for m, ok in zip(M.MODEL_ORDER, available) if ok]
model_pick = st.multiselect("Models in this run", M.MODEL_ORDER, default=default_models, key="ds_models")
if not model_pick:
    st.warning("Select at least one model.")
    st.stop()
c1, c2, c3, c4 = st.columns(4)
with c1:
    L = st.number_input("Lead time L (days)", 1, 30, 7, key="ds_L")
with c2:
    sv = st.slider("Service target", 0.5, 0.999, 0.95, 0.005, key="ds_sv")
with c3:
    H = st.number_input("Holding cost H (per unit-day)", 0.1, 20.0, 1.0, 0.1, key="ds_H")
with c4:
    P = st.number_input("Stockout penalty P (per unit)", 0.5, 100.0, 5.0, 0.5, key="ds_P")
policy = {"lead_time": int(L), "service_target": float(sv), "H": float(H), "P": float(P),
          "z": None, "sigma_floor": 0.1}

run = st.button("▶ Run experiment", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Build / refresh experiment (button, or automatically on any config change)
# ---------------------------------------------------------------------------
finger = E.hash_series(applied["demand"].to_numpy(dtype=float)) + "|" + "|".join(
    [str(horizon), str(cfg), ",".join(model_pick), str(policy), str(series_id), source])
if run or state.exp() is None or st.session_state.get("ds_fingerprint") != finger:
    with st.spinner("Running forecast ladder + inventory simulation…"):
        e = state.build_experiment("CSV upload" if source == "CSV upload" else "Built-in",
                                   dataset, dataset, series_id, applied, int(horizon),
                                   cfg, list(model_pick), policy)
        e["dataset_kind"] = dataset if dataset in ("m5", "store_item_demand") else "custom"
        state.log_experiment(e)
        st.session_state["exp"] = e
        st.session_state["ds_fingerprint"] = finger

e = state.exp()

# ---------------------------------------------------------------------------
# Result summary
# ---------------------------------------------------------------------------
section_head("Current experiment", f'{e["exp_id"]} · {e["scenario_name"] or "no scenario"}')
scenario_note = (f"scenario applied: <b>{e['scenario_name']}</b>" if e["scenario_name"]
                 else "baseline demand (no scenario applied)")
meta_rail([
    ("Experiment", e["exp_id"], "sandbox ID"),
    ("Series", e["series_id"][:28], f'{e["dataset"]} · n={len(e["series_df"])} d'),
    ("Evaluation", f'{e["horizon"]} d from {e["origin_date"]:%Y-%m-%d}' if hasattr(e["origin_date"], "strftime") else f'{e["horizon"]} d', "last horizon days"),
    ("Models", f'{len(e["models"])}', ", ".join(e["models"][:4]) + ("…" if len(e["models"]) > 4 else "")),
    ("Policy", f'L{e["policy"]["lead_time"]} · {e["policy"]["service_target"]:.0%} · H={e["policy"]["H"]:g} · P={e["policy"]["P"]:g}', "order-up-to"),
], cols=5)
insight_panel(scenario_note, "All downstream pages (Forecast Lab, Model Arena, Inventory "
              "Simulator, Policy Lab, Decision Center, Diagnostics, Experiments) now run on "
              "this configuration. Each run is logged with full provenance — nothing touches "
              "the frozen benchmark.", tone="live")

# Demand DNA + profile
dna = demand_dna(e["series_df"]["demand"].to_numpy(dtype=float))
section_head("Demand DNA", "What this series looks like now")
meta_rail([
    ("Zero rate", f'{dna["zero_rate"]:.0%}', "share of zero days"),
    ("ADI", f'{dna["ADI"]:.2f} d', "avg interval between demands"),
    ("CV²", f'{dna["CV2"]:.2f}', "squared CV of nonzero sizes"),
    ("Mean / trend", f'{dna["mean"]:.1f} · {dna["trend_per_day"]:+.3f}/d', "level & drift"),
    ("Weekly seasonality", f'{dna["weekly_seasonality"]:.2f}', "0–1 strength"),
], cols=5)
st.caption(f'Croston-type classification: <b>{dna["syntos_type"]}</b> demand (ADI/CV² quadrant).', unsafe_allow_html=True)

dates = pd.to_datetime(e["series_df"]["date"])
fig = fig_series_profile(dates, e["series_df"]["demand"])
chart_panel(fig, "Demand series (post-edits, post-scenario)", "",
            tag=("SANDBOX", "live"))
lab_footer("Next → Forecast Lab: watch all models respond to this demand.")
