# FINAL CONSISTENCY QA — publication correction freeze

## Fix 1: canonical Store Moving Average inventory cost
- Frozen source: 06_results/inventory/inventory_by_model.csv value 2084.5013831777087
  (number sheet records 2084.501383). Standard rounding to two decimals: 2,084.50.
- Previous report state: inconsistent (2,084.49 in abstract, at-a-glance, 3.3, 8.2,
  appendix lookup; 2,084.50 in 4.8 prose and Table 7).
- Corrected: all five 2,084.49 occurrences -> 2,084.50. Post-fix grep: 2,084.49 = 0
  in .tex; 2,084.50 present in front.tex, sec3.tex, sec4.tex (prose + Table 7),
  sec8.tex, appI_L.tex. PDF text extraction: 2,084.49 = 0, 2,084.50 = 7.
- Table 7 cross-check: holding 1,276.10 + stockout 808.40 = 2,084.50 internally consistent.

## Fix 2: cover provenance line
- Before: "Evidence-freeze commit edb42ad | Final public report" (implied edb42ad is final).
- After: "Evidence freeze: edb42ad | Publication correction freeze: 8802da1".
- Historical freeze-range/commit-list mentions in 2.14 and Appendix I left intact
  (factually correct as history). PDF text: edb42ad x3 (cover + two historical
  mentions), 8802da1 x1 (cover). Visually verified on title page.

## Compilation
- pdflatex x3 + bibtex: all EXIT=0, zero `!` errors, zero undefined references,
  no bibtex errors/warnings. 44 pages, ~3.9 MB. 28 figures, 9 main + 7 appendix
  tables, 12 bib entries (unchanged from correction freeze).

## Visual inspection (rendered cover, at-a-glance/TOC, Table 6/7 + 4.8, conclusion)
- Cover provenance line, abstract 2,084.50, at-a-glance 2,084.50: clean.
- Table 7 (MA 2,084.50; LSTM 2,247.46) and 4.8 prose ("fourth-lowest" fix from
  prior freeze intact): clean, internally consistent.
- Conclusion (2,084.50, 9/7/6/5, dependence reference): clean.
- No layout regressions; no other editorial changes made.

## Scope confirmation
- No research, methodology, ranking, figure, table-value, reference, or evidence
  changes. DOCX not regenerated (stale; awaiting separate approval).
