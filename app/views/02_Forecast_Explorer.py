"""Page 2 - FORECAST EXPLORER. Interactive model-analysis workspace.

Two data layers, clearly separated:
  * FROZEN rankings come read-only from the number sheet (full study).
  * DERIVED forecast-vs-actual lines come from app_data/ cached samples and
    are labeled as such. Nothing is computed from raw research data here.
"""

import numpy as np
import pandas as pd
import streamlit as st

from lib import appdata_loader as A
from lib import frozen_loader as F
from lib.lab import (
    INDIGO, INDIGO_L, MUTED, STEEL_L, TEAL, TEAL_L, VIOLET_L, WHITE,
    badges, chart_panel, empty_state, fig_base, glossary, hero, inject_theme,
    insight_panel, kpi_strip, lab_footer, mono_annotation, section_head,
)

inject_theme()
badges(("Interactive / Experimental", "live"), ("Sample data · derived", "dim"), ("v1.0", "ver"))
hero("Forecast Explorer",
     "Interrogate how each model behaves. Rankings are frozen full-study evidence; "
     "the trace chart runs on a cached origin-1 sample so you can see the shape of demand.")

missing = [k for k, ok in A.check_all_present().items() if not ok]
if missing:
    empty_state(f"app_data missing: {missing}. Run <code>python scripts/build_app_data.py</code> from the repo root.")
    st.stop()

rep = A.load_representative_series()
fc = A.load_forecasts_sample()
LADDER = ["Naive", "Seasonal Naive", "Moving Average", "SES", "DES", "TES",
          "ARIMA", "SARIMA", "CROSTON", "SBA", "TSB", "LSTM"]
SERIES_LABEL = {
    "FOODS_1_098_CA_3_evaluation": "CA-3 · FOODS_1_098 (M5)",
    "FOODS_1_133_TX_3_evaluation": "TX-3 · FOODS_1_133 (M5)",
    "S01_I01": "Store S01 · item 01", "S01_I02": "Store S01 · item 02",
    "store_10_item_1": "Store 10 · item 1", "store_10_item_10": "Store 10 · item 10",
}

# ---------- unified control rail (sticky, divided; only options backed by data) ----------
_rc = st.columns(4)
with _rc[0]:
    ds = st.segmented_control("Dataset", ["M5", "Store"], default="M5", key="fe_ds") or "M5"
ds_key = "m5" if ds == "M5" else "store_item_demand"
series_opts = sorted(rep.loc[rep["dataset"] == ds_key, "series_id"].unique().tolist())
with _rc[1]:
    series = st.segmented_control("Series", series_opts, default=series_opts[0], key="fe_series",
                                  format_func=lambda s: SERIES_LABEL.get(s, s))
series_id = series or series_opts[0]
# model list = what the cached sample actually holds for this series
models_here = [m for m in LADDER if m in fc[(fc["series_id"] == series_id)]["model"].unique().tolist()]
with _rc[2]:
    metric = st.segmented_control("Metric (frozen)", ["MASE", "MAE", "RMSE", "sMAPE"], default="MASE", key="fe_metric") or "MASE"
with _rc[3]:
    view = st.segmented_control("View", ["Ranking", "Forecast vs actual", "Errors"], default="Ranking", key="fe_view") or "Ranking"

# ---------- VIEW: ranking (frozen) ----------
if view == "Ranking":
    ns = F.load_number_sheet()
    rank = ns[(ns["metric"] == metric) & (ns["dataset"] == ds_key)].sort_values("value")
    fig = fig_base(height=max(320, 40 * len(rank) + 100))
    colors = [TEAL if m == rank["model"].iloc[0] else STEEL_L for m in rank["model"]]
    fig.add_bar(x=rank["value"], y=rank["model"], orientation="h", marker_color=colors, width=.62,
                hovertemplate="%{y}<br>" + metric + " %{x:.4f}<extra></extra>")
    unit = "pct" if metric == "sMAPE" else "units"
    fig.update_layout(title=dict(text=f"{metric} by model · lower is better — {ds} (frozen full study)",
                                 font=dict(size=16, color=WHITE), x=.01),
                      xaxis_title=f"{metric} ({unit})")
    fig.add_annotation(mono_annotation(rank["value"].iloc[0] * 1.015, 0, "winner", color=TEAL_L, xanchor="left"))
    chart_panel(fig, "", "500 series × 8 origins × 28 days, identical evaluation windows for every model.",
                tag=("Frozen evidence", "frozen"))
    w = rank.iloc[0]; worst = rank.iloc[-1]
    insight_panel(
        f"<b>{w['model']}</b> holds the lowest {metric} ({w['value']:.3f}) on {ds}; "
        f"worst is <b>{worst['model']}</b> ({worst['value']:.3f}).",
        "Forecast accuracy is a useful signal, but it does not determine inventory cost by itself — "
        "switch to 03 Inventory Lab to see what each ranking actually buys.",
        tone="frozen",
    )

