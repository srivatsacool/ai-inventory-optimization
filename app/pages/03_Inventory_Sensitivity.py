"""Page 3 - Inventory Cost / Sensitivity. INTERACTIVE / DERIVED.

Shows the compact 27-policy sensitivity grid from app_data/ (derived copy of
the local sensitivity run). The frozen claim stays on the Frozen Results page;
here the visitor interrogates how the winner moves across policies.
"""

import streamlit as st

from app.lib import appdata_loader as A

st.title("Inventory Cost / Sensitivity")
st.caption("INTERACTIVE LAB - derived 27-policy grid copy. Default frozen policy: L7 / 95% / H=1 / P=5.")

status = A.check_all_present()
if not status.get("sensitivity_compact.csv"):
    st.warning("app_data/sensitivity_compact.csv missing. Run: python scripts/build_app_data.py")
    st.stop()

grid = A.load_sensitivity_compact()
if grid.empty:
    st.error("Sensitivity grid is empty.")
    st.stop()

dataset = st.selectbox("Dataset", sorted(grid["dataset"].unique().tolist()))
g = grid[grid["dataset"] == dataset]

lt = st.selectbox("Lead time", sorted(g["lead_time"].unique().tolist()))
sv = st.selectbox("Service target", sorted(g["service_target"].unique().tolist()))
px = st.selectbox("Stockout penalty P (H=1)", sorted(g["P"].unique().tolist()))
cell = g[(g["lead_time"] == lt) & (g["service_target"] == sv) & (g["P"] == px)].sort_values("total_cost")
st.subheader(f"Cheapest model at L={lt} svc={sv} P={px}: {cell.iloc[0]['model']} ({cell.iloc[0]['total_cost']:.2f})")
st.dataframe(cell, use_container_width=True)

st.subheader("Policy wins (derived copy)")
wins = grid.groupby(["dataset", "model"]).size().reset_index(name="policies_cheapest")
st.dataframe(wins.sort_values(["dataset", "policies_cheapest"], ascending=[True, False]), use_container_width=True)
