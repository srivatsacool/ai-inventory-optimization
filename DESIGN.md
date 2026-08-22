---
name: AI-INVENTORY-OPTIMIZATION — Research Proposal Website
description: Research proposal site for "From Traditional Forecasting to Large Language Models" — neutral, instrument-grade, editorial.
colors:
  paper: "#F4F4F1"
  surface: "#FDFDFB"
  ink: "#161A22"
  ink-2: "#3B424E"
  ink-3: "#5A6270"
  line: "#D9D8D0"
  line-2: "#C6C4B9"
  traditional: "#35618A"
  statistical: "#27757A"
  neural: "#5B56A0"
  llm: "#7A53A6"
  inventory: "#3D7B55"
  uncertainty: "#8F5619"
  lab-bg: "#0F131A"
  lab-ink: "#E9E8E2"
typography:
  display:
    fontFamily: "Spectral, Georgia, 'Times New Roman', serif"
    fontSize: "clamp(2.6rem, 5.2vw, 4.4rem)"
    fontWeight: 500
    lineHeight: 1.16
    letterSpacing: "-0.015em"
  headline:
    fontFamily: "Spectral, Georgia, 'Times New Roman', serif"
    fontSize: "clamp(1.8rem, 3.2vw, 2.6rem)"
    fontWeight: 600
    lineHeight: 1.16
  title:
    fontFamily: "Spectral, Georgia, 'Times New Roman', serif"
    fontSize: "clamp(1.15rem, 1.6vw, 1.4rem)"
    fontWeight: 600
  body:
    fontFamily: "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "1.0625rem"
    lineHeight: 1.68
  label:
    fontFamily: "'Fragment Mono', 'JetBrains Mono', Consolas, monospace"
    fontSize: "0.78rem"
    letterSpacing: "0.08em"
    textTransform: "uppercase"
rounded:
  sm: "4px"
  md: "8px"
  lg: "14px"
spacing:
  sp-1: "0.25rem"
  sp-2: "0.5rem"
  sp-3: "0.75rem"
  sp-4: "1rem"
  sp-5: "1.5rem"
  sp-6: "2rem"
  sp-7: "3rem"
  sp-8: "4.5rem"
  sp-9: "6.5rem"
components:
  button-default:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "0.7rem 1.25rem"
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.md}"
    padding: "0.7rem 1.25rem"
  nav-link:
    textColor: "{colors.ink-2}"
    typography: "{typography.label}"
  chain-step:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "{spacing.sp-4}"
  section-num:
    textColor: "{colors.ink-3}"
    typography: "{typography.label}"
---

# Design System: AI-INVENTORY-OPTIMIZATION

## Overview

**Creative North Star: "The Instrument Bench"** — a research laboratory bench where a serious study is laid out for inspection: premium data product meets editorial storytelling. The page reads like a well-kept lab notebook plus a rigorous data readout: serif-display headlines carry the argument, mono uppercase labels act as instrument markings, and a faint gridpaper underpins the hero. Density is editorial but disciplined; the atmosphere is calm, evidence-first, and explicitly neutral — the site's whole stance is "we don't know which model will win," and the visuals never oversell.

**Key Characteristics:**
- Cool stone paper (`#F4F4F1`) and near-white surfaces, never cream or warm paper.
- Serif (Spectral) argument headlines over sans (Inter) body with mono (Fragment Mono) instrument labels.
- Color is semantic only: each model family and each outcome type has one restrained hue; nothing is decorative.
- Flat-by-default depth: hairline borders, small precise radii (4/8/14px), low offset-blur shadows.
- One deliberate inversion: the Uncertainty section becomes "The Dark Lab" — the only dark surface on the page.

## Colors

A restrained, cooled palette. Paper is cool stone, ink is blue-black; the six semantic hues are muted (steel blue, teal, indigo, violet, green, darkened amber) and appear as text accents, ticks, and washes — never as loud fills.

