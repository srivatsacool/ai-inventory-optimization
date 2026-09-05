// Deployment artifact — NOT a second source of truth.
// Copies the canonical publication 09_reports/final/report.pdf into the static
// site as public/doc/research-report.pdf. Never edit the copy; rebuild it.
// Run: npm run copy-pdf  (also runs automatically as `prebuild`).
import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const src = join(root, '09_reports', 'final', 'report.pdf');
const dest = join(root, 'site', 'public', 'doc', 'research-report.pdf');

mkdirSync(dirname(dest), { recursive: true });
copyFileSync(src, dest);
console.log(`PDF artifact staged: ${dest}`);
