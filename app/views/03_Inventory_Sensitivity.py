"""Page 3 - INVENTORY LAB. Interactive what-if laboratory.

All dynamic values derive from app_data/sensitivity_compact.csv (the 27-policy
grid copy) and are labeled INTERACTIVE SENSITIVITY. The frozen default cell
(L7 / 95% / P=5) is shown for contrast only, read-only via frozen_loader.
"""

import pandas as pd
import streamlit as st

from lib import appdata_loader as A
from lib import frozen_loader as F
from lib.lab import (
    FROZEN, MUTED, STEEL_L, TEAL, TEAL_L, VIOLET_L, WARNING, WHITE,
    badges, chart_panel, empty_state, fig_base, glossary, hero, inject_theme,
    insight_panel, kpi_strip, lab_footer, meta_rail, mono_annotation, section_head,
)

inject_theme()
badges(("Interactive / Experimental", "live"), ("Sensitivity · not published result", "dim"), ("v1.0", "ver"))
hero("Inventory Lab",
     "The what-if laboratory: move lead time, service target, and stockout penalty, "
     "and watch which model wins the decision. A winner under one assumption may not "
     "remain a winner under another.")

if not A.check_all_present().get("sensitivity_compact.csv"):
    empty_state("app_data/sensitivity_compact.csv missing. Run <code>python scripts/build_app_data.py</code>.")
    st.stop()
grid = A.load_sensitivity_compact()
if grid.empty:
    empty_state("Sensitivity grid is empty.")
    st.stop()

FROZEN_CELL = {"lead_time": 7, "service_target": 0.95, "P": 5}
DS = {"m5": "M5 · sparse demand", "store_item_demand": "Store · dense demand"}

# ---------- one experiment surface: controls beside the chart (DESIGN.md §12) ----------
section_head("Experiment", "What wins under your policy?")
ctrl, main_col = st.columns([1, 2.15], gap="medium")
with ctrl:
    st.markdown("#### Scenario controls")
    ds = st.selectbox("Dataset", list(DS.keys()), format_func=lambda d: DS[d], key="il_ds")
    g = grid[grid["dataset"] == ds]
    lt = st.select_slider("Lead time (days)", sorted(g["lead_time"].unique().tolist()), value=7, key="il_lt")
    sv = st.select_slider("Service target", sorted(g["service_target"].unique().tolist()), value=0.95,
                          format_func=lambda v: f"{v:.0%}", key="il_sv")
    px = st.select_slider("Stockout penalty P (H=1)", sorted(g["P"].unique().tolist()), value=5, key="il_px")
    st.caption("Holding cost H = 1/day is the normalization constant of the whole study — it is not a free slider.")
    is_frozen = lt == FROZEN_CELL["lead_time"] and sv == FROZEN_CELL["service_target"] and px == FROZEN_CELL["P"]
    st.markdown(
        f'<div class="badge {"frozen" if is_frozen else "live"}" style="margin-top:6px;">'
        f'<span class="dot"></span>{"Frozen default cell" if is_frozen else "Interactive sensitivity"}</div>',
        unsafe_allow_html=True,
    )

with main_col:
    cell = g[(g["lead_time"] == lt) & (g["service_target"] == sv) & (g["P"] == px)].sort_values("total_cost")
    if cell.empty:
        empty_state("No rows for this cell.")
        st.stop()
    w = cell.iloc[0]
    st.markdown(
        f'<div class="lab-scenario"><div class="w"><b>{w["model"]}</b> · cost <b>{w["total_cost"]:.2f}</b>'
        + (" — reproduces the published frozen claim." if is_frozen
           else " — an interactive scenario, not the published result.") + "</div>"
        + f'<div class="ctx">L={lt} · SERVICE {sv:.0%} · P={px} · H=1 · {DS[ds]}</div></div>',
        unsafe_allow_html=True,
    )

    # cost-vs-service scatter across the whole grid for context
    fig = fig_base(height=560)
    for i, m in enumerate(sorted(cell["model"].unique().tolist())):
        pts = grid[(grid["dataset"] == ds) & (grid["model"] == m)]
        fig.add_scatter(x=pts["total_cost"], y=pts["service_level"], mode="markers", name=m,
                        marker=dict(size=8, color=[STEEL_L, TEAL_L, VIOLET_L, "#B8956A", "#7FBDE6",
                                                   "#9AA4B5", "#6FA88F", "#5F7A9E", "#C78B94", "#7C8AA0",
                                                   "#93A7C4"][i % 11], opacity=.8))
    fig.add_scatter(x=[w["total_cost"]], y=[w["service_level"]], mode="markers", name="this cell winner",
                    marker=dict(size=16, color=TEAL, line=dict(width=2, color=WHITE)),
                    hovertemplate=f"{w['model']}<br>cost {w['total_cost']:.2f}<extra></extra>")
    fig.update_layout(
        title=dict(text="All 27 policies · cost vs achieved service · lower-left is better", font=dict(size=16, color=WHITE), x=.01),
        xaxis_title="Total cost (H=1 units)", yaxis_title="Fill rate",
        legend=dict(orientation="h", y=-0.28),
    )
    chart_panel(fig, "", "One dot per policy cell. The teal marker is the winner under the current scenario.")

# ---------- metric rail + composition ----------
section_head("Scenario outcome", "What the winning cell costs")
kpi_strip([
    ("Total cost", f"{w['total_cost']:.2f}", "lower better"),
    ("Holding", f"{w['holding_cost']:.2f}", "H=1 units"),
    ("Stockout", f"{w['shortage_cost']:.2f}", "P=" + str(px)),
    ("Service level", f"{w['service_level']:.1%}", "fill rate"),
], cols=4)
fig2 = fig_base(height=460)
ordered = cell.sort_values("total_cost")
fig2.add_bar(y=ordered["model"], x=ordered["holding_cost"], orientation="h", name="Holding",
             marker=dict(color=STEEL_L, opacity=.9), hovertemplate="holding %{x:.2f}<extra></extra>")
