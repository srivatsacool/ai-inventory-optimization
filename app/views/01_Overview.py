"""AI Inventory Optimization Lab — Overview.

Explains the two-mode design (frozen Research Benchmark vs interactive
Sandbox), the forecast → inventory chain, and how to drive a live demo.
"""

import streamlit as st

from lib.lab import (
    badges, flow_diagram, glossary, hero, inject_theme, insight_panel,
    lab_footer, meta_rail, section_head, thesis_statement,
)

inject_theme()
badges(("Interactive Lab", "live"), ("Frozen benchmark read-only", "frozen"), ("SIRP v1.0", "ver"))
hero("AI Inventory Optimization Lab",
     "From forecasts to shelf decisions. Select data, reshape demand, run the full model "
     "ladder, and watch every forecast become safety stock, orders, cost and service — "
     "step by step, live.")

thesis_statement(
    "Forecast quality and inventory value are <b>not the same thing</b>. "
    "This lab lets you prove it on any series: change demand, change policy, "
    "and watch the winner change."
)

section_head("How it works", "Two modes, one engine")
st.markdown(
    '<div class="gloss" style="font-size:14px;">'
    "<b>Research Benchmark</b> (amber) — the frozen SIRP v1.0 evidence, read-only, "
    "thesis-verified on every load. Nothing in the sandbox can touch it.<br>"
    "<b>Interactive Experiment</b> (blue) — your sandbox. Every result is stamped "
    "with an Experiment ID and labeled SANDBOX; the frozen files are never written.</div>",
    unsafe_allow_html=True,
)

section_head("The chain", "Every sandbox run follows the same pipeline")
flow_diagram([
    ("Data Studio", "built-in M5/Store series, CSV upload, edits, demand scenarios"),
    ("Forecast Lab", "12-model ladder on your modified series · leakage-free"),
    ("Model Arena", "MAE · RMSE · MASE · RMSSE · WAPE · sMAPE · runtime"),
    ("Inventory Simulator", "forecast → σ → safety stock → order-up-to → daily simulation"),
    ("Policy Lab", "27-policy grid or custom · winner matrix · your constraints"),
    ("Decision Center", "five winners, never collapsed into one"),
], last_highlight=False)

section_head("Start here", "Live demo path")
meta_rail([
    ("1 · Data Studio", "pick a series", "or upload a CSV"),
    ("2 · Forecast Lab", "see the ladder run", "metrics per model"),
    ("3 · Inventory Simulator", "open the calc chain", "L · service · H · P"),
    ("4 · Policy Lab", "run the 27-policy grid", "set pass/fail rules"),
    ("5 · Decision Center", "read the five winners", "accuracy ≠ value"),
], cols=5)

section_head("Signature result", "Why this lab exists")
insight_panel(
    "In the frozen benchmark, <b>LSTM</b> is the best forecaster on both datasets, "
    "but <b>Moving Average</b> wins Store inventory cost. The Decision Center and "
    "Diagnostics pages reproduce this <b>Accuracy ≠ Value</b> result live on whatever "
    "series and policy you choose — data-driven, never hard-coded.",
    "Inventory decisions care about forecast <i>behavior</i> (level, noise, bias) under a "
    "policy — not point accuracy alone.",
    tone="live",
)

glossary("MASE", "Inventory cost", "Common policy", "Intermittent demand")
lab_footer("Open Data Studio to begin — every other sandbox page follows your experiment.")
