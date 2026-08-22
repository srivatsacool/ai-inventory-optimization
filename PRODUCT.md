# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Astro (existing codebase — `12_website/`, dev server via `bun run dev`)

## Users

- **Primary: recruiters and portfolio audiences.** They land here to judge how the author frames, structures, and communicates research. Success = quick grasp of the study's design, rigor, and neutrality, and a lasting impression of the author's thinking.
- Secondary: academic supervisor / committee (study design, rigor, neutrality), and the research community (idea communication and engagement). Not confirmed to be primary by the user, so they remain secondary.

## Product Purpose

A research-communication layer for the AI Inventory Optimization study: a single-page proposal website ("Research Proposal — v0.1") that presents the study's framing — from traditional forecasting to LLM-based approaches — with an explicitly neutral, evidence-driven stance. Success now = communicating the *conceptual freeze* clearly: the study design is locked, experimental parameters are intentionally open and governed by an explicit decision framework, and no results exist yet (nothing fabricated).

## Positioning

What neighboring pages cannot truthfully copy: the site states **"We don't know which model will win"** and shows results as pending. It sells the rigor of the *design and the question*, not results — a research proposal that is honest about its own uncertainty and about inventory being the business endpoint (forecast accuracy is a means, not the goal).

## Operating Context

- The site is one layer of a living research workflow: `00_project/decisions.md` (methodological decision register) and `01_research/research_proposal.md` (single source of truth, frozen at conceptual level v0.1) feed the website content.
- The project will progress through 12 roadmap phases (the site currently marks Phase 01 — Foundation — as NOW); website result sections must update as experiments produce real evidence, never before.
- Dedicated Astro site with 17 sections: hero, research question, why-inventory, model evolution, datasets, experiment design, forecasting evaluation, inventory simulation, inventory metrics, LLM experiment, uncertainty, robustness, practicality, roadmap, expected contribution, references, closing.

## Capabilities and Constraints

- Single-page Astro site (`12_website/`), one route (`src/pages/index.astro`), composed of 16+ components; data centralized in `src/data/*.ts`.
- Model ladder is fixed: MA → SES → DES → TES → ARIMA → SARIMA → LSTM → LLM (local via Ollama).
- Datasets locked at dataset level: Walmart M5 (primary) + Corporación Favorita (secondary robustness).
- Evaluation is three-dimensional: forecast accuracy, inventory outcomes, practicality — one common inventory policy so differences are attributable to forecasts.
- **Constraint (hard):** no fabricated conclusions, rankings, or results. "Results pending" states are real. LLM prompts must never leak future demand. Simulated inventory is labeled simulated, not presented as real operations.
- Open experimental parameters (series selection, horizon, costs, service level, LSTM architecture, Ollama model, prompt design, etc.) are deliberately undecided and must be finalized through EDA → literature → validation → feasibility → evidence, each recorded in the decision log.

## Brand Commitments

- Name: **AI·INV·OPT** (AI-INVENTORY-OPTIMIZATION); footer: "AI-INVENTORY-OPTIMIZATION · 12_WEBSITE".
- Title: "From Traditional Forecasting to Large Language Models: Evaluating AI-Based Inventory Optimization".
- Stance: neutral by design — "Do not assume that the most sophisticated model is the best model" (confirmed decision).
- Labeling: "RESEARCH PROPOSAL · V0.1", "Conceptual freeze — no results yet".

## Evidence on Hand

- `01_research/research_proposal.md` — frozen proposal v0.1 (locked sections + Section 7 open-parameter framework).
- `00_project/decisions.md` — confirmed decisions incl. title, research question, model progression, datasets, evaluation philosophy, inventory-as-endpoint, neutrality principle, conceptual freeze.
- `12_website/` — full implemented site (Astro) with all copy, data files, components.
- **Absent (must never fabricate):** experimental results, real rankings, literature fully verified (bibliography is labeled "starting, not final").

## Product Principles

1. **No fake results.** The site communicates the design and the question; outcomes are earned by evidence, never invented.
2. **Neutrality is the posture.** The study — and the site — must not assume the LLM or the most sophisticated model wins.
3. **Inventory is the endpoint.** Forecasting accuracy is a means; the business outcome and its assumptions carry the interpretation.
4. **Open parameters are a feature, not a gap.** Intentional openness is presented with the decision framework that governs it.
5. **Every claim is traceable.** Content maps to the proposal and decision log; nothing is asserted off-record.

## Accessibility & Inclusion

No product-specific requirement established. Default to inclusive baseline (semantic HTML, contrast, keyboard access) as the implementation allows.