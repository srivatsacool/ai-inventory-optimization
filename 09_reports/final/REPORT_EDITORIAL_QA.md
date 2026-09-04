# REPORT EDITORIAL QA — academic rewrite pass

## Scope
Prose-only revision of 09_reports/final/sections/{front,sec1-sec8}.tex.
No change to research, methods, figures, tables, numbers, rankings, verdicts,
protocol, or configurations. Appendix .tex files untouched except zero edits
(none required; already technical).

## Writing changes
- Em-dashes: 99 -> 3 (two explanatory breaks + one subsection-title separator;
  all standard academic uses). Replaced with periods, commas, semicolons, parentheses.
- Removed ~25 flagged marketing/rhetorical items, including: "live or die,"
  "smartest forecaster," "cheapest stocker," "dumbest method," "quiet
  overachiever," "cautionary tale," "untouchable," "microscope finds everything
  significant," "astronomically significant," "fast car with weak brakes,"
  "bank M5-LSTM; rent Store-MA," "exonerate as well as convict," "same paranoia,"
  "shelf, not scoreboard," "Bottom line," "trust map," "center of gravity,"
  "daylight," "drown," "p-value theater," "too close to call." Replaced with
  neutral equivalents (e.g., "lowest-error forecaster," "lowest-cost inventory
  input," "simplest benchmark," "indistinguishable for practical purposes").
- Section 3 rewritten from formulaic Does/Why/Implementation/Role blocks into
  flowing methodological paragraphs; every implementation detail retained
  (windows w14/w7 with validation values, alphas, ARIMA/SARIMA orders,
  pre-check rule, LSTM L28/chronological/seed, Croston alphas, scope exceptions).
- Central-forecast-vs-inventory restatement trimmed in 4.7/4.8 closings, 6.1,
  8.2 (full treatment retained in abstract, at-a-glance, 4.9, 5.1, 8.4).
- Overconfident scope language qualified ("within the evaluated model set,"
  "under the default cost ratio," "conditional on stated conditions").
- WAPE history compressed to a methodological note (4.19 item 6 + 2.8/6.7
  rationale); no debugging narrative remains.
- Hypotheses, verdicts, at-a-glance finding, LLM non-execution statement: preserved verbatim in content.

## Methodological qualifications added (no results changed)
- 2.9: dependence paragraph — 112,000 paired errors are repeated dependent
  observations (500 series x 8 origins x 28 steps, overlapping windows); nominal
  count is not effective independent sample size; reported tests are the
  preregistered paired design.
- 5.6: dependence reinforces weighting effect sizes over p-values.
- 7.9 (new 7.9 Statistical dependence) + 7.10 item 7: series-level and
  block-bootstrap inference as future robustness extension. (Section numbering:
  LLM moved to 7.10; TOC/labels regenerate automatically.)

## References
- Added: none. All 11 existing citations verified used and sufficient for the
  methods actually applied. No fabricated sources.
- FLAGGED FOR HUMAN REVIEW (candidate additions requiring external
  verification; NOT added): M5 Uncertainty competition paper (for the
  probabilistic-forecasting context, if the author wants it); Syntetos, Boylan
  & Croston review literature on intermittent demand; Fildes & Goodwin on
  forecasting practice/implementation gap; recent block-bootstrap-forecast-evaluation
  references to underpin the proposed series-level inference extension.

## QA results
- Compile: pdflatex x3 + bibtex, EXIT=0, zero `!` errors, zero undefined references.
- Refs: 144 labels / 31 refs all defined; 11 cites = 11 bib entries.
- Numbers: headline values spot-checked against frozen CSVs (MASE boards, both
  inventory rankings, spotlight dz/p, 25/27 + 9/7/6/5, convergence, protocol) — intact.
- Guards: full500 SARIMA, pooled archetype WAPE, Smooth n=1 cap, LLM future-only,
  Store ranking + fragility pairing, no pre-hardening/subset artifacts — intact.
- Layout: 44 pages (was 43; +1 from slightly longer methodological paragraphs),
  28 figures. Visual QA of rendered pages (title, abstract, boards, tables,
  robustness, appendix math): clean, scholarly tone confirmed.
- No unsupported claims introduced; no AI-detector gaming; no deliberate awkwardness.

## Files modified
- sections/front.tex, sec1-sec8.tex (full prose rewrite)
- research_report.pdf + report.pdf (recompiled)
- (New) REPORT_EDITORIAL_QA.md (this file)

## Issues requiring human review
1. Candidate references: the verified Syntetos-Boylan-Croston (2005) categorization paper has been ADDED (2.5 + refs.bib, 12 entries). Remaining unverified candidates (Fildes/Goodwin, block-bootstrap refs) stay out per instructions.
2. Em-dash reduction reached 97% (3 remain, all legitimate); confirm tone target met.
3. DOCX was NOT regenerated (per instructions); the committed .docx predates the editorial + correction passes and is stale relative to the PDF. Regenerate on approval.

## Peer-review correction log (B1-B3, I1-I5: all resolved, edit-only, no reruns)
- B1 (4.7): SES sentence now reads second-lowest stockout (21.00, after Croston 20.28) and third-highest service (93.6%, after Croston, Seasonal Naive). Source-verified.
- B2 (4.8): MA stockout frequency now "low (10.72, fourth-lowest)". Source-verified.
- B3 (4.7): "ten times" ratio clause deleted; qualitative amplification point retained without cross-unit comparison.
- I1: Store LSTM total 2,247.45 -> 2,247.46 in all five locations (front, 4.8 prose, Table 7, 4.12, 8.2); Table 7 now internally consistent (1,157.70 + 1,089.76).
- I2: hybrid-evaluation note added below Table 3 (3,094 fitted + 906 fallback; pointer to 4.13).
- I3: Appendix B carries the DM/bootstrap dependence-inheritance sentence.
- I4: categorization reference added and cited in 2.5 (verified real via web search).
- I5: 4.19 item 2 now reads "DES and TES carry roughly double (1.7x and 2.2x, respectively)".
- Post-correction compile: EXIT=0, zero errors, zero undefined refs, 44 pages, 12 bib entries; touched pages visually spot-checked (hybrid note, Table 6/7 consistency).