# ---------- VIEW: forecast vs actual (derived sample) ----------
elif view == "Forecast vs actual":
    srep = rep[rep["series_id"] == series_id].sort_values("forecast_date")
    chosen = st.multiselect("Overlay models", models_here,
                            default=[m for m in ["Moving Average", "SES", "LSTM"] if m in models_here] or models_here[:3],
                            key="fe_models")
    if not chosen:
        empty_state("Pick at least one model to overlay on actuals.")
        st.stop()
    fig = fig_base(height=600)
    fig.add_scatter(x=srep["forecast_date"], y=srep["actual"], mode="lines+markers", name="Actual",
                    line=dict(color=WHITE, width=2.4), hovertemplate="actual %{y}<extra></extra>")
    pal = [STEEL_L, TEAL_L, VIOLET_L, INDIGO_L, "#B8956A", "#7FBDE6", "#9AA4B5", "#5F7A9E", "#6FA88F", "#8F7FB8", "#C78B94", "#7C8AA0"]
    for i, m in enumerate(chosen):
        g = fc[(fc["series_id"] == series_id) & (fc["model"] == m)].sort_values("forecast_date")
        if g.empty:
            continue
        fig.add_scatter(x=g["forecast_date"], y=g["forecast"], mode="lines", name=m,
                        line=dict(color=pal[i % len(pal)], width=1.7, dash="dot"),
                        hovertemplate=m + " %{y}<extra></extra>")
    fig.update_layout(
        title=dict(text=f"Forecast vs actual — {SERIES_LABEL.get(series_id, series_id)} · origin 1, H28",
                   font=dict(size=16, color=WHITE), x=.01),
        xaxis_title="Date", yaxis_title="Demand (units)", hovermode="x unified",
        legend=dict(orientation="h", y=-0.22),
    )
    chart_panel(fig, "", "Cached sample (derived), not frozen evidence. The frozen full study covers all 8 origins; this is the readable one.",
                tag=("Derived sample", "live"))
    zero = float((srep["actual"] == 0).mean())
    kpi_strip([
        ("Series", "M5" if ds_key == "m5" else "Store", "dataset"),
        ("Horizon", "28 d", "origin 1"),
        ("Zero-demand share", f"{zero:.0%}", "sparse" if zero > .3 else "dense"),
        ("Models cached", f"{len(models_here)}", "this series"),
        ("Sample size", f"{len(srep)}", "points"),
    ])

# ---------- VIEW: errors (derived sample) ----------
else:
    chosen = st.multiselect("Error models", models_here,
                            default=[m for m in ["Moving Average", "SES", "LSTM"] if m in models_here] or models_here[:3],
                            key="fe_err_models")
    if not chosen:
        empty_state("Pick at least one model.")
        st.stop()
    tab1, tab2 = st.tabs(["Error by day", "Error distribution"])
    with tab1:
        fig = fig_base(height=520)
        for i, m in enumerate(chosen):
            g = fc[(fc["series_id"] == series_id) & (fc["model"] == m)].sort_values("forecast_date")
            if g.empty:
                continue
            fig.add_scatter(x=g["forecast_date"], y=g["forecast"] - g["actual"], mode="lines+markers", name=m,
                            line=dict(color=[STEEL_L, TEAL_L, VIOLET_L, INDIGO_L][i % 4], width=1.6),
                            hovertemplate=m + " err %{y:.1f}<extra></extra>")
        fig.add_hline(y=0, line_color=MUTED, line_width=1)
        fig.update_layout(
            title=dict(text="Signed error by day (forecast − actual) · origin 1, H28", font=dict(size=16, color=WHITE), x=.01),
            yaxis_title="Error (units)", hovermode="x unified", legend=dict(orientation="h", y=-0.22),
        )
        chart_panel(fig, "", "Above the line = over-forecast (extra holding); below = under-forecast (stockout risk).",
                    tag=("Derived sample", "live"))
    with tab2:
        fig = fig_base(height=520)
        for i, m in enumerate(chosen):
            g = fc[(fc["series_id"] == series_id) & (fc["model"] == m)]
            if g.empty:
                continue
            fig.add_histogram(x=(g["forecast"] - g["actual"]), name=m, opacity=.55, nbinsx=24,
                              marker_color=[STEEL_L, TEAL_L, VIOLET_L, INDIGO_L][i % 4],
                              hovertemplate=m + "<br>err %{x:.1f}<br>n %{y}<extra></extra>")
        fig.update_layout(barmode="overlay",
                          title=dict(text="Absolute error distribution · origin 1, H28", font=dict(size=16, color=WHITE), x=.01),
                          xaxis_title="Error (units)", yaxis_title="Days")
        chart_panel(fig, "", "A tall, narrow spread near zero is a calm forecast; wide tails are what inventory cost punishes.",
                    tag=("Derived sample", "live"))
    insight_panel(
        f"Sample series <b>{SERIES_LABEL.get(series_id, series_id)}</b> — cached forecasts for {len(chosen)} overlay model(s).",
        "The shapes here explain the frozen rankings: models that mis-read zero-demand stretches produce the fat tails "
        "the common policy pays for in holding or stockout cost.",
        tone="live",
    )

glossary("MASE", "MAE", "RMSE", "sMAPE", "Intermittent demand", "Dense demand")
lab_footer("Next → 03 Inventory Lab: change the policy and watch the winner move.")
