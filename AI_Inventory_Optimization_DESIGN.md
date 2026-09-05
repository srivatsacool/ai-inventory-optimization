---
description: A custom design system for a serious AI inventory
  optimization research product composed of an editorial research
  website (HOME), a flagship interactive Streamlit analytics laboratory
  (LAB), and a formal research-paper reader (DOC). Inspired by the
  information hierarchy, editorial calm, analytical density, and
  component discipline of Coinbase, Claude, ClickHouse, and Airtable,
  but intentionally designed as an original research interface rather
  than a brand clone.
name: AI Inventory Optimization Research Product Design System
version: 1
---

# AI Inventory Optimization --- DESIGN.md

## 1. Design Intent

### Product identity

This project is a public research product, not a SaaS dashboard and not
a generic academic report.

It has three connected surfaces:

-   **HOME** --- editorial research publication: explain the problem,
    question, methodology, model evolution, findings, and thesis.
-   **LAB** --- flagship interactive research dashboard: let visitors
    interrogate the actual evidence through charts, controls,
    comparisons, forecast behavior, inventory simulation, and
    sensitivity analysis.
-   **DOC** --- formal research-paper reader: let visitors read the
    complete canonical publication with index, navigation, search/zoom
    where supported, and full-screen reading.

The experience should communicate:

> **Research publication → interactive evidence → formal paper**

The visitor should feel that all three are parts of one system.

### Design north star

**Editorial intelligence × analytical precision × research
credibility.**

The design should feel:

-   sophisticated
-   calm
-   data-rich
-   technical
-   cinematic in moderation
-   highly legible
-   deliberate
-   trustworthy
-   interactive

It should NOT feel:

-   gamer-like
-   neon-heavy
-   like a generic BI dashboard
-   like a stock Streamlit app
-   like a wall of academic prose
-   like a collection of unrelated UI templates

### Source inspiration

This system extracts principles rather than copying brand identities:

-   **Claude:** warm editorial typography, restrained surfaces, literary
    hierarchy, strong dark product panels.
-   **Coinbase:** institutional calm, restrained accent usage,
    product/UI cards, analytical credibility, clear financial-data
    hierarchy.
-   **ClickHouse:** dark-first analytical density, strong stat
    treatment, technical cards, code/data surfaces.
-   **Airtable:** modular information architecture, tabs/filters, clean
    workflow controls, signature section bands, disciplined spacing.

Do not reproduce any brand's exact logo, proprietary font, signature
illustration, or distinctive visual identity.

------------------------------------------------------------------------

# 2. Product Architecture

## Global navigation

Use:

**HOME · LAB · DOC**

Optional secondary navigation may expose:

-   Research
-   Methodology
-   Findings
-   About

but never compete with the three primary destinations.

### Route responsibilities

`/`

Editorial research story.

`/lab`

Full interactive Streamlit research dashboard embedded into the public
shell.

`/doc`

Formal research-paper reading environment.

### Layer distinction

HOME asks:

> What is this research and why does it matter?

LAB asks:

> What does the evidence actually show, and what happens when I
> interrogate it?

DOC asks:

> What is the complete formal research record?

------------------------------------------------------------------------

# 3. Visual Theme & Atmosphere

## HOME atmosphere

HOME uses a refined editorial canvas:

-   warm off-white / paper background
-   dark ink
-   restrained steel-blue, teal, indigo, and violet
-   occasional dark full-width research bands
-   large editorial typography
-   generous whitespace
-   diagrams and product-style research visualizations

The HOME page should feel closer to a premium research publication than
to a startup landing page.

## LAB atmosphere

LAB is intentionally darker and denser.

Base:

-   near-black navy
-   layered blue-black surfaces
-   subtle blue/indigo/teal atmospheric lighting
-   restrained borders
-   analytical chart surfaces
-   compact metadata
-   strong numerical hierarchy

LAB should feel like a **research instrument**.

The dark environment must not become decorative. Every surface should
support analysis.

## DOC atmosphere

DOC returns to an editorial reading environment:

-   warm paper/off-white canvas
-   dark ink
-   very low visual noise
-   persistent document index
-   strong reading width
-   subtle page controls
-   excellent typography

------------------------------------------------------------------------

# 4. Color System

Use semantic roles rather than scattering raw colors throughout the UI.

## Core colors

