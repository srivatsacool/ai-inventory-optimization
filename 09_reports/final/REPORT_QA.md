# REPORT QA — LaTeX/PDF build

## Compilation
- Engine: MiKTeX pdfTeX 4.23. Passes: pdflatex x3 + bibtex, final pass EXIT=0, zero `!` errors.
- Output: research_report.pdf (copy of report.pdf), 43 pages, ~3.9 MB.
- Refs: 25/25 cleveref targets defined (checked programmatically). Citations: 11/11 resolve, 0 natbib warnings, 0 undefined references.
- Overfull hboxes: 8 remaining, all <20pt (mono filenames in body/appendix). No text lost; cosmetic only.

## Counts
- Figures in main text: 28 (FIG-01..FIG-28 per figure_audit.csv; all files verified present, no basename collisions).
- Main tables: 9 (T-01 protocol, T-02 taxonomy, T-03 M5 forecast, T-04 Store forecast, T-05 spotlight, T-06 M5 inventory, T-07 Store inventory, T-08 robustness, T-09 convergence).
- Appendix tables: 7 (gates x2, pairs x3, winners x2). Bibliography: 11 entries, all cited.

## Numerical cross-checks (against data/final_number_sheet.csv + source CSVs)
- M5 MASE: LSTM 1.316 / MA 1.346 / SES 1.351 / TSB 1.369. Store MASE: LSTM 0.978 / SARIMA-full500 1.055 / SNaive 1.183. All present.
- Inventory M5: 152.83 / 158.83 / 159.31 / 160.66 / 165.13 / 174.81 / 192.55 / 194.60 / 200.75 / 268.80 / 346.67. Store: 2084.49 / 2113.82 / 2128.14 / 2247.45 / 2282.31 / 2320.87 / 2700.37 / 2779.64 / 3419.88. All present.
- Spotlight: M5 LSTM-TSB dz -0.031 Holm p~2e-10; Store LSTM-MA dz -0.29. MA-SES DM disagreement footnoted.
- Robustness: M5 LSTM 25/SES 2 (L3/P10 corner documented); Store 9/7/6/5. Grid recomputed programmatically.
- Convergence: M5 ARIMA 22.65% pre-check / 0 optimizer fails; Store 0; SARIMA full500 4000/4000, 2382 s.
- Protocol: 1034/121 (leap day)/83, H28, 8 origins, seed 42, 112000 per model-dataset.

## Content guards (all verified in prose)
- Store SARIMA = full500 everywhere (8.45/1.055/2282.31); subset (8.31) labeled exploratory, never headlined.
- WAPE: model-level per-series-mean vs archetype pooled-ratio distinction stated; 2e9 episode disclosed as fixed intermediate.
- Smooth n=1: anecdotal-only cap stated in 4.11, 6-scope, 7.6, appendix.
- LLM: appears ONLY in 7.9 (future work) + abstract/scope one-liners stating non-execution. Zero LLM numbers.
- Store ranking always paired with fragility verdict (4.8 warning, T-07 caption, 4.16, discussion).
- No pre-hardening numbers: phase1_*.csv, _pre_hardening_backup, 12_notebooks_pdf, subset panels never cited; 3 rejected figures excluded.

## Corrections applied during build (empirical, source-verified)
- Variable-forecast-MAE best = SES 1.799 (three-way tie within 0.007), not LSTM; Moderate = SES 2.634 (both verified in archetype_metrics.csv).
- Archetype-inventory crown: LSTM takes Highly Intermittent (64.52) + Intermittent (147.94); MA takes Variable (285.93); SBA takes Moderate (383.59) (verified in sensitivity_by_archetype_m5.csv).
- Store policy geography enumerated from grid: short leads MA/DES, mid SES/MA, long Naive/SES, LSTM zero Store cells.

## Visual QA (rendered 8/43 pages at 60dpi: 1,2,3,7,14,21,29,36)
- Title/abstract/keywords/RQ/hypotheses/at-a-glance: clean. TOC: clean, links live.
- Figures (ACF/PACF, inventory-link, Store MAE rebuild, heatmaps implied): render correctly with captions.
- Tables (spotlight T-05, robustness T-08): booktabs clean, footnote legible.
- Appendix (gates/pairs/winners chunks, metric math): clean at scriptsize.

## Toolchain notes
- MiKTeX kernel 2025-11-01 is incompatible with its shipped longtable.sty and the on-disk tabularray; appendix long tables were converted to chunked regular tabulars (generator: 11_src/gen_appendix_tables.py). No content lost: 91 pairs / 44 gates / 54 winner cells all printed.
- Stale fragments gen_pairs.tex, gen_winners.tex, gen_gates.tex (longtable era) removed from appendix dir.

## Remaining issues
- None blocking. Minor: 8 sub-20pt overfulls (mono paths); appendix tables at scriptsize by design.
- DOCX conversion: NOT started (awaiting approval, per instructions).
