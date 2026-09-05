# Architecture — HOME / LAB / DOC (P0 foundation, 2026-09-05)

One research product, three modes. Static site (Astro) owns HOME + DOC shells
and mounts the independently hosted Streamlit runtime at LAB.

## Surfaces and responsibilities

- HOME (`site/src/pages/index.astro`) — narrative only. Real copy from
  `01_research/research_proposal.md`, git-history content model, and frozen
  thesis numbers. No computation, no Streamlit logic.
- LAB (`site/src/pages/lab.astro` + `site/src/components/LabEmbed.astro`) —
  embeds the Streamlit app via iframe (`?embed=true&toolbarMode=minimal`).
  No research logic in Astro, ever.
- DOC (`site/src/pages/doc.astro`) — native `<object>` PDF reader shell with
  chapter list mirroring `report.tex`, download + new-tab controls.
  pdf.js upgrade path open; not built in P0.
- Shared (`site/src/styles/tokens.css`, `BaseLayout.astro`) — values
  transcribed from `.impeccable/design.json`, the website design contract.

## Canonical paths

- PDF source of truth: `09_reports/final/report.pdf` (tracked).
  `research_report.pdf` was a byte-identical duplicate — removed (P0).
- Served artifact: `/doc/research-report.pdf` = `site/public/doc/research-report.pdf`,
  produced by `site/scripts/copy-pdf.mjs` (`npm run copy-pdf`, also `prebuild`).
  It is a deployment artifact. Never edit it; rebuild it.
- Streamlit boundary: `site/src/config.mjs` → `STREAMLIT_URL`
  (or `ASTRO_STREAMLIT_URL` env). Empty = unconfigured → LabEmbed shows the
  honest "deployment pending" fallback. No fake embed.

## Deployment model

- PUBLIC WEBSITE: Astro static `site/dist/` → Cloudflare Pages → existing
  qzz.io domain. No adapter. Redeploy path from the old Astro project to be
  rediscovered (no wrangler/pages config in repo).
- RESEARCH LAB: Streamlit (`app/`, `app_data/`) → independent Streamlit-capable
  host (UNDECIDED — external dependency) → framed by `/lab`.
- DOCUMENT: canonical PDF served through `/doc` reader.

## Research-integrity boundaries (do not cross)

- `app/lib/frozen_loader.py`, THESIS_ROWS, frozen CSVs, report data,
  validators, number-sheet generation, experiment protocol: untouched by P0.
- Parked redesign (not lost): restored 2026-09-05 post-clarification
  (stash popped; `app/lib/lab.py` copied back from
  `.tmp/parked-lab-redesign/`). Lab is a first-class premium dashboard surface.

## Validation performed (P0)

- `astro build`: 3 pages, 0 errors. All routes 200: /, /lab/, /doc/,
  /doc/research-report.pdf (3,902,413 bytes, md5 == canonical).
- Active nav verified per route; zero browser console errors; screenshots in
  `.impeccable/review/site-{home,lab,doc}-1280.png`.
- `11_src/test_inventory_policy.py`: 0 failures. Thesis lock: 7/7 OK.
- `git status`: no frozen evidence modified (only PDF dedup + new site/ files).

## Open dependencies

1. Streamlit host URL (gates the real /lab embed).
2. Cloudflare Pages project wiring for site/dist (gates public deploy).
3. Future visual redesign (explicitly out of scope for P0).