``` yaml
colors:
  paper: "#F4F4F1"
  paper-soft: "#ECEDEA"
  ink: "#161A22"
  ink-soft: "#303641"

  lab-bg: "#080C16"
  lab-surface: "#0E1422"
  lab-surface-2: "#131B2B"
  lab-surface-3: "#182236"

  steel: "#35618A"
  teal: "#27757A"
  indigo: "#5B56A0"
  violet: "#7A53A6"

  white: "#F7F8FA"
  muted: "#8B94A5"
  muted-soft: "#626B7A"

  hairline: "#273246"
  hairline-light: "#D9DDE1"

  success: "#48B89A"
  warning: "#D5A34A"
  danger: "#D66B73"
  info: "#6C9DDA"

  frozen: "#C59B52"
  interactive: "#4FA6D8"
```

## Color rules

### Research identity

Steel, teal, indigo, and violet are the project's controlled accent
family.

Do not use all four at equal intensity.

Recommended hierarchy:

1.  Steel --- primary analytical accent
2.  Teal --- inventory / operational outcome
3.  Indigo --- model / forecast analysis
4.  Violet --- secondary analytical emphasis

### Frozen evidence

Use `frozen` amber/gold sparingly for:

-   LOCKED
-   PUBLISHED
-   READ-ONLY
-   evidence freeze metadata

Frozen evidence should look authoritative, not warning-like.

### Interactive state

Use `interactive` blue for:

-   selected controls
-   active analysis
-   interactive badges
-   hover/focus
-   scenario state

### Semantic colors

Use:

-   success = positive outcome / valid state
-   warning = sensitivity / caution
-   danger = stockout / failure / invalid state
-   info = explanatory context

Do not use red and green merely as decoration.

------------------------------------------------------------------------

# 5. Typography

## General principle

Use two typographic voices.

### Editorial display

For HOME and DOC headings:

``` yaml
fontFamily:
  "Georgia, 'Times New Roman', serif"
```

Use a refined serif only for major editorial headings.

### Analytical interface

LAB uses a clean sans:

``` yaml
fontFamily:
  "Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
```

Numbers and technical metadata may use:

``` yaml
fontFamily:
  "'JetBrains Mono', 'SFMono-Regular', Consolas, monospace"
```

Do not make the entire dashboard monospaced.

## Type scale

``` yaml
display-xl: 64px / 1.02 / 400
display-lg: 48px / 1.08 / 400
display-md: 36px / 1.12 / 400

lab-title: 34px / 1.15 / 650
lab-section: 24px / 1.25 / 650
lab-card-title: 16px / 1.35 / 650

body-lg: 18px / 1.55 / 400
body-md: 15px / 1.55 / 400
body-sm: 13px / 1.5 / 400

label: 11px / 1.35 / 650
metric: 34px / 1.0 / 650
metric-large: 48px / 0.95 / 650
mono: 12px / 1.45 / 500
```

### Labels

Use uppercase only for compact metadata:

`FORECAST ACCURACY`

`FROZEN EVIDENCE`

`DATASET`

Do not turn paragraphs into uppercase text.

### Numerical typography

Research values should be visually dominant.

Example:

``` text
LSTM
1.316
MASE
```

not:

``` text
M5 FORECAST WINNER
LSTM
MASE 1.316
Lowest forecast error...
```

with every line receiving equal visual weight.

The number should be immediately scannable.

------------------------------------------------------------------------

# 6. Layout System

## Desktop target

Primary design target:

1440px wide desktop.

Support:

-   1280px
-   1440px
-   1600px+
-   1024px tablet
-   mobile fallback

## Main content width

HOME:

`max-width: 1200–1280px`

LAB:

`max-width: 1500–1600px`

DOC:

`max-width: 1440px`

## Grid

LAB uses a dashboard grid.

Recommended:

``` text
12-column analytical grid
gap: 16–20px
```

Typical compositions:

``` text
4 × metric cards

8 / 4
large chart / insight panel

7 / 5
forecast chart / model comparison

6 / 6
inventory outcome / sensitivity controls

12
full-width detailed chart/table
```

Avoid putting every element into a card.

Charts can occupy large open surfaces.

------------------------------------------------------------------------

# 7. Surfaces, Cards & Depth

## LAB surfaces

Use four levels:

### Level 0

`lab-bg`

Page background.

### Level 1

`lab-surface`

Primary sections.

### Level 2

`lab-surface-2`

Cards and analytical containers.

### Level 3

`lab-surface-3`

Nested controls, selected states, chart overlays.

### Borders

Use 1px hairlines.

Borders should define structure, not glow.

### Radius

