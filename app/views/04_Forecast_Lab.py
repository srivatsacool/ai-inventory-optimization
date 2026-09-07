"""Page 4 - FORECAST LAB. Overlay chart + model cards for the current experiment."""

import pandas as pd
import streamlit as st

from lib import engine as E
from lib import models as M
from lib import state
from lib.lab import (
    FROZEN, INK, chart_panel, hero, inject_theme, insight_panel, lab_footer,
    meta_rail, metric_card, model_color, mono_annotation, section_head, fig_base,
)
from lib.diagnostics import fig_forecast_overlay

inject_theme()
state.sandbox_badges()
hero("Forecast Lab",
     "Every model, run on your current demand with leakage-free history. Overlay shows "
     "history, actuals and all forecasts; each card carries the values, runtime and metrics.")
e = state.sandbox_gate("Forecast Lab")

mets = e["metrics_df"].set_index("model")
statuses = e["statuses"]
shown = [m for m in e["models"] if statuses.get(m) not in ("error", "unavailable")]

# ---------------------------------------------------------------------------
section_head("Overlay", "History · actuals · all model forecasts")
dates = pd.to_datetime(e["series_df"]["date"])
n = len(e["series_df"])
hist_dates = dates.iloc[:-e["horizon"]]
eval_dates = dates.iloc[-e["horizon"]:]
fig = fig_forecast_overlay(hist_dates, e["history"], eval_dates, e["actual"],
                           {m: e["fc_by_model"][m] for m in shown if m in e["fc_by_model"]})
chart_panel(fig, "", "History is everything before the evaluation window; models never see "
            "the actuals they are scored against.", tag=("SANDBOX", "live"))

# ---------------------------------------------------------------------------
section_head("Model cards", "Forecast values, runtime, status, all six metrics")
METRICS = ["MAE", "RMSE", "MASE", "RMSSE", "WAPE", "sMAPE"]
best = {m: mets[m].idxmin() for m in METRICS}  # lower is better for all six

card_models = st.multiselect("Cards to show", shown, default=shown, key="fl_cards")
runtimes = {r.model: r.runtime_s for r in E.model_status_table(e["fc_long"]).itertuples()}
cols = st.columns(3)
for i, m in enumerate(card_models):
    r = mets.loc[m]
    star_metrics = [mm for mm in METRICS if best[mm] == m]
    stars = " ".join(f'<span style="color:#3D7B55;font-weight:700">★{mm}</span>' for mm in star_metrics) or "&nbsp;"
    with cols[i % 3]:
        st.markdown(
            f"""<div class="mc tone-forecast"><div class="mc-k">{M.MODEL_LADDER[m]['family']}</div>
            <div class="mc-model">{m}</div>
            <div class="mc-value">{r['MAE']:.2f}</div>
            <div class="mc-unit">MAE · lower is better</div>
            <div class="mc-note">{' · '.join(f"{mm} {r[mm]:.3f}" for mm in METRICS[1:])}
            <br>runtime {runtimes.get(m, 0):.3f}s · status {statuses.get(m, '?')}</div>
            <div class="mc-note">{stars}</div></div>""",
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
section_head("Forecast values", "28-day horizon, per model")
with st.expander("Forecast table (all models × horizon)", expanded=False):
    tab = pd.DataFrame({m: e["fc_by_model"][m] for m in shown}).round(2)
    tab.index = [f"d{h+1}" for h in range(len(tab))]
    tab["ACTUAL"] = e["actual"]
    st.dataframe(tab, use_container_width=True)
st.caption("d1 = first forecast day after the origin. SANDBOX results — never research evidence.")

insight_panel(
    f"<b>Best MAE:</b> {best['MAE']} ({mets.loc[best['MAE'], 'MAE']:.2f}). "
    f"Best per metric: " + " · ".join(f"{mm} → <b>{best[mm]}</b>" for mm in METRICS),
    "Different metrics crown different models. The Inventory Simulator shows what these "
    "forecasts do to stock, cost and service.",
    tone="live",
)
lab_footer("Next → Model Arena for the full accuracy ladder and compatibility report.")
