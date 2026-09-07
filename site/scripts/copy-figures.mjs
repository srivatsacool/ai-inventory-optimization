// Deployment artifact — NOT a second source of truth.
// Copies the canonical publication figures 09_reports/final/figures/ into the
// static site as public/figures/*.png. Never edit the copies; rebuild them.
// Run: npm run copy-figures  (also runs automatically as part of `prebuild`).
import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const srcDir = join(root, '09_reports', 'final', 'figures');
const destDir = join(root, 'site', 'public', 'figures');

// Key figures served by the site (subset of the full figure set). The hero
// chart and the figure set advertised on the home dashboard.
const FIGURES = [
  '05_forecast_vs_inventory_scatter.png', // hero chart
  '01_total_cost_comparison.png',         // inventory cost comparison
  '01_comparison_MAE.png',                // forecast accuracy comparison
  '02_service_level_comparison.png',      // service levels
  '11_forecasting_model_ladder.png',      // model ladder
];

mkdirSync(destDir, { recursive: true });
for (const f of FIGURES) {
  copyFileSync(join(srcDir, f), join(destDir, f));
  console.log(`Figure artifact staged: ${f}`);
}