"""Page 10 - EXPERIMENTS. Run log with provenance; scenario winner tracking.

Every sandbox run is stamped: Experiment ID, dataset, series, horizon, policy,
models, timestamp, configuration. The frozen benchmark is never written.
"""

import pandas as pd
import streamlit as st

from lib import state
from lib.lab import (
    badges, empty_state, hero, inject_theme, insight_panel, lab_footer,
    meta_rail, section_head,
)

inject_theme()
state.sandbox_badges()
hero("Experiments",
     "The sandbox lab notebook. Every applied configuration is a logged run with full "
     "provenance — replayable, comparable, and clearly separated from the frozen benchmark.")
log = st.session_state.get("run_log", [])
if not log:
    empty_state("No runs yet — apply a configuration in Data Studio (or change a policy knob "
                "in the Inventory Simulator) and the run will appear here.")
    st.stop()

# ---------------------------------------------------------------------------
section_head("Run log", f"{len(log)} sandbox run(s) this session")
rows = []
for r in log:
    w = r["winners"]
    rows.append({
        "Experiment ID": r["experiment_id"],
        "timestamp": r["timestamp"],
        "mode": r["mode"],
        "dataset": r["dataset"],
        "series": r["series_id"][:30],
        "origin": r["origin_date"] if isinstance(r["origin_date"], str) else str(r["origin_date"])[:10],
        "H": r["horizon"],
        "scenario": r["scenario"] or "—",
        "models": len(r["models"]),
        "policy": f'L{r["policy"]["lead_time"]}·{r["policy"]["service_target"]:.0%}·P{r["policy"]["P"]:g}',
        "best forecaster": w.get("best_forecaster", "—"),
        "lowest cost": w.get("lowest_cost", "—"),
        "highest service": w.get("highest_service", "—"),
        "min cost": w.get("total_cost", "—"),
    })
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
st.caption("Mode is always SANDBOX for these runs — the frozen SIRP evidence (v1.0-evidence-freeze) "
           "is never modified, never overwritten, and always thesis-verified on the Research "
           "Benchmark page.")

# ---------------------------------------------------------------------------
section_head("Scenario tracking", "How the winner changes")
if len(log) >= 2:
    base = log[-1]  # earliest run
    cur = log[0]    # most recent
    st.markdown("**First run in this session → current run**")
    chg = []
    for k in ("best_forecaster", "lowest_cost", "highest_service", "lowest_inventory"):
        a, b = base["winners"].get(k, "—"), cur["winners"].get(k, "—")
        chg.append({"objective": k, "first run": a, "current run": b,
                    "changed": "→" if a != b else "="})
    st.dataframe(pd.DataFrame(chg), use_container_width=True, hide_index=True)
    if any(c["changed"] == "→" for c in chg):
        insight_panel(
            "<b>The winner changed.</b> Same models, same engine — different demand or policy. "
            "This is the scenario engine at work: spike, drop, volatility, intermittency, "
            "lead time, service target, P/H ratio — each re-runs the whole chain.",
            tone="live")
    else:
        st.caption("Winners so far are stable across your runs. Change a scenario in Data "
                   "Studio or a policy knob in the Simulator to stress them.")
else:
    st.caption("One run logged. Apply a scenario or change policy to compare runs here.")

# ---------------------------------------------------------------------------
section_head("Latest run provenance", "Full configuration")
p = log[0]
meta_rail([
    ("Experiment ID", p["experiment_id"], "sandbox"),
    ("Dataset · series", f'{p["dataset"]} · {p["series_id"][:24]}', "source config"),
    ("Horizon · origin", f'{p["horizon"]} d', str(p["origin_date"])[:10]),
    ("Models", f'{len(p["models"])}', ", ".join(p["models"][:4]) + ("…" if len(p["models"]) > 4 else "")),
    ("Policy", f'L{p["policy"]["lead_time"]} · {p["policy"]["service_target"]:.0%} · H=1 · P={p["policy"]["P"]:g}', "order-up-to"),
], cols=5)
with st.expander("Raw provenance (latest run)"):
    st.json(p, expanded=True)
st.caption("Provenance convention: every sandbox number on every page can be traced to a "
           "run here; frozen numbers trace to 09_reports/final/data/final_number_sheet.csv "
           "and the v1.0-evidence-freeze tag.")

lab_footer("Next → Research/Methodology: what the sandbox may and may not touch.")
