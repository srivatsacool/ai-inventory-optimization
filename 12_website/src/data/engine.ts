// Inventory Decision Engine — hero visualization content.
// v0.1 — conceptual freeze. NO experimental results exist yet.
// Every performance-facing value is a neutral placeholder ("—")
// or explicitly labeled ILLUSTRATIVE. Real results will replace
// these without redesigning the UI.

export const ENGINE = {
  title: 'Inventory Decision Engine',
  status: 'Research question active',

  chartTitle: 'Demand signal',
  chartNote: 'Schematic — not data',
  legend: {
    actual: 'Actual demand',
    forecast: 'Forecast',
    uncertainty: 'Uncertainty',
  },

  comparisonTitle: 'Forecast comparison',
  illustrative: 'Illustrative — not research results',
  comparison: [
    { name: 'ARIMA', hue: 'stat', metric: '—', note: 'Statistical benchmark' },
    { name: 'LSTM', hue: 'neural', metric: '—', note: 'Neural approach' },
    { name: 'LLM', hue: 'llm', metric: '—', note: 'Language-model forecast' },
  ],

  datasetTitle: 'Dataset snapshot',
  datasets: [
    {
      name: 'Walmart M5',
      detail: 'Demand forecasting benchmark',
      status: 'Dataset selected',
      sub: 'Details pending',
    },
    {
      name: 'Grocery dataset',
      detail: 'Retail demand dataset',
      status: 'Dataset selected',
      sub: 'Details pending',
    },
  ],

  policyTitle: 'Inventory policy recommendation',
  policy: [
    { name: 'Safety stock', value: '— units' },
    { name: 'Order quantity', value: '— units' },
    { name: 'Service level', value: '— %' },
  ],

  impactTitle: 'Decision impact',
  impact: [
    { name: 'Total cost', value: '—', hint: 'tracked' },
    { name: 'Stockout rate', value: '—', hint: 'tracked' },
    { name: 'Service level', value: '—', hint: 'tracked' },
  ],

  scope: [
    { value: '8', label: 'Model families' },
    { value: '2', label: 'Datasets' },
    { value: '3', label: 'Decision metrics' },
    { value: '1', label: 'Research question' },
  ],
} as const;