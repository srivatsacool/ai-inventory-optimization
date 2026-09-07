"""Page 6 - INVENTORY SIMULATOR. Forecast → safety stock → order-up-to → cost.

Exposes L, service target, H, P; reproduces the research order-up-to logic
(11_src/inventory_policy.py, imported — never reimplemented) and shows the
complete calculation chain with 'Show calculation' expanders.
"""

import numpy as np
import pandas as pd
import streamlit as st

from lib import engine as E
from lib import state
from lib.lab import (
    badges, chart_panel, fig_base, hero, inject_theme, insight_panel, kpi_strip,
    lab_footer, meta_rail, section_head, model_color,
)
from lib.diagnostics import fig_cost_decomposition

inject_theme()
state.sandbox_badges()
hero("Inventory Simulator",
     "The same order-up-to policy the research benchmark uses — applied to your forecasts, "
     "step by step. Change a policy knob and the whole chain recomputes.")
e = state.sandbox_gate("Inventory Simulator")

# ---------------------------------------------------------------------------
section_head("Policy", "Lead time · service target · costs")
c1, c2, c3, c4 = st.columns(4)
with c1:
    L = st.slider("Lead time L (days)", 1, 30, e["policy"]["lead_time"], key="inv_L")
with c2:
    sv = st.slider("Service target", 0.50, 0.999, e["policy"]["service_target"], 0.005, key="inv_sv",
                   format="%.3f")
with c3:
    H = st.number_input("Holding cost H / unit-day", 0.1, 20.0, e["policy"]["H"], 0.1, key="inv_H")
with c4:
    P = st.number_input("Stockout penalty P / unit", 0.5, 100.0, e["policy"]["P"], 0.5, key="inv_P")

policy = {"lead_time": int(L), "service_target": float(sv), "H": float(H), "P": float(P),
          "z": None, "sigma_floor": 0.1}
if any(policy[k] != e["policy"][k] for k in ("lead_time", "service_target", "H", "P")):
    e = state.rerun_with(e, policy=policy)
    st.session_state["exp"] = e

model_pick = st.selectbox("Model driving the policy",
                          [m for m in e["models"] if e["statuses"].get(m) not in ("error", "unavailable")],
                          key="inv_model")
fc = e["fc_by_model"][model_pick]
act = e["actual"]
chain = E.simulation_chain(fc, act, e["policy"])
inv_row = e["inventory_df"].set_index("model").loc[model_pick]

# ---------------------------------------------------------------------------
section_head("KPIs", "Current policy · current model")
kpi_strip([
    ("Safety stock", f'{chain["safety_stock"]:.1f}', f"z={chain['z']:.2f} · σ={chain['err_std']:.2f} · √L=√{chain['lead_time']}"),
    ("Order-up-to level", f'{chain["days"]["order_up_to"].iloc[0]:.1f}', f"lead-time demand + SS (day 1)"),
    ("Total cost", f'{chain["total_cost"]:.1f}', f"H={e['policy']['H']:g} · P={e['policy']['P']:g}"),
    ("Service level", f'{chain["service_level"]:.0%}', f"{chain['stockout_days']} stockout days"),
    ("Avg inventory", f'{chain["average_inventory"]:.1f}', f'{chain["reorder_count"]} reorders / {e["horizon"]} d'),
], cols=5)

# ---------------------------------------------------------------------------
section_head("The chain", "Forecast → volatility → safety stock → order-up-to → simulation → cost")

def calc(title, body, formulas: list[str]):
    with st.expander(f"ⓘ {title}"):
        st.markdown(body, unsafe_allow_html=True)
        for f in formulas:
            st.markdown(f'<div class="gloss" style="font-family:JetBrains Mono,monospace;">{f}</div>',
                        unsafe_allow_html=True)

calc(
    "1 · Forecast → forecast-error volatility (σ)",
    "The simulator compares each model's forecast with the actuals over the evaluation "
    "window and measures how noisy the forecast errors are. This σ is what safety stock "
    "must absorb — it is computed from the <b>same forecast you just inspected</b>.",
    [f"errors e = forecast − actual (28 values)",
     f"σ = std(e) = {chain['err_std']:.4f} (floored at {e['policy']['sigma_floor']})"],
)

