"""Page 9 - DIAGNOSTICS. Demand DNA, error shapes, accuracy-vs-cost,
cost decomposition, ranking, frontier, heatmaps, and Accuracy ≠ Value."""

import numpy as np
import pandas as pd
import streamlit as st

from lib import engine as E
from lib import state
from lib.lab import (
    chart_panel, hero, inject_theme, insight_panel, lab_footer, meta_rail,
    metric_card, section_head, model_color,
)
from lib.diagnostics import (
    accuracy_value_gap, demand_dna, fig_accuracy_vs_cost, fig_cost_decomposition,
    fig_error_distribution, fig_forecast_overlay, fig_heatmap,
    fig_service_cost_frontier,
)

inject_theme()
state.sandbox_badges()
hero("Diagnostics",
     "Why the winners win. Demand DNA, forecast-error shapes, cost decomposition and "
     "frontiers — all computed from the current run.")
e = state.sandbox_gate("Diagnostics")

models_ok = [m for m in e["models"] if e["statuses"].get(m) not in ("error", "unavailable")]
mets = e["metrics_df"].set_index("model")
inv = e["inventory_df"].set_index("model")
METRICS = ["MAE", "RMSE", "MASE", "RMSSE", "WAPE", "sMAPE"]

# ---------------------------------------------------------------------------
section_head("Demand DNA", "Zero rate · ADI · CV² · trend · weekly seasonality")
dna = demand_dna(e["series_df"]["demand"].to_numpy(dtype=float))
meta_rail([
    ("Zero rate", f'{dna["zero_rate"]:.0%}', "share of zero-demand days"),
    ("ADI", f'{dna["ADI"]:.2f}', "average demand interval (days)"),
    ("CV²", f'{dna["CV2"]:.2f}', "squared CV of non-zero sizes"),
    ("Mean · CV", f'{dna["mean"]:.1f} · {dna["CV"]:.2f}', "level & dispersion"),
    ("Trend", f'{dna["trend_per_day"]:+.3f}/d', "linear slope"),
    ("Weekly seasonality", f'{dna["weekly_seasonality"]:.2f}', "0–1 · variance explained"),
], cols=6)
st.caption(f'Quadrant (Syntetos-Boylan): <b>{dna["syntos_type"]}</b> — ADI/CV² classify whether '
           'Croston-family models are appropriate. In the frozen benchmark M5 is '
           'sparse/intermittent (64.5% zeros), Store is smooth (0.02%).', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
section_head("Forecast-error distribution", "How each model is wrong")
pick = st.multiselect("Models", models_ok, default=models_ok[:6], key="dg_err")
fig = fig_error_distribution({m: e["fc_by_model"][m] for m in pick}, e["actual"], pick)
chart_panel(fig, "", "Box of (forecast − actual) over the evaluation window. A model with a "
            "consistent bias still produces a tidy box — and still distorts inventory.")

# ---------------------------------------------------------------------------
section_head("Accuracy vs cost", "Does the best forecaster win the shelf?")
acc_metric = st.select_slider("Accuracy metric on X", METRICS, value="MAE", key="dg_acc")
fig = fig_accuracy_vs_cost(e["metrics_df"], e["inventory_df"], acc_metric)
chart_panel(fig, "", "Each point is a model: accuracy on X, simulated inventory cost on Y. "
            "A downward-sloping pattern means accuracy buys value; anything else is the "
            "Accuracy ≠ Value effect.", tag=("SANDBOX", "live"))

# ---------------------------------------------------------------------------
section_head("Cost decomposition", "Holding vs stockout")
fig = fig_cost_decomposition(e["inventory_df"])
chart_panel(fig, "", "Same total, different anatomy: cheap-to-hold/often-short vs "
            "expensive-to-hold/rarely-short. P/H ratio decides which hurts.")

# ---------------------------------------------------------------------------
section_head("Service–cost frontier", "Efficient models only")
fig = fig_service_cost_frontier(e["inventory_df"])
chart_panel(fig, "", "Models on the dotted frontier are not dominated: no other model "
            "delivers both higher service and lower cost.")

# ---------------------------------------------------------------------------
section_head("Model ranking", "Rank per metric, side by side")
ranks = mets[METRICS].rank().astype(int)
ranks = ranks.loc[ranks.mean(axis=1).sort_values().index]
fig = fig_heatmap(ranks, "Rank by metric (1 = best)", colorscale="RdYlGn", reverse=False, fmt="d")
chart_panel(fig, "", "A model can rank 1st on MAE and 6th on RMSSE — the metric you "
            "report decides the story you tell.")

# ---------------------------------------------------------------------------
section_head("Model × policy heatmap", "Cost across the 27-policy research grid")
with st.expander("Policy grid heatmap (27 research cells, current experiment)", expanded=True):
    cells = E.default_policy_grid()
    pol_labels = [f"L{dict(c)['lead_time']}·{dict(c)['service_target']:.0%}·P{dict(c)['P']:g}" for c in cells]
    grid = E.policy_grid(E.hash_series(e["actual"]), E.arrays_to_json(e["fc_by_model"]),
                         e["actual"], cells)
    grid = grid[grid.model.isin(models_ok)]
    pivot = grid.pivot_table(index="model", columns="policy_id", values="total_cost")
    pivot.columns = pol_labels
    chart_panel(fig_heatmap(pivot, "Total cost by model × policy"), "",
                "The 27-cell research grid run on the current experiment (cached).")

# ---------------------------------------------------------------------------
section_head("Accuracy ≠ Value", "The signature result, computed live")
gap = accuracy_value_gap(e["metrics_df"], e["inventory_df"], acc_metric)
if gap:
    c1, c2 = st.columns(2)
    metric_card(c1, "Best forecaster (lowest " + acc_metric + ")", gap["best_forecaster"],
                f"{gap['best_forecaster_cost']:.1f}", "its total inventory cost",
                "The forecaster you would pick on accuracy alone.")
    metric_card(c2, "Lowest-cost model", gap["best_cost_model"],
                f"{gap['best_cost']:.1f}", "total inventory cost",
                f"Accuracy premium: {gap['gap_abs']:.1f} ({gap['gap_pct']:+.1f}%) — "
                "what choosing the best forecaster costs you on the shelf.")
    if gap["agrees"]:
        insight_panel("On this run the two coincide. Scenario the demand or move a policy "
                      "knob — the split usually reappears.", tone="live")
    else:
        insight_panel(
            f"<b>{gap['best_forecaster']}</b> forecasts best but costs "
            f"<b>+{gap['gap_pct']:.1f}%</b> more on the shelf than <b>{gap['best_cost_model']}</b>. "
            "Same policy, same data — only the forecast behavior differs.",
            "This is the thesis, reproduced on your own experiment. Nothing here is hard-coded.",
            tone="live")
lab_footer("Next → Experiments: provenance for every sandbox run.")
