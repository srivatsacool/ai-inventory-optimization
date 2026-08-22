// Evaluation — metrics, robustness dimensions, practicality.

export const FORECAST_METRICS: { code: string; name: string; note: string }[] = [
  { code: 'MAE', name: 'Mean Absolute Error', note: 'Average absolute deviation — interpretable in demand units.' },
  { code: 'MSE', name: 'Mean Squared Error', note: 'Penalizes large errors quadratically.' },
  { code: 'RMSE', name: 'Root Mean Squared Error', note: 'MSE returned to demand units.' },
  { code: 'sMAPE', name: 'Symmetric Mean Absolute Percentage Error', note: 'Scale-free; used where appropriate.' },
  { code: 'MASE / RMSSE', name: 'Scaled errors', note: 'Used where justified for cross-series evaluation.' },
];

export const INVENTORY_METRICS: { code: string; name: string; note: string }[] = [
  { code: 'TC', name: 'Total inventory cost', note: 'The headline business-level outcome.' },
  { code: 'HC', name: 'Holding cost', note: 'Storage, capital tied up, handling.' },
  { code: 'SC', name: 'Stockout cost', note: 'Consequences of unmet demand.' },
  { code: 'SR', name: 'Stockout rate / frequency', note: 'How often the system runs dry.' },
  { code: 'SL', name: 'Service level', note: 'Share of demand satisfied without stockout.' },
  { code: 'AI', name: 'Average inventory', note: 'Capital committed on average.' },
  { code: 'OF', name: 'Order frequency', note: 'Replenishment activity under the policy.' },
];

export const PRACTICALITY_DIMENSIONS: { label: string; note: string }[] = [
  { label: 'Runtime', note: 'Time to fit, forecast, and simulate.' },
  { label: 'Computational requirements', note: 'Hardware and memory footprint.' },
  { label: 'Model complexity', note: 'Parameters, configuration, and tuning burden.' },
  { label: 'Interpretability', note: 'How explainable each forecast is.' },
  { label: 'Reproducibility', note: 'Determinism and version control of outputs.' },
];

export const ROBUSTNESS_DIMENSIONS: { label: string; range: string; note: string }[] = [
  { label: 'Lead time', range: 'Low → Medium → High', note: 'Does the winner hold as replenishment slows?' },
  { label: 'Holding cost', range: 'Low → Medium → High', note: 'Does the winner hold as carrying cost rises?' },
  { label: 'Stockout cost', range: 'Low → Medium → High', note: 'Does the winner hold when stockouts get expensive?' },
];

export const COMMON_POLICY_PRINCIPLE = {
  title: 'One policy for every model',
  body: 'Forecasting models should primarily differ in the forecasts they provide, while downstream inventory decision rules remain standardized wherever practical. Otherwise we would be comparing Model A + Policy A against Model B + Policy B — and the result would be uninterpretable.',
};