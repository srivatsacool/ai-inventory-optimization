// modelColors.js — the 12-model data palette from MASTER.md §2.
// Single frontend source of truth; winners render full saturation, others 55%.
export const MODEL_COLORS = {
  'Naive': '#9D4EDD',
  'Seasonal Naive': '#C77DFF',
  'Moving Average': '#2A9D8F',
  'SES': '#43AA8B',
  'DES': '#577590',
  'TES': '#35618A',
  'ARIMA': '#E76F51',
  'SARIMA': '#F4A261',
  'Croston': '#E9C46A',
  'SBA': '#BC6C25',
  'TSB': '#6D597A',
  'LSTM': '#D1495B',
};

export function modelColor(name) {
  if (MODEL_COLORS[name]) return MODEL_COLORS[name];
  const key = String(name).trim().toUpperCase().replace(/\s+/g, '');
  const hit = Object.entries(MODEL_COLORS).find(
    ([m]) => m.toUpperCase().replace(/\s+/g, '') === key
  );
  return hit ? hit[1] : '#4A505C'; // ink-soft fallback (MASTER.md §1)
}

// Opacity language: winner 1.0 · context 0.55 · dimmed-on-hover 0.25
export const OPACITY = { winner: 1.0, context: 0.55, dim: 0.25 };