calc(
    "2 · σ → safety stock (SS)",
    "Safety stock covers demand surprises during the lead time. The service target sets "
    "z, the standard-normal quantile: 95% → z = 1.645, 99% → z = 2.326.",
    [f"z = Φ⁻¹({e['policy']['service_target']:.3f}) = {chain['z']:.4f}",
     f"SS = z · σ · √L = {chain['z']:.4f} × {chain['err_std']:.4f} × √{chain['lead_time']} = {chain['safety_stock']:.3f}"],
)

calc(
    "3 · Forecasts → lead-time demand",
    "Each day, the expected demand over the next L days is the sum of the next L forecast "
    f"values (truncated at the horizon). Average across the window: {chain['avg_lead_time_demand']:.2f}.",
    [f"LT demand(d) = Σ forecast[d : d+L]  →  e.g. day 1 = {chain['days']['lead_time_demand'].iloc[0]:.1f}"],
)

calc(
    "4 · Lead-time demand + SS → order-up-to level",
    "The order-up-to level is the stock position you want to reach after ordering: enough "
    "to cover expected lead-time demand plus safety stock.",
    [f"order-up-to(d) = LT demand(d) + SS  →  day 1: {chain['days']['lead_time_demand'].iloc[0]:.1f} + {chain['safety_stock']:.2f} = {chain['days']['order_up_to'].iloc[0]:.2f}"],
)

calc(
    "5 · Daily review → orders (simulation)",
    f"Daily review with lost sales, exactly as in the research simulator: start with "
    f"initial on-hand = max(Σ first L forecasts, 1) = {chain['initial_inventory']:.1f}; each day receive "
    "arrivals, review position (on-hand + pipeline), order up to the level if below "
    "(arrives after L days), serve demand from on-hand; unmet demand is lost.",
    [f"if position(d) < order-up-to(d): order = difference ({chain['reorder_count']} orders placed)",
     "demand served = min(on-hand, demand); shortage = demand − served"],
)

calc(
    "6 · Simulation → holding + stockout cost → totals",
    f"Holding cost = H per unit on end-of-day on-hand; stockout cost = P per lost unit. "
    f"Totals: holding {chain['total_holding_cost']:.1f} + stockout {chain['total_stockout_cost']:.1f} "
    f"= <b>{chain['total_cost']:.1f}</b>. Service = 1 − stockout days/28 = {chain['service_level']:.1%}.",
    [f"holding = H × Σ end-of-day inventory = {e['policy']['H']:g} × {chain['total_holding_cost'] / max(e['policy']['H'], 1e-9):.1f} = {chain['total_holding_cost']:.2f}",
     f"stockout = P × lost units = {e['policy']['P']:g} × {chain['stockout_quantity']:.1f} = {chain['total_stockout_cost']:.2f}",
     f"avg inventory = holding cost / 28 = {chain['average_inventory']:.2f}",
     f"total cost = {chain['total_holding_cost']:.2f} + {chain['total_stockout_cost']:.2f} = {chain['total_cost']:.2f}"],
)

# Day-by-day table
with st.expander("Day-by-day simulation trace", expanded=False):
    st.dataframe(chain["days"].round(2), use_container_width=True, hide_index=True)
    st.caption("One row per evaluation day: arrival, review, order, demand served/lost, end-of-day inventory.")

# ---------------------------------------------------------------------------
section_head("Compare", "All models under this policy")
fig = fig_base(height=400)
df = e["inventory_df"].sort_values("total_cost")
fig.add_bar(x=df["model"], y=df["total_cost"], marker_color=[model_color(m) for m in df["model"]],
            showlegend=False)
fig.update_yaxes(title="Total cost")
chart_panel(fig, "", "Same policy, different forecast behavior — different cost. The "
            "Decision Center names the winners explicitly.")

with st.expander("Model × policy table (current policy)"):
    show = df[["model", "total_holding_cost", "total_stockout_cost", "total_cost",
               "service_level", "average_inventory", "reorder_count"]].round(3)
    st.dataframe(show, use_container_width=True, hide_index=True)

lab_footer("Next → Policy Lab: sweep all 27 policies or your own grid.")
