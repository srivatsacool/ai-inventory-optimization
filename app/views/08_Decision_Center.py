"""Page 8 - DECISION CENTER. Five winners, never collapsed.

Winners: Best Forecaster · Lowest Inventory Cost · Highest Service ·
Lowest Inventory · Best Model Under User Constraints.
Only collapses into one when the user explicitly picks a single objective.
"""

import streamlit as st

from lib import engine as E
from lib import state
from lib.lab import (
    hero, inject_theme, insight_panel, lab_footer, meta_rail, metric_card,
    section_head,
)

inject_theme()
state.sandbox_badges()
hero("Decision Center",
     "One question at a time. Every objective below is a different question with a "
     "different answer — the pages never merge them unless you declare an objective.")
e = state.sandbox_gate("Decision Center")

# ---------------------------------------------------------------------------
section_head("Five questions", "Five independent answers")
objs = list(state.WINNER_OBJECTIVES)
cols = st.columns(4)
for col, name in zip(cols, objs):
    model, value = state.objective_winner(e, name)
    unit = {"Best Forecaster": "MAE (lower is better)",
            "Lowest Inventory Cost": "total cost",
            "Highest Service": "service level",
            "Lowest Inventory": "avg inventory"}[name]
    fmt = f"{value:.2%}" if name == "Highest Service" else (f"{value:.2f}" if value is not None else "—")
    metric_card(col, name, model or "—", fmt, unit, "SANDBOX result on your current run")

# 5th: under user constraints
section_head("Your constraints", "Best model that passes YOUR requirements")
st.caption("All rules optional — set 0 / off for anything you don't care about. "
           "Ranking within passing models: lowest total cost.")
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    max_cost = st.number_input("Max total cost", 0.0, 1e9, 0.0, key="dc_maxcost")
with c2:
    min_service = st.slider("Min service level", 0.0, 1.0, 0.0, 0.01, key="dc_minsvc", format="%.0f%%")
with c3:
    max_mase = st.number_input("Max MASE", 0.0, 1e6, 0.0, key="dc_maxmase")
with c4:
    max_inv = st.number_input("Max avg inventory", 0.0, 1e9, 0.0, key="dc_maxinv")
with c5:
    max_runtime = st.number_input("Max runtime (s)", 0.0, 1e6, 0.0, key="dc_maxrt")

cons = {"max_cost": max_cost or None, "min_service": min_service or None,
        "max_mase": max_mase or None, "max_avg_inventory": max_inv or None,
        "max_runtime": max_runtime or None}
winner, judged = state.constraints_winner(e, cons)
if winner:
    metric_card(st.container(), "Best model under user constraints", winner, "PASS",
                "passes every rule you set", "Cheapest among the passing models.")
    with st.expander("Constraint judgement — every model, every rule"):
        st.dataframe(judged.round(3), use_container_width=True, hide_index=True)
else:
    st.markdown('<div class="empty">No model passes your constraints. Relax a rule to see candidates.</div>',
                unsafe_allow_html=True)
    if len(judged):
        with st.expander("Constraint judgement — every model, every rule"):
            st.dataframe(judged.round(3), use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
section_head("Declared objective", "Collapse the answer — only if you say so")
st.caption("Pick one objective to declare as THE answer for this run. Leave it at "
           "'No single objective' to keep the five answers separate.")
declared = st.select_slider(
    "Objective", ["No single objective", "Best Forecaster", "Lowest Inventory Cost",
                  "Highest Service", "Lowest Inventory", "Best Under My Constraints"],
    key="dc_objective")
if declared != "No single objective":
    if declared == "Best Under My Constraints":
        m = winner
        st.success(f"**{declared} → {m or 'none passes'}** — by your constraint set, not by ours.")
    else:
        m, v = state.objective_winner(e, declared)
        st.success(f"**{declared} → {m}** ({v:.3f}) — declared by you for this run.")
else:
    st.info("No single 'best model' is declared. The five answers above stand on their own — "
            "collapsing them would hide exactly the trade-offs this lab exists to show.")

# Accuracy ≠ Value teaser (data-driven)
from lib.diagnostics import accuracy_value_gap
gap = accuracy_value_gap(e["metrics_df"], e["inventory_df"])
if gap and not gap["agrees"]:
    insight_panel(
        f"<b>Accuracy ≠ Value, live:</b> best forecaster <b>{gap['best_forecaster']}</b> costs "
        f"<b>{gap['best_forecaster_cost']:.1f}</b>, but lowest-cost model "
        f"<b>{gap['best_cost_model']}</b> costs <b>{gap['best_cost']:.1f}</b> "
        f"(+{gap['gap_pct']:.1f}% penalty for choosing accuracy over value).",
        "Computed from the current run — not from the frozen benchmark. See Diagnostics for the full view.",
        tone="live",
    )
elif gap:
    insight_panel(
        f"On this run, <b>{gap['best_forecaster']}</b> is both the best forecaster and the "
        f"lowest-cost model — accuracy and value agree here.",
        "Change demand or policy in Data Studio / the Simulator and watch the agreement break.",
        tone="live",
    )

lab_footer("Next → Diagnostics: Demand DNA, error shapes, frontiers and heatmaps.")
