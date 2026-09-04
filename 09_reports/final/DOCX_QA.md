# DOCX QA — publication derivative of the frozen report

## Source and method
- Source: working tree at 1837ce9 (contains audit freeze 8802da1 plus the
  final-consistency fix 1837ce9 mandating canonical 2,084.50). Built from the
  final .tex sources; PDF master untouched (sha256 prefix a0323af7d0337f16
  before and after — verified unchanged).
- Pipeline (generators in 11_src/): build_docx.py (copies master, expands all
  45 \cref to typed refs from report.aux's 288 labels, pandoc 3.10.2
  latex->docx with citeproc) -> polish_docx.py (A4, 2.5cm margins, Calibri
  styles, centered figures capped at 6in, Table Grid + header shading, header
  short-title, footer PAGE field, TOC field, core properties) ->
  number_captions.py (prefixes all 28 figure + 9 table captions with aux
  numbers; zero mismatches). One real bug found and fixed in QA:
  number_captions.py raw-string regex matched zero aux labels (all captions
  read "Figure ??"); fixed, rebuilt, now zero `??`.
- DOCX renders to 41 Word pages (vs 44 LaTeX pages; expected — Word reflows,
  appendices use full tables instead of scriptsize chunks).

## Content comparison (programmatic, vs frozen evidence)
- Headline numbers present at PDF-matching frequencies: 1.316, 0.978, 152.83,
  2,084.50 x7, 2,247.46 x5, 2,282.31, 25/27 splits, 9/7/6/5, 22.65%, 3,094 +
  906 fallback, 2,382 s, 112,000. Stale 2,084.49: 0 occurrences.
- Zero LaTeX leakage: no $, no \commands, balanced braces, no label{/citep/
  includegraphics remnants. Zero `??`, zero `[?]`.
- Preserved: hybrid-ARIMA note, 112,000 dependence qualification, Syntetos
  categorization citation (9 Syntetos mentions), LLM future-only statement.
- Structure: 322 paragraphs, 21 H1, 90 H2, 17 tables (9 main + 8 appendix),
  28 embedded figures, captioned Figure 1..28 / Table 1..9; spot-checked
  Fig 19/26/28 caption-vs-body agreement. References render author-date
  (Word convention; PDF uses numbered style).

## Visual QA (via Word's own engine -> docx_visual_qa.pdf)
- Sampled title, at-a-glance/TOC, methodology + Table 1, inventory tables,
  archetype/scatter/heatmap figures, conclusion: no clipping, overflow,
  broken tables, orphaned headings, blank pages, or font problems. Captions
  stay with figures; tables intact with shaded headers.

## Known formatting-only notes (no content impact)
1. Header short-title prints on page 1 (no different-first-page set).
2. TOC is a Word field: right-click > Update Field on first open to populate
   page numbers.
3. Citations are author-date in DOCX vs numbered in PDF (standard
   submission behavior of pandoc citeproc).

## Verdict: PASS — publication-ready DOCX derivative
PDF master unchanged; no research values altered (formatting-only fixes).
