"""Page 7 - POLICY LAB. Full 27-policy grid or custom cells; winner matrix;
cost/service rankings; stability; user-defined pass/fail constraints."""

import numpy as np
import pandas as pd
import streamlit as st

from lib import engine as E
from lib import state
from lib.lab import (
    chart_panel, hero, inject_theme, insight_panel, lab_footer, meta_rail,
    section_head, model_color,
)
from lib.diagnostics import fig_heatmap

inject_theme()
state.sandbox_badges()
hero("Policy Lab",
     "Sweep the full 27-policy research grid — or your own — across every model. See who "
     "wins where, who is stable, and which models pass your requirements.")
e = state.sandbox_gate("Policy Lab")

# ---------------------------------------------------------------------------
section_head("Policy set", "27 research cells or custom")
mode = st.segmented_control("Grid", ["Full 27-policy grid", "Custom policies"], key="pl_mode")

if mode == "Custom policies":
    c1, c2, c3 = st.columns(3)
    with c1:
        lead_times = st.multiselect("Lead times L", [1, 2, 3, 5, 7, 10, 14, 21, 30], default=[3, 7, 14], key="pl_lt")
    with c2:
        targets = st.multiselect("Service targets", [0.80, 0.85, 0.90, 0.95, 0.98, 0.99],
                                 default=[0.90, 0.95, 0.99], key="pl_sv", format_func=lambda v: f"{v:.0%}")
    with c3:
        ps = st.multiselect("P (H = 1 fixed)", [1, 2, 3, 5, 8, 10, 15, 20, 50], default=[3, 5, 10], key="pl_p")
    if not (lead_times and targets and ps):
        st.warning("Pick at least one value in each column.")
        st.stop()
    cells = E.custom_policy_cells(lead_times, targets, ps)
else:
    cells = E.default_policy_grid()
    st.caption("Research grid: L {3, 7, 14} × service {90%, 95%, 99%} × P {3, 5, 10}, H = 1. "
               "The frozen cell is L7 · 95% · P=5.")

pol_labels = [f"L{p['lead_time']}·{p['service_target']:.0%}·P{p['P']:g}" for p in (dict(c) for c in cells)]

with st.spinner("Simulating model × policy cells…"):
    grid = E.policy_grid(E.hash_series(e["actual"]), E.arrays_to_json(e["fc_by_model"]),
                         e["actual"], cells)

models_ok = [m for m in e["models"] if e["statuses"].get(m) not in ("error", "unavailable")]
grid = grid[grid.model.isin(models_ok)]

# ---------------------------------------------------------------------------
section_head("Winner matrix", "Cheapest model in every cell")
cost_pivot = grid.pivot_table(index="model", columns="policy_id", values="total_cost")
cost_pivot.columns = pol_labels
winner_ids = cost_pivot.values.argmin(axis=0)
winner_names = [cost_pivot.index[i] for i in winner_ids]
win_counts = pd.Series(winner_names).value_counts()

fig = fig_heatmap(cost_pivot, "Total cost by model × policy (greener = cheaper)")
chart_panel(fig, "", "Each cell runs the full order-up-to simulation for that model under "
            "that policy. Hover for exact costs; the winner matrix below names each "
            "cell's cheapest model.", tag=("SANDBOX", "live"))

