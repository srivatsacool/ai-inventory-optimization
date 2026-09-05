"""Page 1 - FROZEN RESULTS. Chart-first overview of published evidence.

Read-only: every number arrives via app.lib.frozen_loader from files tracked
at tag v1.0-evidence-freeze. Nothing here recomputes or reinterprets. The one
derived element (the origin-1 forecast-vs-actual illustration) is labeled.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from app.lib import frozen_loader as F
from app.lib.lab import (
    FROZEN, STEEL, STEEL_L, TEAL, TEAL_L, INDIGO_L, MUTED, WHITE,
    badges, meta_rail, metric_card, chart_panel, insight_panel, flow_diagram,
    glossary, inject_theme, lab_footer, fig_base, mono_annotation, empty_state,
)

inject_theme()
badges(("Locked / Published", "frozen"), ("Evidence · read only", "dim"), ("v1.0", "ver"))
st.title("Frozen Results")
st.markdown(
    '<p class="sub" style="color:#9AA4B5;font-size:15px;max-width:880px;margin-top:2px;">'
    'Forecast accuracy and inventory performance from the final verified research run — '
    'nothing on this page is recomputed. Interrogate the "why" in the interactive sections.</p>',
    unsafe_allow_html=True,
)
meta_rail([
    ("Train", "2013-01-01 → 2015-10-31", "1,034 days"),
    ("Validation", "2015-11-01 → 2016-02-29", "121 d · incl. leap day"),
    ("Test", "2016-03-01 → 2016-05-22", "83 d · 8 origins · H28"),
    ("Dataset", "M5 + Store", "500 series each · seed 42"),
    ("Policy", "L7 · 95% · H=1 · P=5", "common policy, all models"),
], cols=5)
ok = {k: v for k, v in F.verify_thesis().items()}
missing = [k for k, v in F.check_all_present().items() if not v]
if missing:
    st.error(f"Missing frozen files: {missing}. Run from repo root.")
    st.stop()
if not all(v.get("ok") for v in ok.values()):
    st.error(f"Thesis verification FAILED: {ok}")
    st.stop()

try:
    inv = F.load_inventory_by_model()
    ns = F.load_number_sheet()
except Exception as e:
    st.error(f"Could not load frozen evidence: {e}")
    st.stop()

DS = {"m5": "M5", "store_item_demand": "Store"}
mase = ns[ns["metric"] == "MASE"]
fc_win = mase.loc[mase.groupby("dataset")["value"].idxmin()].set_index("dataset")
inv_win = inv.loc[inv.groupby("dataset")["total_cost"].idxmin()].set_index("dataset")
store_lstm = float(inv.loc[(inv["dataset"] == "store_item_demand") & (inv["model"] == "LSTM"), "total_cost"].iloc[0])

# ---------- thesis in numbers ----------
st.subheader("Thesis in numbers")
c1, c2, c3, c4 = st.columns(4)
metric_card(c1, "M5 · forecast quality", fc_win.loc["m5", "model"], f"{fc_win.loc['m5', 'value']:.3f}", "MASE · lower is better",
            "Lowest forecast error on sparse, intermittent demand.")
metric_card(c2, "Store · forecast quality", fc_win.loc["store_item_demand", "model"], f"{fc_win.loc['store_item_demand', 'value']:.3f}", "MASE · lower is better",
            "Lowest forecast error on dense, smooth demand.")
metric_card(c3, "M5 · inventory performance", inv_win.loc["m5", "model"], f"{inv_win.loc['m5', 'total_cost']:.2f}", "simulated cost · lower is better",
            "Lowest simulated inventory cost under the common policy.")
metric_card(c4, "Store · inventory performance", inv_win.loc["store_item_demand", "model"], f"{inv_win.loc['store_item_demand', 'total_cost']:.2f}", "simulated cost · lower is better",
            "Lowest simulated inventory cost under the common policy.")
glossary("MASE", "Inventory cost")

# ---------- charts A/B: model ranking ----------
ds_pick = st.segmented_control("Demand environment", ["M5", "Store"], default="M5", key="fr_ds") or "M5"
ds_key = "m5" if ds_pick == "M5" else "store_item_demand"
rank = mase[mase["dataset"] == ds_key].sort_values("value")
fig = fig_base(height=max(300, 34 * len(rank) + 90))
colors = [TEAL if m == rank["model"].iloc[0] else STEEL_L for m in rank["model"]]
fig.add_bar(x=rank["value"], y=rank["model"], orientation="h", marker_color=colors, width=.62,
            hovertemplate="%{y}<br>MASE %{x:.4f}<extra></extra>")
fig.update_layout(
    title=dict(text=f"MASE by model · lower is better — {ds_pick}", font=dict(size=16, color=WHITE), x=.01),
    xaxis_title="MASE",
)
fig.add_annotation(mono_annotation(rank["value"].iloc[0], 0.6, "winner", color=TEAL_L, xanchor="left"))
chart_panel(fig, "", "Frozen forecast accuracy over 500 series × 8 origins, test window only.")

# ---------- chart D: forecast vs inventory outcome ----------
st.subheader("Forecast winner ≠ inventory winner")
fig2 = fig_base(height=430)
for i, (ds, label) in enumerate([("m5", "M5 · sparse"), ("store_item_demand", "Store · dense")]):
    sub = inv[inv["dataset"] == ds].sort_values("total_cost")
    fig2.add_bar(
        x=sub["total_cost"], y=sub["model"], orientation="h", legendgroup=ds, name=label,
        marker_color=[TEAL if m == inv_win.loc[ds, "model"] else (INDIGO_L if m == fc_win.loc[ds, "model"] else "#22304A") for m in sub["model"]],
        offsetgroup=i, width=.42,
        hovertemplate=f"{label}<br>%{{y}}<br>cost %{{x:.2f}}<extra></extra>",
    )
fig2.update_layout(
    title=dict(text="Simulated inventory cost by model · lower is better", font=dict(size=16, color=WHITE), x=.01),
    xaxis_title="Total cost (holding units, H=1)", barmode="group", legend=dict(x=1.0, y=1),
)
fig2.add_annotation(mono_annotation(0.5, -0.5, "teal = inventory winner · indigo = forecast winner", color=MUTED,
                                    xref="paper", yref="paper", xanchor="center"))
chart_panel(fig2, "", "Same models, same windows, one common policy. On Store demand the indigo forecast winner is not the teal inventory winner.",
            tag=("Frozen evidence", "frozen"))

insight_panel(
    "<b>LSTM wins forecast quality on both environments</b> (MASE "
    f"{fc_win.loc['m5', 'value']:.3f} / {fc_win.loc['store_item_demand', 'value']:.3f}), "
    "but on Store demand <b>Moving Average wins inventory cost</b> "
    f"({inv_win.loc['store_item_demand', 'total_cost']:.2f} vs LSTM {store_lstm:.2f}).",
    "Inventory performance depends on how forecast <i>behavior</i> interacts with the common policy — "
    "uncertainty, lead time, service level, and cost structure — not on point accuracy alone. A smoother, "
    "slightly less accurate forecast can order more economically.",
)

flow_diagram([
    ("Forecast quality", "MASE · MAE · RMSE · sMAPE measured on identical test windows"),
    ("Forecast behavior", "level, noise, and bias each model feeds forward"),
    ("Common inventory policy", "daily-review order-up-to · L7 · 95% · H=1 · P=5 · lost sales"),
    ("Simulated inventory outcome", "holding + stockout cost · fill rate · average inventory"),
])

# ---------- supporting tables + figures ----------
st.subheader("Exact evidence — audit view")
SHOW = ["model", "total_cost", "total_holding_cost", "total_stockout_cost", "service_level", "average_inventory"]
t1, t2 = st.columns(2)
for col, (ds, label) in zip([t1, t2], [("m5", "M5"), ("store_item_demand", "Store Item Demand")]):
    with col:
        tab = inv[inv["dataset"] == ds].sort_values("total_cost")[SHOW].round(2)
        st.dataframe(tab, use_container_width=True, hide_index=True)
        st.caption(f"{label} · cheapest: {tab.iloc[0]['model']} at {tab.iloc[0]['total_cost']:.2f} · mean of 500 series × 8 origins")
with st.expander("Frozen published figures (tracked PNGs)"):
    st.image(str(F.frozen_path("fig_cost")), caption="Total cost comparison — 07_figures/inventory", use_container_width=True)
    st.image(str(F.frozen_path("fig_service")), caption="Service level comparison — 07_figures/inventory", use_container_width=True)
    st.image(str(F.frozen_path("fig_leaderboard")), caption="Combined MASE leaderboard — 09_reports/final/figures", use_container_width=True)
with st.expander("Thesis lock — exact number-sheet rows"):
    st.dataframe(
        ns[ns["metric_id"].isin(list(F.THESIS_ROWS))][["metric_id", "dataset", "model", "metric", "value", "units"]],
        use_container_width=True, hide_index=True,
    )
    st.caption("Verified against 09_reports/final/data/final_number_sheet.csv on every load (7 rows).")

lab_footer("Next → 02 Forecast Explorer: interrogate model behavior series by series.")