fig2.add_bar(y=ordered["model"], x=ordered["shortage_cost"], orientation="h", name="Stockout",
             marker=dict(color=WARNING, opacity=.9), hovertemplate="stockout %{x:.2f}<extra></extra>")
fig2.update_layout(barmode="stack",
                   title=dict(text="Cost composition per model · this cell", font=dict(size=16, color=WHITE), x=.01),
                   xaxis_title="Cost (H=1 units)", legend=dict(x=1.0, y=0))
chart_panel(fig2, "", "Blue = holding cost (order too much); amber = stockout cost (order too little). Winners sit where both stay low.")

# ---------- scenario comparison ----------
section_head("Scenario comparison", "Baseline policy vs compared policy")
base, comp = st.columns([1.6, 1])
with comp:
    clt = st.select_slider("Compare: lead time", sorted(g["lead_time"].unique().tolist()), value=14, key="cmp_lt")
    csv = st.select_slider("Compare: service", sorted(g["service_target"].unique().tolist()), value=0.95, format_func=lambda v: f"{v:.0%}", key="cmp_sv")
    cpx = st.select_slider("Compare: P", sorted(g["P"].unique().tolist()), value=5, key="cmp_px")
c1 = g[(g["lead_time"] == lt) & (g["service_target"] == sv) & (g["P"] == px)]
c2 = g[(g["lead_time"] == clt) & (g["service_target"] == csv) & (g["P"] == cpx)]
merged = c1[["model", "total_cost"]].merge(c2[["model", "total_cost"]], on="model", suffixes=("_cur", "_cmp"))
merged["delta"] = merged["total_cost_cmp"] - merged["total_cost_cur"]
merged = merged.sort_values("delta")
with base:
    fig3 = fig_base(height=max(260, 30 * len(merged) + 70))
    fig3.add_bar(x=merged["delta"], y=merged["model"], orientation="h",
                 marker_color=[TEAL if d < 0 else WARNING for d in merged["delta"]], width=.6,
                 hovertemplate="%{y}<br>Δ cost %{x:.2f}<extra></extra>")
    fig3.add_vline(x=0, line_color=MUTED, line_width=1)
    fig3.update_layout(
        title=dict(text="Cost change vs current cell · teal = cheaper",
                   font=dict(size=15, color=WHITE), x=.01),
        xaxis_title="Δ total cost")
    chart_panel(fig3, "", f"Compared L{clt}·{csv:.0%}·P{cpx} against current L{lt}·{sv:.0%}·P{px}. "
                          "Read: moving right means the compared policy is more expensive for that model.")

# ---------- policy robustness ----------
section_head("Robustness", "Who wins across all 27 policies?")
CELL_KEYS = ["dataset", "lead_time", "service_target", "P"]
winners = grid.loc[grid.groupby(CELL_KEYS)["total_cost"].idxmin()]
wins = winners.groupby(["dataset", "model"]).size().reset_index(name="policies_won")
w1, w2 = st.columns(2)
for col, (ds2, label) in zip([w1, w2], [("m5", "M5"), ("store_item_demand", "Store")]):
    with col:
        wt = wins[wins["dataset"] == ds2].sort_values("policies_won", ascending=False)
        fig4 = fig_base(height=max(220, 30 * len(wt) + 60))
        fig4.add_bar(x=wt["policies_won"], y=wt["model"], orientation="h",
                     marker_color=[TEAL if i == 0 else "#22304A" for i in range(len(wt))], width=.6,
                     hovertemplate="%{y}<br>%{x:.0f} of 27 cells<extra></extra>")
        fig4.update_layout(title=dict(text=f"{label} · policies won (of 27)", font=dict(size=15, color=WHITE), x=.01),
                           xaxis_title="Cells won", xaxis_range=[0, 27])
        chart_panel(fig4, "", "Frozen robustness finding: LSTM takes 25 of 27 M5 cells — this grid lets you feel it out.",
                    tag=("Derived grid", "live"))

# ---------- contrast with frozen truth ----------
try:
    inv = F.load_inventory_by_model()
    frozen_w = inv.loc[inv.groupby("dataset")["total_cost"].idxmin()].set_index("dataset")
    meta_rail([
        ("Frozen · M5 winner", f"{frozen_w.loc['m5', 'model']} @ {frozen_w.loc['m5', 'total_cost']:.2f}", "L7 / 95% / P=5"),
        ("Frozen · Store winner", f"{frozen_w.loc['store_item_demand', 'model']} @ {frozen_w.loc['store_item_demand', 'total_cost']:.2f}", "L7 / 95% / P=5"),
        ("Your scenario winner", f"{w['model']} @ {w['total_cost']:.2f}", f"L{lt} / {sv:.0%} / P={px}"),
        ("Same as frozen?", "Yes — default cell" if is_frozen else "No — experimental", "never overwrites evidence"),
    ], cols=4)
    st.caption("Frozen default cell L7 · 95% · P=5 — reference only. Your scenario never overwrites it.")
except Exception as e:
    st.warning(f"Frozen contrast rail unavailable: {e}")

insight_panel(
    "Moving a slider changes <i>who wins</i> — it never changes the frozen page.",
    "The published thesis (Frozen Results) was decided at L7 · 95% · P=5. The grid shows the thesis is robust across the other 26 cells; "
    "exploring outside the grid is out of evidence scope, and the Lab says so instead of guessing.",
    tone="live",
)

glossary("Inventory cost", "Service level", "Common policy")
lab_footer("Next → 04 Methodology: the protocol that produced every number on these pages.")