with st.expander("Winner per policy cell"):
    wtab = pd.DataFrame({"policy": pol_labels, "winner": winner_names,
                         "cost": [f"{cost_pivot.iloc[i, j]:.1f}" for j, i in enumerate(winner_ids)]})
    st.dataframe(wtab, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
section_head("Rankings", "Cost · service · stability")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Total cost — mean over all policy cells**")
    cost_rank = grid.groupby("model")["total_cost"].mean().sort_values()
    st.dataframe(cost_rank.round(2).to_frame("mean total cost"), use_container_width=True)
    st.markdown("**Service level — mean over all cells**")
    svc_rank = grid.groupby("model")["service_level"].mean().sort_values(ascending=False)
    st.dataframe(svc_rank.round(4).to_frame("mean service level"), use_container_width=True)
with c2:
    st.markdown("**Policy stability — cells won per model**")
    stab = win_counts.reindex(cost_pivot.index).fillna(0).astype(int).sort_values(ascending=False)
    st.dataframe(stab.to_frame("cells won"), use_container_width=True)
    st.caption(f"{len(cells)} cells total. A model winning every cell is robust to policy "
               "choice; a fragmented matrix means the policy decides, not the model.")

# ---------------------------------------------------------------------------
section_head("Requirements", "Your pass/fail rules — nothing is pre-decided")
st.caption("Set thresholds; blank/zero = rule off. Models are judged per policy cell and "
           "on the mean over cells. This is your constraint set, not ours.")
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    max_cost = st.number_input("Max mean total cost", 0.0, 1e9, 0.0, key="pl_maxcost",
                               help="0 = rule off")
with c2:
    min_service = st.slider("Min mean service level", 0.0, 1.0, 0.0, 0.01, key="pl_minsvc",
                            format="%.0f%%", help="0 = rule off")
with c3:
    max_mase = st.number_input("Max MASE (forecast)", 0.0, 1e6, 0.0, key="pl_maxmase",
                               help="0 = rule off")
with c4:
    max_inv = st.number_input("Max mean avg inventory", 0.0, 1e9, 0.0, key="pl_maxinv",
                              help="0 = rule off")
with c5:
    max_runtime = st.number_input("Max model runtime (s)", 0.0, 1e6, 0.0, key="pl_maxrt",
                                  help="0 = rule off")

mets = e["metrics_df"].set_index("model")
runtimes = {r.model: r.runtime_s for r in E.model_status_table(e["fc_long"]).itertuples()}
rules = pd.DataFrame(index=models_ok)
rules["mean total cost"] = grid.groupby("model")["total_cost"].mean()
rules["mean service"] = grid.groupby("model")["service_level"].mean()
rules["MASE"] = mets["MASE"]
rules["mean avg inventory"] = grid.groupby("model")["average_inventory"].mean()
rules["runtime s"] = pd.Series(runtimes)
rules["PASS_bool"] = (
    ((rules["mean total cost"] <= max_cost) if max_cost > 0 else True)
    & ((rules["mean service"] >= min_service) if min_service > 0 else True)
    & ((rules["MASE"] <= max_mase) if max_mase > 0 else True)
    & ((rules["mean avg inventory"] <= max_inv) if max_inv > 0 else True)
    & ((rules["runtime s"] <= max_runtime) if max_runtime > 0 else True)
)
rules["PASS"] = np.where(rules["PASS_bool"], "PASS", "FAIL")
rules = rules.drop(columns=["PASS_bool"])
styled = rules.round(3).style.map(
    lambda v: "background-color: rgba(61,123,85,.18); color: #3D7B55; font-weight:700"
    if v == "PASS" else
    ("background-color: rgba(194,91,100,.15); color: #C25B64; font-weight:700" if v == "FAIL" else ""),
    subset=["PASS"])
st.dataframe(styled, use_container_width=True)
passing = rules[rules["PASS"] == "PASS"].index.tolist()
if passing:
    winner = rules.loc[passing, "mean total cost"].idxmin()
    st.markdown(f'<span class="badge" style="border-color:rgba(61,123,85,.6);color:#3D7B55;">'
                f'<span class="dot"></span>WINNER UNDER YOUR CONSTRAINTS · {winner}</span>',
                unsafe_allow_html=True)
else:
    st.markdown('<span class="badge" style="border-color:rgba(194,91,100,.6);color:#C25B64;">'
                '<span class="dot"></span>NO MODEL PASSES — relax a rule</span>', unsafe_allow_html=True)

insight_panel(
    f"<b>{win_counts.idxmin()}</b> wins only {win_counts.min()} of {len(cells)} cells; "
    f"<b>{win_counts.idxmax()}</b> wins {win_counts.max()}." if len(win_counts) else "",
    "Policy robustness is a property of the model, not a given. The Decision Center reads "
    "these results under your declared objective.",
    tone="live",
)
lab_footer("Next → Decision Center: five winners, five answers.")
