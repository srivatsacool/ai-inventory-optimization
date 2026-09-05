"""Shared visual system for the Interactive Research Laboratory.

Implements the binding contract in AI_Inventory_Optimization_DESIGN.md:
near-black navy lab-bg, four surface levels, hairline borders, the
steel/teal/indigo/violet accent family, Inter + JetBrains Mono, the
frozen-amber vs interactive-blue status system, and the Lab component kit
(MetricCard, ChartPanel, ControlBar, StatusBadge, InsightPanel,
ComparisonPanel, MethodStep, EmptyState, ErrorState).

Research integrity: this module renders; it never computes evidence.
Frozen values must arrive via app.lib.frozen_loader; derived values via
app.lib.appdata_loader, and every caller must label them accordingly.
"""

from typing import Iterable

import streamlit as st

# ---- DESIGN.md section 4 tokens (verbatim hex values) ----
PAPER = "#F4F4F1"
INK = "#161A22"
LAB_BG = "#080C16"
LAB_S1 = "#0E1422"
LAB_S2 = "#131B2B"
LAB_S3 = "#182236"
STEEL = "#35618A"
TEAL = "#27757A"
INDIGO = "#5B56A0"
VIOLET = "#7A53A6"
WHITE = "#F7F8FA"
MUTED = "#8B94A5"
MUTED_SOFT = "#626B7A"
HAIRLINE = "#273246"
SUCCESS = "#48B89A"
WARNING = "#D5A34A"
DANGER = "#D66B73"
INFO = "#6C9DDA"
FROZEN = "#C59B52"
INTERACTIVE = "#4FA6D8"
# lighter display steps of the accent family for dark surfaces (ramps in
# .impeccable/design.json)
STEEL_L = "#4E7BA8"
TEAL_L = "#3F9398"
INDIGO_L = "#7A76B9"
VIOLET_L = "#9673BE"

