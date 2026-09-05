"""Page 1 - FROZEN RESULTS. Read-only, tracked evidence only.

No recomputation, no reinterpretation. Every number comes from files tracked
at tag v1.0-evidence-freeze via app.lib.frozen_loader.
"""

import streamlit as st

from app.lib import frozen_loader as F

st.title("Frozen Results - published evidence")
st.caption("READ-ONLY. Source: tag v1.0-evidence-freeze. Nothing on this page is recomputed.")
st.info(F.THESIS_TEXT)

present = F.check_all_present()
missing = [k for k, ok in present.items() if not ok]
if missing:
    st.error(f"Missing frozen files: {missing}. Run from repo root: streamlit run app/streamlit_app.py")

checks = F.verify_thesis()
bad = {k: v for k, v in checks.items() if not v.get("ok")}
if bad:
    st.error(f"Thesis verification FAILED: {bad}")
else:
    st.success("Thesis lock verified against 09_reports/final/data/final_number_sheet.csv (7 rows).")

st.subheader("Inventory cost by model - default policy L7 / 95% / H=1 / P=5")
try:
    inv = F.load_inventory_by_model()
    st.dataframe(inv, use_container_width=True)
    m5 = inv[inv["dataset"] == "m5"].sort_values("total_cost")
    st.write(f"M5 cheapest frozen: {m5.iloc[0]['model']} at {m5.iloc[0]['total_cost']:.2f}")
    st_ = inv[inv["dataset"] == "store_item_demand"].sort_values("total_cost")
    st.write(f"Store cheapest frozen: {st_.iloc[0]['model']} at {st_.iloc[0]['total_cost']:.2f}")
except Exception as e:
    st.error(f"Could not load frozen inventory table: {e}")

st.subheader("Frozen figures")
for key, label in [
    ("fig_cost", "Total cost comparison (tracked 07_figures/inventory)"),
    ("fig_service", "Service level comparison (tracked 07_figures/inventory)"),
    ("fig_leaderboard", "Combined MASE leaderboard (tracked 09_reports/final/figures)"),
]:
    p = F.frozen_path(key)
    if p.exists():
        st.image(str(p), caption=label, use_container_width=True)
    else:
        st.warning(f"Frozen figure missing: {p}")

st.subheader("Number sheet excerpt - thesis rows")
try:
    ns = F.load_number_sheet()
    st.dataframe(ns[ns["metric_id"].isin(list(F.THESIS_ROWS))], use_container_width=True)
except Exception as e:
    st.error(f"Could not load number sheet: {e}")