``` yaml
xs: 4px
sm: 6px
md: 10px
lg: 14px
xl: 18px
pill: 9999px
```

Use:

-   10px for controls
-   14px for cards
-   18px for major feature panels
-   pills for compact status tags only

Do not make everything pill-shaped.

## Shadows

Prefer subtle elevation:

``` text
0 12px 40px rgba(0,0,0,0.18)
```

Avoid large blurred neon shadows.

------------------------------------------------------------------------

# 8. LAB --- Flagship Dashboard Rules

This is the most important section of this DESIGN.md.

The Streamlit application is a **full portfolio-quality analytical
dashboard**.

It must not look like a Streamlit report.

It must not become text-heavy.

## Core dashboard rule

Every major analytical section should contain:

1.  a clear question;
2.  an interactive control where meaningful;
3.  a visualization;
4.  a concise interpretation.

Avoid:

``` text
Heading
paragraph
paragraph
paragraph
table
paragraph
```

Prefer:

``` text
QUESTION
[controls]

        CHART / VISUAL

KEY FINDING
one concise explanation

[expand for detail]
```

## Dashboard density

The Lab should feel information-rich without feeling crowded.

Target approximately:

-   60--70% visual/interactive surface
-   20--30% explanatory text
-   5--10% metadata

Text should explain visuals, not replace them.

------------------------------------------------------------------------

# 9. LAB Navigation

Use a persistent left navigation or compact top/side navigation.

Primary sections:

``` text
01  Frozen Results
02  Forecast Explorer
03  Inventory Lab
04  Methodology
```

The active page must be visually obvious.

Use icons only when they improve scanability.

Recommended status system:

``` text
LOCKED / PUBLISHED
Evidence — Read Only
```

and:

``` text
INTERACTIVE
Scenario / Experimental
```

Never blur these two states.

------------------------------------------------------------------------

# 10. Frozen Results --- Dashboard Redesign

The current implementation is too text-heavy.

Do not reproduce its present layout.

## Hero

Use a compact analytical hero:

``` text
FROZEN RESULTS                         v1.0
Published evidence · Read-only

Forecast accuracy and inventory performance
from the final verified research run.
```

Then immediately present the thesis visually.

## Research metadata

Do not use five large prose cards.

Use a compact metadata rail:

``` text
TRAIN             VALIDATION        TEST
2013–2015         2015–2016         2016–2016

DATASET           POLICY
M5 + Store        L7 · 95% · H=1 · P=5
```

## Thesis in numbers

Use four compact analytical cards:

### M5 forecast

``` text
LSTM
1.316
MASE
```

### Store forecast

``` text
LSTM
0.978
MASE
```

### M5 inventory

``` text
LSTM
152.83
COST
```

### Store inventory

``` text
Moving Average
2084.50
COST
```

Never truncate `Moving Average`.

Each card may contain one short sentence, but not a paragraph.

## Add actual charts

Frozen Results should immediately show visual evidence.

Recommended chart modules:

### Chart A --- Forecast model comparison

Horizontal bar chart:

``` text
M5
MASE
lower is better

MA
SES
DES
TES
ARIMA
SARIMA
LSTM
```

Highlight the actual winner.

### Chart B --- Store model comparison

Same structure.

Provide a dataset toggle:

``` text
[M5] [STORE]
```

Do not create fake data for models that do not have verified results.

### Chart C --- Forecast vs actual

A temporal line chart with:

-   Actual
-   selected model forecast

Controls:

``` text
Dataset
Model
Date range
```

Only expose controls supported by existing data.

### Chart D --- Inventory outcome comparison

Show:

``` text
Forecast winner
Inventory winner
```

for each environment.

This should visually reinforce:

> Forecast winner ≠ inventory winner.

## Thesis relationship diagram

Use a compact horizontal analytical flow:

``` text
FORECAST QUALITY
       ↓
FORECAST BEHAVIOR
       ↓
COMMON INVENTORY POLICY
       ↓
SIMULATED INVENTORY OUTCOME
```

Each node should be visual, not a paragraph.

------------------------------------------------------------------------

# 11. Forecast Explorer

This page is a genuine model-analysis workspace.

## Control bar

At the top:

``` text
DATASET
[M5 ▼]

MODEL
[LSTM ▼]

METRIC
[MASE ▼]

VIEW
[Forecast] [Errors] [Comparison]
```

Use segmented controls where choices are mutually exclusive.

Use dropdowns only where the option list is long.

## Primary chart

Large chart:

**Actual vs Forecast**

Controls should update the visualization.

