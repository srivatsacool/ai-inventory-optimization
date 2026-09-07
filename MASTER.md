# SIRP Paint Design System — MASTER.md

> Single source of truth for the SIRP visual universe: the Astro site, the HOME Svelte charts, and the Streamlit lab. Every hex, duration, and spacing value in code must come from this file.

**Thesis (validated 2026-09-06):**
- **Visual:** Warm editorial research world — cream off-white grounds, dark ink text, steel-blue structure, 12-hue colorblind-safe data palette as the color heroes; hairline borders, small radii, editorial whitespace, charts as color on quiet paper.
- **Interaction:** Fast and quiet (120–200ms ease-out), instant toggles, gentle 300ms bar-grow, hover = brightness only, no parallax, no bounce, data moves / chrome never does.

---

## 1. Grounds & Ink (shared)

| Token | Hex | Role |
|-------|-----|------|
| `--paper` | `#FAF8F4` | Site page ground (warm cream) |
| `--paper-2` | `#F3EFE6` | Lab panel ground (deeper cream) |
| `--paper-3` | `#EDE8DB` | Elevated panel / hover ground |
| `--ink` | `#1E222A` | Primary text (both worlds) |
| `--ink-soft` | `#4A505C` | Secondary text |
| `--ink-mute` | `#8A8D93` | Labels, captions, metadata |
| `--line` | `#D8D2C4` | Hairline borders |
| `--line-strong` | `#C4BBA8` | Hover/active borders |
| `--trad` | `#35618A` | Structure blue (nav, buttons, active, focus) |
| `--trad-bright` | `#4E7BA8` | Blue on cream for data/UI where more presence is needed |
| `--frozen` | `#B08D3F` | Frozen-evidence accent (darkened amber for light ground) |
| `--interactive` | `#4FA6D8` | Interactive status blue |
| `--success` | `#3D7B55` | Success/winner green (light-ground) |
| `--warning` | `#B08D3F` | Warning = frozen amber |
| `--danger` | `#C25B64` | Danger (light-ground) |

Contrast: ink on paper = 14.8:1; ink-soft = 7.4:1; trad on paper = 6.1:1; ink-mute ≥ 4.6:1 ✓ (all ≥ 4.5:1 WCAG AA).

## 2. The 12-Model Data Palette

The color heroes. Okabe-Ito derived, colorblind-safe, tuned for cream grounds. Winners = full saturation + bold; losers = 55% opacity, never gray.

| Model | Token | Hex |
|-------|-------|-----|
| Naive | `--m-naive` | `#9D4EDD` violet |
| Seasonal Naive | `--m-snaive` | `#C77DFF` lilac |
| Moving Average | `--m-ma` | `#2A9D8F` teal |
| SES | `--m-ses` | `#43AA8B` jade |
|
DES | `--m-des` | `#577590` slate |
| TES | `--m-tes` | `#35618A` site blue |
| ARIMA | `--m-arima` | `#E76F51` terracotta |
| SARIMA | `--m-sarima` | `|`#F4A261` amber |
| Croston | `--m-croston` | `#E9C46A` saffron |
| SBA | `--m-sba` | `#BC6C25` umber |
| TSB | `--m-tsb` | `#6D597A` plum |
| LSTM | `--m-lstm` | `#D1495B` crimson (hero) |

**Winner treatment:** winner bar/line = 100% opacity + 2.5px stroke; all others 55% opacity. No extra chrome, the color itself is the highlight.

## 3. Typography

Unchanged from the validated site system — the lab inherits it verbatim.

| Role | Spec |
|------|------|
| UI | `Inter, ui-sans-serif, system-ui, 'Segoe UI', sans-serif` |
| Mono | `'JetBrains Mono', Consolas, monospace` |
| H1 | 34px / 650 / -0.02em |
| H2 | 24px / 650 / -0.015em |
| H3 | 16px / 650 |
| Body | 13–15px / 400 |
| Kicker/labels | 10–11px / 650 / 0.12–0.15em / uppercase / mono-family |
| KPI numerals | mono / 48px / tabular-nums |

## 4. Spacing (4px base)

`4 · 8 · 12 · 16 · 20 · 24 · 32 · 48 · 64` — large gaps between sections (32–48px), tight within groups (8–12px). Same rhythm as the site.

## 5. Radii & Elevation

| Token | Value | Use |
|-------|-------|------|
| `--r-sm` | 4px | inline chips |
| `--r-md` | 6px | buttons, inputs |
| `--r-lg` | 10px | panels, cards |
| `--r-pill` | 9999px | status badges |
| shadow-1 | `0 1px 2px rgba(30,34,42,.05)` | cards (barely-there) |
| shadow-2 | `0 2px 8px rgba(30,34,42,.07)` | elevated panels |

## 6. Motion Tokens

| Token | Value | Use |
|-------|--------|-----|
| `--dur-fast` | 120ms | hovers, toggles |
| `--dur-norm` | 200ms | panel transitions, tab swaps |
| `--dur-grow` | 300ms | bar-grow, chart entry |
| `--ease-out` | cubic-bezier(0.22, 0.61, 0.36, 1) | everything |
| stagger | none | no stagger (chrome never moves) |

**Forbidden:** gradients, glass, glow, bounce, parallax, decorative animation, animated counters, scale-on-hover. Hover = brightness/color shift only.

## 7. Streamlit Theme Mapping (config.toml)

```toml
[theme]
base = "light"
primaryColor = "#35618A"
backgroundColor = "#F3EFE6"        # lab panel cream
secondaryBackgroundColor = "#FAF8F4" # paper cards
textColor = "#1E222A"
font = "sans serif"
```

## 8. Site tokens.css delta

The site's `tokens.css` keeps its existing validated values (`--paper #fbfbfa` etc.) — no churn on the already-FINAL site chrome. The **only** site-side additions: the 12-model palette CSS custom properties + `.chart-card` backgrounds moving to `--paper-2` cream where charts sit on panels. Site chrome stays ink/paper/blue; data palette is additive.

## 9. Component Kit (lab.py API — unchanged)

All lab.py component APIs stay: `badges`, `hero`, `meta_rail`, `section_head`, `thesis_statement`, `metric_card`, `chart_panel`, `insight_panel`, `flow_diagram`, `kpi_strip`, `empty_state`, `glossary`, `lab_footer`, `fig_base`, `mono_annotation`, plus new `MODEL_COLORS` dict + `model_color(model)` helper.

`fig_base()` becomes the **light Plotly template** (cream panel, ink text, hairline grids, hoverlabel = paper-2 on line-strong, legend = ink-soft).

## 10. Audit Gates

- Contrast ≥ 4.5:1 for all text pairs (verified in §1)
- All motion 120–300ms ease-out; no forbidden patterns
- `@media (prefers-reduced-motion: reduce)` — bar-grow/hovers become instant
- 4 breakpoints: 375 / 768 / 1024 / 1440
- Focus rings: 2px `--interactive` outline, always visible
- Winner treatment: saturation+bold, no winner chrome
