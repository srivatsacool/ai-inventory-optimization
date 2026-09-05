"""Page 4 - METHODOLOGY. The frozen protocol as a visual pipeline.

Content sources are tracked at v1.0-evidence-freeze (protocol doc, decision
log, number sheet). No prose walls: each stage is a compact module.
"""

import streamlit as st

from lib import frozen_loader as F
from lib.lab import (
    badges, flow_diagram, glossary, inject_theme, lab_footer, meta_rail,
)

inject_theme()
badges(("Frozen protocol", "frozen"), ("Tracked sources only", "dim"), ("v1.0", "ver"))
st.title("Methodology")
st.markdown(
    '<p class="sub" style="color:#9AA4B5;font-size:15px;max-width:880px;margin-top:2px;">'
    'The research protocol as an instrument: eight stages, in order, with the locks '
    'that make every number reproducible.</p>',
    unsafe_allow_html=True,
)

STAGES = [
    ("Data", "500 M5 series (sparse, 64.5% zeros) + 500 Store-Item-Demand series (dense, 0.02%). Two deliberately different demand environments.",
     ["02_data audits", "seed 42"]),
    ("Exploration", "EDA establishes what each environment actually looks like: intermittency, seasonality, scale — the reason one dataset cannot stand for the other.",
     ["08_notebooks/03"]),
    ("Preprocessing", "Stratified series selection and leakage-safe feature windows; the frozen split below is the only timeline every model ever sees.",
     ["08_notebooks/04"]),
    ("Forecasting", "Twelve approaches on the ladder: Naive, Seasonal Naive, MA, SES, DES, TES, ARIMA, SARIMA (Store only, full-500), Croston / SBA / TSB (M5 only), LSTM. 8 rolling origins × 28-day horizon.",
     ["112,000 forecasts / model-dataset"]),
    ("Forecast evaluation", "MAE · RMSE · sMAPE · MASE on identical evaluation periods, plus 91 paired statistical comparisons with validation gates.",
     ["number sheet 188 rows"]),
    ("Inventory simulation", "One common daily-review order-up-to policy with lost sales for every model: L7 · 95% · H=1 · P=5. Gaps come from forecasts, never from policy tuning.",
     ["06_results/inventory"]),
    ("Robustness", "27-policy sensitivity grid — lead time {3,7,14} × service {.90,.95,.99} × penalty {3,5,10}. The thesis is stress-tested, not cherry-picked.",
     ["LSTM: 25/27 M5 cells"]),
    ("Final comparison", "Forecast quality, decision outcome, and cost composed into the published thesis — locked as the evidence freeze.",
     ["tag v1.0-evidence-freeze"]),
]

flow_diagram([(t, "") for t, _, _ in STAGES], last_highlight=True, compact=True)
st.caption("Each stage expands below. LLM: designed (11_src/llm_experiment_design.md), not executed — no LLM number exists anywhere in this study.")

for i, (t, d, tags) in enumerate(STAGES, 1):
    with st.expander(f"{i:02d} · {t}"):
        st.markdown(f'<div class="gloss" style="font-size:14px;">{d}</div>', unsafe_allow_html=True)
        st.markdown(" ".join(f'<span class="badge" style="border-radius:4px;">{x}</span>' for x in tags), unsafe_allow_html=True)

st.subheader("Temporal integrity")
meta_rail([
    ("Train", "2013-01-01 → 2015-10-31", "1,034 days"),
    ("Validation", "2015-11-01 → 2016-02-29", "121 d · leap-day corrected"),
    ("Test", "2016-03-01 → 2016-05-22", "83 d · 8 origins · H28"),
    ("Seed", "42", "everywhere"),
    ("Boundary", "history < origin", "leakage-safe"),
], cols=5)

st.subheader("The frozen boundary")
st.markdown(
    '<div class="insight"><div class="h">Why pages 01 and 02–03 look different</div>'
    '<div class="w"><b>Frozen evidence</b> (amber) is read-only, loaded through '
    '<code>app.lib.frozen_loader</code> from files tracked at tag <code>v1.0-evidence-freeze</code>, '
    'and thesis-verified on every page load.<br><b>Interactive analysis</b> (blue) derives from '
    '<code>app_data/</code> small extracts and is labeled on every module it produces. '
    'One never overwrites the other.</div></div>',
    unsafe_allow_html=True,
)

st.subheader("Protocol provenance")
st.markdown(
    '<div class="gloss">docs/research/experiment-protocol.md is the study\'s v1.0 experiment constitution '
    '(2026-08-22): temporal integrity, fair comparison, one common inventory policy, neutral reporting. '
    'Its v1.0 numeric lockings were voided by the 2026-08-27 reset and re-decided through EDA, literature, '
    'validation, and feasibility — recorded in 00_project/decisions.md (leap-day correction, SARIMA full-500, '
    'Croston benchmark, leakage-safe protocol).</div>',
    unsafe_allow_html=True,
)
ok = F.verify_thesis()
st.success("Thesis lock verified live: " + " · ".join(
    f"{k.split('-', 1)[1]}={v['got']:.4f}" for k, v in ok.items() if v.get("ok")) + f" ({sum(v.get('ok') for v in ok.values())}/{len(ok)} rows)")

glossary("MASE", "Common policy", "Intermittent demand", "Dense demand")
lab_footer("Loop closed: return to 01 Frozen Results — now you know exactly what those numbers are.")
