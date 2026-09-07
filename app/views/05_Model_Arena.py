"""Page 5 - MODEL ARENA. The full model ladder, scored on the current experiment."""

import pandas as pd
import streamlit as st

from lib import engine as E
from lib import models as M
from lib import state
from lib.lab import (
    chart_panel, fig_base, hero, inject_theme, insight_panel, lab_footer,
    meta_rail, section_head, model_color,
)
from lib.diagnostics import fig_heatmap

inject_theme()
state.sandbox_badges()
hero("Model Arena",
     "The research model ladder on your current series: accuracy ladder, dynamic "
     "compatibility report, and runtime — benchmark scope rules preserved, custom data "
     "reported honestly.")
e = state.sandbox_gate("Model Arena")

mets = e["metrics_df"].set_index("model")
statuses = e["statuses"]
METRICS = ["MAE", "RMSE", "MASE", "RMSSE", "WAPE", "sMAPE"]

# ---------------------------------------------------------------------------
section_head("Accuracy ladder", "All six metrics · best per column highlighted")
sort_metric = st.select_slider("Rank by", METRICS, value="MAE", key="ma_sort")
tab = mets[METRICS].copy()
tab.insert(0, "status", [statuses.get(m, "?") for m in tab.index])
tab = tab.sort_values(sort_metric)
styled = tab.style.format({m: "{:.3f}" for m in METRICS})
st.dataframe(styled, use_container_width=True)
best = {m: tab[m].idxmin() for m in METRICS}
st.caption("★ best: " + " · ".join(f"**{mm} → {best[mm]}**" for mm in METRICS)
           + " · all six metrics are 'lower is better'. SANDBOX results.")

section_head("Dynamic compatibility", "Can each model run on *this* demand — and why")
dna_map = {}
rows = []
for m in M.MODEL_ORDER:
    comp_status, comp_reason = M.compatibility(m, e["history"])
    avail, avail_note = M.model_available(m)
    in_scope = e["dataset"] in M.BENCHMARK_DATASETS.get(m, [])
    scope_note = "benchmark scope" if in_scope else "outside benchmark scope (custom-data run)"
    rows.append({
        "model": m,
        "compatibility": comp_status,
        "reason": comp_reason or scope_note,
        "run status": statuses.get(m, "not selected"),
        "benchmark datasets": " + ".join(M.BENCHMARK_DATASETS[m]),
    })
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
st.caption("Benchmark mode preserves the research scope restrictions (SARIMA → Store, "
           "Croston/SBA/TSB → M5). In custom-data mode every model reports compatibility "
           "dynamically instead of silently executing an unsuitable model.")

# ---------------------------------------------------------------------------
section_head("Runtime", "Fit time per model (this experiment)")
fig = fig_base(height=340)
rt = pd.Series(runtimes := {r.model: r.runtime_s for r in E.model_status_table(e["fc_long"]).itertuples()})
rt = rt.sort_values(ascending=False)
fig.add_bar(x=rt.index, y=rt.values, marker_color=[model_color(m) for m in rt.index], showlegend=False)
fig.update_yaxes(title="seconds (first fit, uncached)")
chart_panel(fig, "", "ARIMA/SARIMA fit per series; LSTM trains a small network (sandbox "
            "variant of the research global LSTM). Cached runs return instantly.")
lab_footer("Next → Inventory Simulator: turn these forecasts into stock decisions.")