## Secondary visualizations

Depending on available data:

-   rolling error
-   absolute error distribution
-   model ranking
-   residual behavior
-   error by time
-   forecast horizon behavior

Do not show every chart simultaneously.

Use tabs or progressive disclosure.

## Model comparison

Use a horizontal ranking chart.

Show:

-   model
-   metric
-   rank
-   winner

Never rely only on a table.

## Interpretation panel

Example structure:

``` text
WHAT THIS SHOWS

LSTM has the lowest verified MASE
for this demand environment.

WHY IT MATTERS

Forecast accuracy is a useful signal,
but it does not determine inventory
cost by itself.
```

Keep this concise.

------------------------------------------------------------------------

# 12. Inventory Lab

This is the interactive what-if laboratory.

## Layout

Use:

``` text
┌─────────────────────────────┬──────────────────┐
│ COST / SERVICE CHART        │ SCENARIO CONTROL │
│                             │                  │
│                             │ Service level    │
│                             │ Lead time        │
│                             │ Holding cost     │
│                             │ Stockout cost    │
└─────────────────────────────┴──────────────────┘
```

Controls belong beside the visualization they affect.

## Scenario controls

Where supported:

-   dataset
-   model
-   lead time
-   service level
-   forecast horizon
-   holding cost
-   stockout cost

Use sliders for continuous values.

Use segmented controls/dropdowns for categorical values.

## Results

Show dynamic analytical values:

``` text
TOTAL COST
HOLDING COST
STOCKOUT COST
SERVICE LEVEL
AVERAGE INVENTORY
ORDER FREQUENCY
```

Only show metrics that are actually supported by the underlying
simulation.

## Scenario comparison

Allow:

``` text
BASELINE
vs
SCENARIO A
vs
SCENARIO B
```

when the current implementation/data supports it.

Visualize the change.

## Critical label

Every dynamic sensitivity result must visibly say:

`INTERACTIVE SENSITIVITY`

It must never resemble the frozen published result.

------------------------------------------------------------------------

# 13. Methodology Dashboard

Do not create a wall of prose.

Use a visual research pipeline:

``` text
DATA
  ↓
EXPLORATION
  ↓
PREPROCESSING
  ↓
FORECASTING
  ↓
FORECAST EVALUATION
  ↓
INVENTORY SIMULATION
  ↓
ROBUSTNESS
  ↓
FINAL COMPARISON
```

Each stage becomes an expandable module.

Include:

-   train period
-   validation period
-   test period
-   temporal integrity
-   model ladder
-   metrics
-   common policy
-   frozen evidence boundary

Use diagrams and compact metadata.

------------------------------------------------------------------------

# 14. Interactive Controls

Controls should be obvious and purposeful.

## Preferred hierarchy

### Segmented control

Use for:

``` text
M5 | Store
```

when there are only two or three choices.

### Selectbox

Use for:

``` text
MA | SES | DES | TES | ARIMA | SARIMA | LSTM | ...
```

### Slider

Use for:

-   service level
-   lead time
-   cost assumptions
-   horizon

### Toggle

Use only for true binary states:

``` text
Show confidence band
Show error markers
Normalize values
```

Do not use toggles simply because they look interactive.

## Control grouping

Group related controls into a compact `ANALYSIS CONTROLS` rail.

Do not scatter dropdowns across the page.

------------------------------------------------------------------------

# 15. Charts

Charts are first-class components.

## General chart rules

Every chart needs:

-   meaningful title
-   one-line interpretation
-   readable axes
-   direct labels where useful
-   hover details
-   clear units
-   winner annotation where appropriate
-   "lower is better" / "higher is better" context when relevant

Avoid chart titles like:

`Model Performance`

Prefer:

`MASE by model · lower is better`

## Preferred chart types

### Forecasts

Line charts.

### Model ranking

Horizontal bar charts.

### Cost composition

Stacked bar or carefully chosen composition chart.

### Sensitivity

Line chart or heatmap if supported by the current charting stack.

### Error distributions

Histogram / box-style visualization if supported.

### Relationships

Scatter plot.

Do not create pie charts unless a true part-to-whole relationship exists
and the number of categories is small.

## Plotly

Prefer Plotly for the Streamlit analytical layer.

Charts should inherit the Lab theme:

-   dark plot background
-   muted grid
-   restrained accent family
-   strong selected series
-   subdued comparison series
-   clear hover states

Never make every model a different bright color.

------------------------------------------------------------------------

# 16. Data Tables