FONT_UI = "Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
FONT_MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, monospace"

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root { color-scheme: dark; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
p, span, div, label, li, h1, h2, h3, h4, .stMarkdown {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(1000px 420px at 10% -5%, rgba(53,97,138,.14), transparent 60%),
    radial-gradient(900px 380px at 90% -3%, rgba(91,86,160,.10), transparent 60%),
    radial-gradient(1100px 600px at 50% 112%, rgba(39,117,122,.07), transparent 60%),
    #080C16;
  color: #F7F8FA;
}
[data-testid="stSidebar"] { background: #0A0F1B; border-right: 1px solid #273246; }
.block-container { max-width: 1560px; padding-top: 1.1rem; padding-bottom: 3rem; }

h1 { font-size: 34px; line-height: 1.15; font-weight: 650; letter-spacing: -0.02em; color: #F7F8FA; }
h2 { font-size: 24px; line-height: 1.25; font-weight: 650; letter-spacing: -0.015em; color: #F7F8FA; margin-top: 2.2rem; }
h3 { font-size: 16px; line-height: 1.35; font-weight: 650; color: #F7F8FA; }
[data-testid="stCaptionContainer"], .stCaption { color: #8B94A5 !important; font-size: 13px; line-height: 1.5; }
[data-testid="stWidgetLabel"] span { font-size: 11px !important; font-weight: 650; letter-spacing: .12em; text-transform: uppercase; color: #8B94A5 !important; }
p, li, .stMarkdown { color: #C6CEDB; }

::selection { background: rgba(79,166,216,.32); }
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: #0E1422; }
::-webkit-scrollbar-thumb { background: #182236; border: 1px solid #273246; border-radius: 6px; }
::-webkit-scrollbar-thumb:hover { background: #243349; }

/* ---------- status badges (pills are for status tags only) ---------- */
.lab-badges { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin: 2px 0 14px; }
.badge { display: inline-flex; align-items: center; gap: 7px; font-size: 11px; font-weight: 650;
  letter-spacing: .12em; text-transform: uppercase; border-radius: 9999px; padding: 4px 12px;
  border: 1px solid #273246; color: #8B94A5; background: rgba(19,27,43,.65); }
.badge.frozen { border-color: rgba(197,155,82,.5); color: #D8B376; background: rgba(197,155,82,.08); }
.badge.live { border-color: rgba(79,166,216,.55); color: #7FBDE6; background: rgba(79,166,216,.09); }
.badge .dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.badge.ver { margin-left: auto; border: none; color: #626B7A; background: none; letter-spacing: .06em; }

/* ---------- hero + thesis statement ---------- */
.lab-hero { margin: 2px 0 4px; }
.lab-hero .sub { color: #9AA4B5; font-size: 15px; line-height: 1.55; max-width: 860px; }
.lab-thesis { font-size: clamp(23px, 2.6vw, 31px); line-height: 1.32; font-weight: 600;
  letter-spacing: -0.015em; color: #F7F8FA; max-width: 980px; margin: 14px 0 4px; }
.lab-thesis b { color: #FFFFFF; font-weight: 700; }
.lab-thesis .num { font-family: 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace;
  font-weight: 600; letter-spacing: -0.02em; }

/* ---------- section primitives (dividers, not boxes) ---------- */
.lab-sec { margin-top: 2.1rem; }
.lab-kicker { font-size: 11px; font-weight: 650; letter-spacing: .15em; text-transform: uppercase;
  color: #626B7A; margin: 0 0 6px; }
.lab-sec-title { font-size: 24px; line-height: 1.25; font-weight: 650; letter-spacing: -0.015em;
  color: #F7F8FA; margin: 0; }
.lab-sec-sub { font-size: 13px; color: #8B94A5; margin-top: 5px; max-width: 900px; }
.rule { border: none; border-top: 1px solid #273246; margin: 12px 0 0; }

/* ---------- evidence rail (flat mono rows, hairline rules) ---------- */
.lab-rail { display: grid; grid-template-columns: repeat(5, minmax(0,1fr)); gap: 4px 18px;
  margin: 16px 0 4px; border-top: 1px solid #273246; padding-top: 12px; }
.lab-rail.c4 { grid-template-columns: repeat(4, minmax(0,1fr)); }
.rail-cell { background: none; border: none; border-radius: 0; padding: 2px 0; min-width: 0; }
.rail-cell .k { font-size: 10px; font-weight: 650; letter-spacing: .14em; text-transform: uppercase; color: #626B7A; }
.rail-cell .v { font-family: 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; font-size: 12.5px; font-weight: 600; color: #DCE3EE; margin-top: 5px; letter-spacing: -0.01em; }
.rail-cell .s { font-size: 11px; color: #8B94A5; margin-top: 2px; }

/* ---------- metric cards (the single bordered card; flat, top-accented) ---------- */
.mc { background: #0E1422; border: 1px solid #273246; border-top: 2px solid #273246; border-radius: 14px;
  padding: 20px 22px 18px; height: 100%; display: flex; flex-direction: column;
  transition: border-color .2s ease; }
.mc:hover { border-color: #3A4A66; }
.mc.tone-forecast { border-top-color: #5B56A0; }
.mc.tone-inventory { border-top-color: #27757A; }
.mc-k { font-size: 10px; font-weight: 650; letter-spacing: .14em; text-transform: uppercase; color: #8B94A5; }
.mc-model { font-size: 16px; font-weight: 650; color: #F7F8FA; margin-top: 12px; }
.mc-value { font-family: 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace;
  font-size: 48px; line-height: .95; font-weight: 600; color: #F7F8FA; margin-top: 8px; letter-spacing: -0.03em;
  font-variant-numeric: tabular-nums; }
.mc-unit { font-size: 11px; font-weight: 650; letter-spacing: .14em; text-transform: uppercase; color: #8B94A5; margin-top: 10px; }
.mc-note { font-size: 13px; line-height: 1.5; color: #97A1B3; margin-top: 10px; }

/* ---------- figure headers + captions (borderless; the chart is the surface) ---------- */
.fig-head { display: flex; justify-content: space-between; align-items: baseline; gap: 12px;
  margin: 6px 0 2px; }
.fig-title { font-size: 16px; font-weight: 650; color: #F7F8FA; }
.fig-cap { font-size: 13px; line-height: 1.55; color: #8B94A5; margin: 8px 0 0; max-width: 920px; }

/* ---------- insight (borderless + semantic left rule) ---------- */
.insight { background: transparent; border: none; border-left: 2px solid #273246; border-radius: 0;
  padding: 2px 0 2px 18px; margin: 18px 0; max-width: 960px; }
.insight.tone-frozen { border-left-color: #C59B52; }
.insight.tone-live { border-left-color: #4FA6D8; }
.insight .w { font-size: 15px; line-height: 1.55; color: #DCE3EE; }
.insight .w b { color: #F7F8FA; }
.insight .h { font-size: 10px; font-weight: 650; letter-spacing: .14em; text-transform: uppercase; color: #626B7A; margin: 2px 0 6px; }
.insight .why { border-top: 1px solid #273246; margin-top: 14px; padding-top: 12px; }

/* ---------- flow stepper (numbered mono rail, no boxes) ---------- */
.flow { display: flex; align-items: stretch; margin: 16px 0 4px; counter-reset: labstep; }
.flow-node { flex: 1 1 0; background: transparent; border: none; border-top: 1px solid #273246;
  border-radius: 0 !important; padding: 12px 10px 2px 0; margin-right: 14px; min-width: 0; }
.flow-node.hit { border-top-color: rgba(63,147,152,.7); }
.flow.compact .flow-node { padding: 10px 6px 2px 0; margin-right: 8px; }
.flow-node .t { font-size: 12px; font-weight: 650; letter-spacing: .1em; text-transform: uppercase; color: #DCE3EE; }
.flow-node .t::before { counter-increment: labstep; content: "0" counter(labstep);
  display: block; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 11px; font-weight: 600;
  letter-spacing: .08em; color: #626B7A; margin-bottom: 5px; }
.flow.compact .flow-node .t { font-size: 10.5px; letter-spacing: .06em; }
.flow-node .d { font-size: 12.5px; color: #8B94A5; margin-top: 6px; line-height: 1.5; }
.flow-arrow { display: flex; align-items: flex-start; padding: 26px 10px 0 0; color: #3A4A66;
  font-size: 15px; font-weight: 600; }
.flow.compact .flow-arrow { padding: 24px 4px 0 0; font-size: 13px; }

/* ---------- method steps ---------- */
.mstep { display: flex; gap: 16px; padding: 14px 0; border-top: 1px solid #273246; }
.mstep .num { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 12px; font-weight: 600; color: #4FA6D8; min-width: 30px; padding-top: 2px; }
.mstep .body { flex: 1; min-width: 0; }
.mstep .t { font-size: 15px; font-weight: 650; color: #F7F8FA; }
.mstep .d { font-size: 13px; color: #97A1B3; margin-top: 3px; line-height: 1.55; }
.mstep .tags { margin-top: 8px; }
.mstep .tags span { display: inline-block; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 11px;
  color: #B8C2D2; background: #131B2B; border: 1px solid #273246; border-radius: 4px; padding: 2px 8px; margin: 2px 4px 2px 0; }

/* ---------- scenario readout (experiment hero: one number, mono context) ---------- */
.lab-scenario { margin: 2px 0 4px; max-width: 900px; }
.lab-scenario .w { font-size: clamp(22px, 2.4vw, 29px); line-height: 1.3; font-weight: 600;
  letter-spacing: -0.015em; color: #F7F8FA; }
.lab-scenario .w b { color: #FFFFFF; font-weight: 700; }
.lab-scenario .ctx { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 12px; color: #8B94A5;
  margin-top: 6px; letter-spacing: .02em; }

/* ---------- misc ---------- */
.gloss { font-size: 12.5px; color: #97A1B3; line-height: 1.6; margin: 4px 0; }
.gloss b { color: #DCE3EE; }
.empty { background: transparent; border: 1px dashed #273246; border-radius: 10px; padding: 26px; color: #8B94A5; font-size: 14px; }
.kpi-strip { display: grid; grid-template-columns: repeat(5, minmax(0,1fr)); gap: 4px 18px;
  margin-top: 14px; border-top: 1px solid #273246; padding-top: 12px; }
.kpi-strip.c4 { grid-template-columns: repeat(4, minmax(0,1fr)); }
.kpi { background: none; border: none; border-radius: 0; padding: 2px 0; min-width: 0; }
.kpi .k { font-size: 10px; font-weight: 650; letter-spacing: .13em; text-transform: uppercase; color: #8B94A5; }
.kpi .v { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 17px; font-weight: 600; color: #F7F8FA; margin-top: 5px; }
.kpi .s { font-size: 11px; color: #626B7A; margin-top: 2px; }

/* ---------- unified control rail: divided, sticky, clearly one instrument ---------- */
div[data-testid="stHorizontalBlock"]:has([data-testid="stSegmentedControl"]) {
  position: sticky; top: 0; z-index: 50; background: #080C16;
  border-top: 1px solid #273246; border-bottom: 1px solid #273246;
  padding: 10px 0 12px; margin-top: 14px;
}
div[data-testid="stHorizontalBlock"]:has([data-testid="stSegmentedControl"]) [data-testid="stWidgetLabel"] span {
  color: #626B7A !important;
}
div[data-testid="stSegmentedControl"] button { transition: background .18s ease, color .18s ease, border-color .18s ease; }

/* ---------- sidebar: kill material-icon bleed completely ---------- */
[data-testid="stSidebarNav"] [data-testid="stNavIcon"],
[data-testid="stSidebarNav"] .material-icons,
[data-testid="stSidebarNav"] .material-symbols-outlined,
[data-testid="stSidebarNav"] .material-symbols-rounded,
[data-testid="stSidebarNav"] [class*="material-symbols"],
[data-testid="stSidebarNavLink"] [data-testid="stNavIcon"] { display: none !important; width: 0 !important; font-size: 0 !important; }
[data-testid="stSidebarNavLink"] { gap: 0 !important; }

/* ---------- accessibility: visible focus ---------- */
a:focus-visible, button:focus-visible, input:focus-visible,
[role="tab"]:focus-visible, [tabindex]:focus-visible {
  outline: 2px solid #4FA6D8 !important; outline-offset: 2px;
}

.stTabs [data-bid="stTab"] { font-weight: 600; }
div[data-testid="stExpander"] { background: transparent !important; }
div[data-testid="stExpander"] > details { border: none !important; border-top: 1px solid #273246 !important;
  border-radius: 0 !important; background: transparent !important; margin: 0 !important; }
div[data-testid="stExpander"] > details > summary { padding-left: 0 !important; }
[data-testid="stToolbar"], [data-testid="stAppDeployButton"], [data-testid="stMainMenu"] { display: none !important; }
[data-testid="stHeader"] { background: transparent; }
.rail-cell .v { white-space: nowrap; }
[data-testid="stSidebarNav"] a { border-radius: 8px; margin: 1px 8px; }
[data-testid="stSidebarNavLink"][aria-current="page"], [data-testid="stSidebarNavLink"][data-active="true"] {
  background: rgba(79,166,216,.14) !important; color: #F7F8FA !important; }
[data-testid="stSidebar"] hr { border-color: #273246; }
[data-testid="stAlert"] { border-radius: 10px; }

@media (max-width: 900px) {
  .lab-rail, .lab-rail.c4, .kpi-strip, .kpi-strip.c4 { grid-template-columns: 1fr 1fr; }
  .rail-cell .v { white-space: normal; overflow-wrap: anywhere; font-size: 11.5px; }
  .mc-value { font-size: 38px; }
  .lab-thesis { font-size: 23px; }
  h1 { font-size: 27px; }
  div[data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
  div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { min-width: min(230px, 100%); }
}
@media (max-width: 560px) {
  .lab-rail, .lab-rail.c4, .kpi-strip, .kpi-strip.c4 { grid-template-columns: 1fr; }
  .flow { flex-direction: column; }
  .flow-node { border-top: 1px solid #273246; margin-right: 0; padding-bottom: 10px; }
  .flow-arrow { transform: rotate(90deg); padding: 2px 0; margin: 0; justify-content: flex-start; align-items: center; height: 22px; }
  div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { min-width: 100%; }
  div[data-testid="stHorizontalBlock"]:has([data-testid="stSegmentedControl"]) { position: static; }
}
"""


def inject_theme() -> None:
    st.markdown("<style>" + _CSS + "</style>", unsafe_allow_html=True)


def badges(*items: tuple[str, str]) -> None:
    """Status badges. kinds: frozen | live | dim | ver (right-aligned version)."""
    cls = {"frozen": "frozen", "live": "live", "dim": "", "ver": "ver"}
    html = '<div class="lab-badges">' + "".join(
        f'<span class="badge {cls.get(k, "")}">'
        + ("" if k == "ver" else '<span class="dot"></span>')
        + f"{text}</span>"
        for text, k in items
    ) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


def hero(title: str, sub: str, version: str = "") -> None:
    st.markdown(
        f'<div class="lab-hero"><h1>{title}</h1>'
        + (f'<span class="panel-tag" style="font-family:{FONT_MONO};font-size:12px;color:#626B7A;">{version}</span>' if version else "")
        + f'<p class="sub">{sub}</p></div>',
        unsafe_allow_html=True,
    )


def meta_rail(items: Iterable[tuple[str, str, str]], cols: int = 5) -> None:
    """items: (label, value, sub) compact metadata rail — not prose cards."""
    cells = "".join(
        f'<div class="rail-cell"><div class="k">{k}</div><div class="v">{v}</div>'
        + (f'<div class="s">{s}</div>' if s else "")
        + "</div>"
        for k, v, s in items
    )
    st.markdown(f'<div class="lab-rail{" c4" if cols == 4 else ""}">{cells}</div>', unsafe_allow_html=True)


def section_head(kicker: str, title: str, sub: str = "") -> None:
    """Section header: mono kicker + title + hairline rule. Never a box."""
    st.markdown(
        f'<div class="lab-sec"><div class="lab-kicker">{kicker}</div>'
        f'<h2 class="lab-sec-title">{title}</h2>'
        + (f'<div class="lab-sec-sub">{sub}</div>' if sub else "")
        + '<hr class="rule"></div>',
        unsafe_allow_html=True,
    )


def thesis_statement(html: str) -> None:
    """Dominant research statement. Large type only — no card, no border."""
    st.markdown(f'<div class="lab-thesis">{html}</div>', unsafe_allow_html=True)


def metric_card(col, kicker: str, model: str, value: str, unit: str, note: str = "",
                tone: str = "") -> None:
    """tone: '' | 'forecast' (indigo top rule) | 'inventory' (teal top rule)."""
    with col:
        st.markdown(
            f"""<div class="mc{f' tone-{tone}' if tone else ''}"><div class="mc-k">{kicker}</div>
            <div class="mc-model">{model}</div>
            <div class="mc-value">{value}</div>
            <div class="mc-unit">{unit}</div>
            <div class="mc-note">{note}</div></div>""",
            unsafe_allow_html=True,
        )


def chart_panel(fig, title: str, interpretation: str = "", tag: str = "") -> None:
    """Borderless figure: header row, the chart as the surface, caption below.

    A tag with no title joins the caption line instead of orphaning a header row.
    """
    if title:
        st.markdown(
            f'<div class="fig-head"><span class="fig-title">{title}</span>'
            + (f'<span class="badge {tag[1]}">{tag[0]}</span>' if tag else "")
            + "</div>",
            unsafe_allow_html=True,
        )
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "displayModeBar": False})
    if interpretation or (tag and not title):
        st.markdown(
            '<div class="fig-cap">'
            + (f'<span class="badge {tag[1]}" style="margin-right:10px;">{tag[0]}</span>' if (tag and not title) else "")
            + (interpretation or "")
            + "</div>",
            unsafe_allow_html=True,
        )


def insight_panel(what: str, why: str = "", header: str = "WHAT THIS SHOWS", why_header: str = "WHY IT MATTERS",
                  tone: str = "") -> None:
    """tone: '' | 'frozen' (amber rule) | 'live' (blue rule)."""
    html = f'<div class="insight{f" tone-{tone}" if tone else ""}"><div class="h">{header}</div><div class="w">{what}</div>'
    if why:
        html += f'<div class="why"><div class="h">{why_header}</div><div class="w">{why}</div></div>'
    st.markdown(html + "</div>", unsafe_allow_html=True)


def flow_diagram(nodes: Iterable[tuple[str, str]], last_highlight: bool = True, compact: bool = False) -> None:
    nodes = list(nodes)
    html = '<div class="flow compact">' if compact and len(nodes) > 5 else '<div class="flow">'
    for i, (t, d) in enumerate(nodes):
        hit = ' hit' if (i == len(nodes) - 1 and last_highlight) else ''
        html += f'<div class="flow-node{hit}"><div class="t">{t}</div>' + (f'<div class="d">{d}</div>' if d else "") + "</div>"
        if i < len(nodes) - 1:
            html += '<div class="flow-arrow">&#8594;</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def kpi_strip(items: Iterable[tuple[str, str, str]], cols: int = 5) -> None:
    cells = "".join(
        f'<div class="kpi"><div class="k">{k}</div><div class="v">{v}</div>'
        + (f'<div class="s">{s}</div>' if s else "") + "</div>"
        for k, v, s in items
    )
    st.markdown(f'<div class="kpi-strip{" c4" if cols == 4 else ""}">{cells}</div>', unsafe_allow_html=True)


def empty_state(msg: str) -> None:
    st.markdown(f'<div class="empty">{msg}</div>', unsafe_allow_html=True)


def glossary(*terms: str) -> None:
    defs = {
        "MASE": "Mean Absolute Scaled Error — forecast error scaled by the in-sample naive error. Below 1 beats naive. Lower is better.",
        "sMAPE": "Symmetric mean absolute percentage error. Lower is better.",
        "MAE": "Mean absolute error, in demand units. Lower is better.",
        "RMSE": "Root mean squared error, in demand units; punishes large misses harder. Lower is better.",
        "Inventory cost": "Simulated total inventory cost under the common policy (holding + stockout penalty). Lower is better.",
        "Service level": "Fill rate — share of demand satisfied without stockout. Higher is better.",
        "Common policy": "One shared daily-review order-up-to policy with lost sales, applied identically to every model, so gaps come from forecasts — never from policy tuning.",
        "Intermittent demand": "Demand with many zero or low-demand periods — sparse and hard to forecast. M5 behaves this way (64.5% zero rate).",
        "Dense demand": "Smooth, mostly non-zero demand per period. Store Item Demand behaves this way (0.02% zero rate).",
        "WAPE": "Weighted absolute percentage error (per-series mean). Lower is better.",
    }
    with st.expander("Metric definitions"):
        for t in terms:
            if t in defs:
                st.markdown(f'<div class="gloss"><b>{t}</b> — {defs[t]}</div>', unsafe_allow_html=True)


def lab_footer(hint: str) -> None:
    st.markdown("---")
    st.caption(hint)


# ---------- Plotly dark template (DESIGN.md §15) ----------

def fig_base(height: int = 430, width=None) -> "object":
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.update_layout(
        height=height,
        width=width,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=48, b=10),
        font=dict(family=FONT_UI, size=12.5, color="#C6CEDB"),
        hoverlabel=dict(bgcolor="#182236", bordercolor="#273246",
                        font=dict(family=FONT_UI, size=12, color="#F7F8FA")),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12, color="#97A1B3")),
    )
    fig.update_xaxes(gridcolor="rgba(39,50,70,.55)", zerolinecolor="#273246", linecolor="#273246",
                     tickfont=dict(size=11.5, color="#8B94A5"), title_font=dict(size=12, color="#8B94A5"))
    fig.update_yaxes(gridcolor="rgba(39,50,70,.55)", zerolinecolor="#273246", linecolor="#273246",
                     tickfont=dict(size=11.5, color="#8B94A5"), title_font=dict(size=12, color="#8B94A5"))
    return fig


def mono_annotation(x, y, text, color="#8B94A5", **kw):
    return dict(x=x, y=y, text=text, showarrow=False,
                font=dict(family=FONT_MONO, size=11, color=color), **kw)
