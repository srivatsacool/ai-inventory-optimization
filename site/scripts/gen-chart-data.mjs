#!/usr/bin/env node
// gen-chart-data.mjs — Generates frozen chart data JSON from research result CSVs.
// Data source of truth: 06_results/ (frozen at v1.0-evidence-freeze).
// No computation of new numbers — just restructuring for the frontend charts.
import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SITE_ROOT = resolve(__dirname, '..');
const PROJECT_ROOT = resolve(SITE_ROOT, '..');
const DST = resolve(SITE_ROOT, 'src', 'data');
mkdirSync(DST, { recursive: true });

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const header = lines[0].split(',');
  return lines.slice(1).map(line => {
    const cells = line.split(',');
    const row = {};
    header.forEach((h, i) => { row[h] = cells[i]; });
    return row;
  });
}

// --- Inventory by model (both datasets) ---
const inventory = parseCsv(
  readFileSync(resolve(PROJECT_ROOT, '06_results', 'inventory', 'inventory_by_model.csv'), 'utf8')
);
const inventoryCharts = {};
for (const ds of ['m5', 'store_item_demand']) {
  const rows = inventory.filter(r => r.dataset === ds).map(r => ({
    model: r.model,
    holding: +(+r.total_holding_cost).toFixed(2),
    stockout: +(+r.total_stockout_cost).toFixed(2),
    total: +(+r.total_cost).toFixed(2),
    service: +(+r.service_level * 100).toFixed(1),
    avgInventory: +(+r.average_inventory).toFixed(2),
  }));
  rows.sort((a, b) => a.total - b.total);
  inventoryCharts[ds] = rows;
}

// --- Forecast metrics by model (both datasets) ---
// Sources: baselines/metrics_by_model.csv (traditional+statistical) and
// lstm/metrics_by_model.csv (the neural rung lives in its own directory).
const metrics = [
  ...parseCsv(
    readFileSync(resolve(PROJECT_ROOT, '06_results', 'baselines', 'metrics_by_model.csv'), 'utf8')
  ),
  ...parseCsv(
    readFileSync(resolve(PROJECT_ROOT, '06_results', 'lstm', 'metrics_by_model.csv'), 'utf8')
  ),
];
const forecastCharts = {};
for (const ds of ['m5', 'store_item_demand']) {
  const rows = metrics.filter(r => r.dataset === ds).map(r => ({
    model: r.model,
    mae: +(+r.MAE).toFixed(3),
    mase: +(+r.MASE).toFixed(3),
    rmse: +(+r.RMSE).toFixed(3),
  }));
  rows.sort((a, b) => a.mase - b.mase);
  forecastCharts[ds] = rows;
}

// --- Sensitivity grid: winner per policy cell ---
const sens = parseCsv(
  readFileSync(resolve(PROJECT_ROOT, '06_results', 'sensitivity', 'sensitivity_grid.csv'), 'utf8')
);
// policies = unique (dataset, lead_time, service_target, P) combos; winner = min total_cost per cell
const cells = new Map();
for (const r of sens) {
  const key = `${r.dataset}|${r.lead_time}-${r.service_target}-${r.P}`;
  if (!cells.has(key)) cells.set(key, []);
  cells.get(key).push({ model: r.model, dataset: r.dataset, cost: +(+r.total_cost).toFixed(2) });
}
const wins = {}; // dataset -> model -> count
const policies = [];
for (const [key, models] of cells) {
  const ds = models[0].dataset;
  const winner = models.reduce((a, b) => (b.cost < a.cost ? b : a));
  policies.push({ policy: key.split('|')[1], dataset: ds, winner: winner.model, cost: winner.cost });
  wins[ds] = wins[ds] || {};
  wins[ds][winner.model] = (wins[ds][winner.model] || 0) + 1;
}

const out = {
  generated: 'frozen-v1.0-evidence-freeze',
  inventory: inventoryCharts,
  forecast: forecastCharts,
  sensitivityWins: wins,
  policies: policies.length,
};
writeFileSync(resolve(DST, 'charts.json'), JSON.stringify(out, null, 2));
console.log('Wrote src/data/charts.json');
console.log('  M5 models:', inventoryCharts.m5.length, '| Store models:', inventoryCharts.store_item_demand.length);
console.log('  Policy cells:', policies.length);
console.log('  M5 wins:', JSON.stringify(wins.m5));
console.log('  Store wins:', JSON.stringify(wins.store_item_demand));