Tables are supporting components, not the main storytelling mechanism.

Use them for:

-   exact values
-   auditability
-   detailed model comparisons
-   reproducibility

Use visualizations for:

-   rankings
-   trends
-   relationships
-   changes
-   patterns

A table should never be the only way to understand a result.

------------------------------------------------------------------------

# 17. HOME --- Editorial Research Website

HOME should be redesigned as a research publication, not a dashboard.

## Hero

Use large serif typography.

Core statement:

> **Forecasting is the mechanism. Inventory is the outcome.**

Supporting copy should establish:

-   AI forecasting models
-   retail demand environments
-   inventory policy
-   operational outcomes

Primary CTAs:

`ENTER THE LAB`

`READ THE RESEARCH`

## Model evolution

Visual horizontal progression:

``` text
MA → SES → DES → TES → ARIMA → SARIMA → LSTM → LLM
```

Use subtle motion on interaction, not constant animation.

## Research environments

Create a visual comparison:

``` text
M5
Sparse / intermittent demand

VS

Store / Favorita
Dense / smoother demand
```

## Research logic

Use visual diagrams:

``` text
Demand
  ↓
Forecast
  ↓
Inventory Policy
  ↓
Service / Holding / Stockout
  ↓
Operational Outcome
```

## Findings

Introduce verified findings without turning HOME into the full
dashboard.

Use concise visual result blocks.

Do not invent or approximate research values.

------------------------------------------------------------------------

# 18. DOC --- Research Reader

DOC should feel like a digital academic publication.

Layout:

``` text
┌───────────────┬───────────────────────────────┐
│ CONTENTS      │ RESEARCH PAPER                │
│               │                               │
│ Abstract      │ page 01 / 43                  │
│ Introduction  │                               │
│ Data          │       PDF READER              │
│ Methodology   │                               │
│ Forecasting   │                               │
│ Results       │                               │
│ Discussion    │                               │
│ References    │                               │
└───────────────┴───────────────────────────────┘
```

Controls:

-   page number
-   previous/next
-   zoom
-   search if supported
-   fullscreen
-   download

Use the canonical research PDF.

Never create competing publication copies.

------------------------------------------------------------------------

# 19. Component System

## Required LAB components

Create reusable components for:

-   `LabShell`
-   `LabNav`
-   `StatusBadge`
-   `MetricCard`
-   `MetricDefinition`
-   `ControlBar`
-   `SegmentedControl`
-   `ChartPanel`
-   `InsightPanel`
-   `ComparisonPanel`
-   `ScenarioPanel`
-   `EvidenceBadge`
-   `DataTable`
-   `MethodStep`
-   `EmptyState`
-   `ErrorState`

## Required HOME components

-   `Header`
-   `Hero`
-   `ResearchSection`
-   `ModelLadder`
-   `DatasetComparison`
-   `ResearchFlow`
-   `FindingCard`
-   `LabCTA`
-   `DocCTA`
-   `Footer`

## Required DOC components

-   `DocShell`
-   `DocTOC`
-   `DocToolbar`
-   `PDFReader`
-   `PageNavigation`

------------------------------------------------------------------------

# 20. Motion

Motion should clarify state and hierarchy.

Use:

-   150--250ms control transitions
-   200--350ms card hover transitions
-   subtle chart transitions
-   section reveal on HOME
-   restrained scroll-driven storytelling

Do NOT use:

-   fake loading sequences
-   constant pulsing
-   bouncing cards
-   neon glow animations
-   animated numbers that obscure exact values

LAB should feel fast.

HOME can feel cinematic.

DOC should feel quiet.

------------------------------------------------------------------------

# 21. Responsive Rules

## Desktop

Full dashboard density.

## Tablet

Collapse:

``` text
8 / 4
```

into:

``` text
12
12
```

Move control bars into horizontal scrolling or stacked groups.

## Mobile

LAB:

-   navigation becomes compact
-   cards become one column
-   charts retain readable minimum height
-   controls stack
-   tables may scroll horizontally
-   no tiny unreadable charts

HOME:

-   maintain editorial hierarchy
-   reduce display sizes
-   preserve CTA prominence

DOC:

-   TOC becomes drawer
-   reader becomes full width

------------------------------------------------------------------------

# 22. Accessibility

Every interactive element must have:

-   visible focus state
-   keyboard accessibility
-   readable contrast
-   meaningful label
-   no color-only meaning

Charts must provide textual context.

Do not rely on hover alone to communicate essential information.

------------------------------------------------------------------------