### Primary
- **Steel Blue** (#35618A): the anchor hue. Traditional-model family (MA/SES/DES/TES), body links, focus rings, the nav active underline.

### Secondary
- **Teal** (#27757A): statistical models (ARIMA/SARIMA).
- **Indigo** (#5B56A0): neural models (LSTM).
- **Violet** (#7A53A6): the LLM — the "most advanced" rung; the hero italicizes "AI" in it.
- **Inventory Green** (#3D7B55): inventory outcomes — the business endpoint.
- **Uncertainty Amber** (#8F5619): darkened for WCAG AA on paper; used for uncertainty/robustness content.

### Neutral
- **Cool Stone Paper** (#F4F4F1): page background.
- **Surface** (#FDFDFB): cards, panels, nav menu, hover surfaces (surface-2 #F7F7F4).
- **Ink** (#161A22): headings, primary buttons (`ink-2` #3B424E sub-text, `ink-3` #5A6270 meta text).
- **Hairlines** (line #D9D8D0, line-2 #C6C4B9): borders and dividers.
- **The Dark Lab** (lab-bg #0F131A, lab-ink #E9E8E2): Uncertainty section only.

### Named Rules
**The Meaning Rule.** Color marks meaning: model family, inventory outcome, uncertainty. No decoration, no gradients, no gratuitous accents. If a color can't be named, it doesn't get used.

## Typography

**Display Font:** Spectral (with Georgia serif fallback) — the argument voice; serif editorial weight at 500–600.
**Body Font:** Inter (with system-ui fallback) — UI and prose; optimized antialiasing.
**Label/Mono Font:** Fragment Mono (with JetBrains Mono / Consolas fallback) — instrument readouts.

**Character:** The pairing is laboratory-meets-editorial: serif display for the claims and questions, quiet sans for reading, and a small uppercase tracked mono voice for everything that is measurement, meta, or navigation.

### Hierarchy
- **Display** (500, clamp(2.6rem→4.4rem), 1.16): the hero research question only.
- **Headline** (600, clamp(1.8rem→2.6rem), 1.16): section titles.
- **Title** (600, clamp(1.15rem→1.4rem), 1.16): card and block titles.
- **Body** (400, 17px, 1.68): prose, capped at 66ch (`--measure`; 48ch narrow).
- **Label** (400, 0.78rem, +0.08em tracked, uppercase): section numbers, nav links, ladder rungs, stamps, axis labels (0.7rem small variant).

### Named Rules
**The Instrument Label Rule.** Every measurement or meta annotation is mono, uppercase, tracked. Two-monogram brand "AI·INV·OPT", "RESEARCH PROPOSAL · V0.1", section numbers — if it reads like an instrument marking, it is mono.

## Layout

A single-column editorial spine capped at 76rem (`--content-max`) with a gutter of `clamp(1.25rem→3.5rem)`. Sections breathe with generous padding `clamp(4.5rem→8.5rem)` vertical rhythm. Section heads are a split grid above 56rem (1.6fr heading / 1fr sub) and stack below. Step/progression flows use a 3-column chain grid (2 below 56rem, 1 below 34rem). The hero ladder is an 8-rung equal grid (4 rungs below 52rem, 2 below 30rem). Full-bleed hero gridpaper `32px` cell; content measure `66ch`; nav fixed height `3.75rem` with `scroll-padding-top` compensating anchors.

## Elevation & Depth

Flat-by-default with tonal layering. Depth comes from hairline borders and subtle offset-blur shadows — never hard block edges or drop shadows on the page frame.

### Shadow Vocabulary
- **shadow-1** (`0 1px 2px rgba(22,26,34,0.05), 0 2px 8px rgba(22,26,34,0.05)`): resting cards (chain steps).
- **shadow-2** (`0 2px 4px rgba(22,26,34,0.06), 0 8px 24px rgba(22,26,34,0.09)`): raised/hover states.

### Named Rules
**The Flat-By-Default Rule.** Surfaces rest flat; elevation is a 1px hairline plus a whisper of shadow, only where structure demands it. The one structural inversion is content, not shadow: the entire Uncertainty section flips to the Dark Lab palette.

## Shapes

Precise, small radii: 4px (sm — stamps, toggles, focus), 8px (md — buttons, cards, chain steps), 14px (lg — larger panels). Hairlines are 1px. The hero titleblock uses a 2px left rule (`line-2`) as an editorial marker. Buttons translate 1px on `:active`; the nav underline grows left-to-right on hover and stays on the active link.

## Components

### Buttons
- **Shape:** 8px radius, 1px border.
- **Default:** surface background, line-2 border, ink text; hover raises to ink-2 border on surface-2.
- **Primary:** ink background, paper text, ink border; hover shifts to ink-2. Active presses down 1px.
- **Embellishment:** optional inline arrow icon, `currentColor` stroke.

### Navigation
- **Shape:** sticky glass bar — paper at 88% with 10px blur; hairline + faint shadow only after scroll.
- **Links:** mono uppercase 0.7rem labels, ink-2 text; hover and `.is-active` turn ink with a 1px steel-blue underline that animates from left (via `::after` `right` transition, 320ms `--ease-out`).
- **Mobile:** hamburger toggle breaks in below 56rem; slide-down menu panel on surface with hairline-divided mono links.

### Cards / Containers (chain steps)
- **Corner Style:** 8px radius.
- **Background:** surface over paper.
- **Shadow:** shadow-1.
- **Border:** 1px line.
- **Internal Padding:** 1rem; content is a grid of `auto 1fr` (number/label + detail), arrows between steps at >56rem.

### Section Heads
- Mono uppercase section number with a 2.5rem hairline rule after it; serif H2; sub text in ink-2 at 66ch.

### Inputs / Fields
None are used on the current surface — intentionally omitted.

### The Ladder (signature instrument)
The hero's model progression: eight equal rungs on a faint axis line, each with a 1px tick, mono model name in its family hue, and a small category caption. Rungs animate in sequence (90ms stagger, 320ms ease-out) respecting `prefers-reduced-motion`. Below: a mono axis reading "+ complexity · + data required".

## Do's and Don'ts

### Do:
- **Do** label every measurement, stamp, and nav item in tracked uppercase mono.
- **Do** keep color semantic — steel blue for traditional, violet for LLM, green for inventory outcomes.
- **Do** cap prose at 66ch and let sections breathe with the full `--section-pad` rhythm.
- **Do** use the Dark Lab inversion for uncertainty content as the page's single dramatic moment.

### Don't:
- **Don't** decorate with color — no gradients, no colorful fills; washes stay at ≈8–12% tint.
- **Don't** add hard block shadows or floating cards without hairlines.
- **Don't** break the ladder's axis metaphor (tick + name + category per rung) into a generic grid.
- **Don't** show invented results, meter fill, or "winner" states — pending is a real state on this site.