# 23. Research Integrity Rules

These are hard constraints.

## Frozen evidence

Frozen evidence is read-only.

Never silently recompute it.

Never overwrite it with interactive sensitivity output.

## Interactive analysis

Interactive outputs must be labeled:

`INTERACTIVE SENSITIVITY`

or:

`EXPERIMENTAL`

## Never fabricate

Do not invent:

-   model results
-   rankings
-   forecast values
-   costs
-   sensitivity outcomes
-   LLM performance
-   missing metrics

If data does not exist, hide the unsupported control or clearly state
that the result is unavailable.

## Research terminology

Prefer:

-   Forecast quality
-   Inventory performance
-   Demand environment
-   Common policy
-   Simulated inventory outcome
-   Frozen evidence
-   Interactive sensitivity
-   Research laboratory
-   Decision outcome

Avoid generic SaaS terms:

-   KPI dashboard
-   AI insights
-   Smart analytics
-   Performance center
-   Business intelligence

unless genuinely required.

------------------------------------------------------------------------

# 24. Content Density Rules

This is a direct correction to the current Streamlit UI.

### Do

-   replace paragraphs with charts
-   use annotations
-   use visual comparisons
-   use tabs for secondary analysis
-   use expandable detail
-   place explanations beside evidence
-   prioritize numbers visually
-   use short research interpretations

### Do not

-   put 3--5 paragraphs under every heading
-   repeat the same explanation in multiple cards
-   create a card for every sentence
-   force users to read tables before seeing the result
-   make the visitor infer what a number means
-   use decorative whitespace that removes useful analytical density

### Target

The visitor should be able to scan a page and understand the major
result in under 10 seconds.

------------------------------------------------------------------------

# 25. Quality Bar

A successful implementation should make the current screenshot feel
obviously obsolete.

The new LAB should visibly contain:

-   multiple analytical charts
-   model comparison
-   dataset controls
-   model controls
-   metric controls
-   forecast-vs-actual views
-   inventory outcome visualization
-   sensitivity controls
-   scenario comparison where supported
-   concise research annotations
-   exact evidence values
-   clear frozen vs interactive distinction

The visitor should not see a page dominated by paragraphs.

The interface should communicate:

> **I can explore this research.**

not:

> **I am reading a Streamlit report.**

------------------------------------------------------------------------

# 26. Anti-Patterns

Never produce:

-   generic SaaS KPI dashboards
-   rainbow charts
-   excessive gradients
-   excessive glassmorphism
-   glowing borders everywhere
-   giant rounded rectangles
-   meaningless toggles
-   fake metrics
-   fake data
-   fake LLM results
-   default Streamlit styling
-   walls of prose
-   tables as the only visualization
-   chart titles with no interpretation
-   unexplained abbreviations
-   truncated labels such as `Moving Aver...`
-   inconsistent card heights
-   horizontal overflow
-   controls that do not affect anything

------------------------------------------------------------------------

# 27. Implementation Directive for Coding Agents

Before coding:

1.  Inspect the current repository.
2.  Inspect the current Streamlit pages and data architecture.
3.  Inspect `.impeccable/design.json`.
4.  Inspect the public website and recover its current content.
5.  Verify frozen evidence values.
6.  Identify which data actually exists for each model/dataset/metric.
7.  Identify existing Plotly/chart infrastructure.
8.  Preserve working research logic.

Then:

1.  Establish shared tokens.
2.  Rebuild the Streamlit shell.
3.  Rebuild Frozen Results as a chart-first analytical overview.
4.  Build Forecast Explorer.
5.  Build Inventory Lab.
6.  Build Methodology.
7.  Refactor HOME into the editorial publication layer.
8.  Build DOC reader.
9.  Connect HOME → LAB → DOC.
10. Run the applications.
11. Capture screenshots.
12. Inspect actual rendered pixels.
13. Fix hierarchy, spacing, clipping, chart readability, control
    placement, and typography.
14. Verify frozen values against source-of-truth.
15. Test all interactions.
16. Test desktop and responsive layouts.

Do not stop at a visual mockup.

Implement the system.

------------------------------------------------------------------------

# 28. Final Design Principle

The entire project should express one idea:

> **The website explains the research.**
>
> **The dashboard lets you interrogate the evidence.**
>
> **The paper preserves the complete research record.**

The LAB is not a secondary widget.

It is the project's **flagship analytical interface and
portfolio-quality dashboard**.

The final product should feel like:

**a serious research publication with a real analytical instrument
attached to it.**
