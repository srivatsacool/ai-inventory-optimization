// Experiment pipeline stages — the master research flow.

export interface Stage {
  id: string;
  label: string;
  detail: string;
}

export const EXPERIMENT_PIPELINE: Stage[] = [
  { id: 'data', label: 'Data', detail: 'Two retail demand environments, documented and versioned.' },
  { id: 'explore', label: 'Exploration', detail: 'EDA identifies demand characteristics and representative series.' },
  { id: 'preprocess', label: 'Preprocessing', detail: 'Raw → interim → processed, with temporal integrity preserved.' },
  { id: 'forecast', label: 'Forecasting', detail: 'The full ladder — MA to LLM — under comparable conditions.' },
  { id: 'eval', label: 'Forecast evaluation', detail: 'Metrics on the same evaluation periods for every model.' },
  { id: 'inventory', label: 'Inventory simulation', detail: 'One common policy translates forecasts into outcomes.' },
  { id: 'robust', label: 'Robustness', detail: 'Sensitivity analysis across operating assumptions.' },
  { id: 'compare', label: 'Final comparison', detail: 'Accuracy, inventory performance, and practicality together.' },
];

// The conceptual inventory simulation chain.
export const INVENTORY_CHAIN: Stage[] = [
  { id: 'fc', label: 'Forecast', detail: 'Model output for the decision horizon.' },
  { id: 'ltd', label: 'Lead-time demand', detail: 'Expected demand over the replenishment lead time.' },
  { id: 'ss', label: 'Safety stock', detail: 'Buffer for demand variability and forecast error.' },
  { id: 'rop', label: 'Reorder point', detail: 'The inventory level that triggers an order.' },
  { id: 'order', label: 'Order decision', detail: 'Quantity and timing under the common policy.' },
  { id: 'sim', label: 'Inventory simulation', detail: 'Costs, stockouts, and service level over time.' },
];

// The LLM experiment chain.
export const LLM_CHAIN: Stage[] = [
  { id: 'hist', label: 'Historical demand', detail: 'Structured, recent demand only — never future values.' },
  { id: 'ctx', label: 'Context preparation', detail: 'Time information, series identity, horizon.' },
  { id: 'prompt', label: 'Structured prompt', detail: 'A versioned, controlled experimental artifact.' },
  { id: 'llm', label: 'Local LLM via Ollama', detail: 'General-purpose model on local hardware.' },
  { id: 'out', label: 'Numerical forecast', detail: 'Structured output — validated, never silently repaired.' },
  { id: 'val', label: 'Validation', detail: 'Shape, numeric, ordering, and time-alignment checks.' },
  { id: 'inv', label: 'Inventory simulation', detail: 'Same common policy as every other model.' },
];

export const OPEN_PARAMETERS: { area: string; howDecided: string }[] = [
  { area: 'Series / SKU selection', howDecided: 'Predefined representativeness criteria after EDA.' },
  { area: 'Forecasting horizon', howDecided: 'Linked to the inventory decision problem and lead time.' },
  { area: 'Train / validation / test periods', howDecided: 'Time-based splits after dataset understanding.' },
  { area: 'Rolling evaluation', howDecided: 'Candidate methodology, subject to computational feasibility.' },
  { area: 'Seasonal structure', howDecided: 'Identified through EDA, not assumed.' },
  { area: 'LSTM architecture & hyperparameters', howDecided: 'Validation-driven range, then selection. Complexity must earn its place.' },
  { area: 'Ollama model', howDecided: 'Hardware, context length, numeracy, speed, reproducibility.' },
  { area: 'LLM prompt design', howDecided: 'A controlled, versioned artifact — no future demand in prompts.' },
  { area: 'Lead time', howDecided: 'Dataset characteristics, literature, realistic retail assumptions, sensitivity.' },
  { area: 'Holding & stockout costs', howDecided: 'Normalized/assumed parameters, explicitly documented.' },
  { area: 'Service-level definition', howDecided: 'Formal definition adopted with the simulation design.' },
  { area: 'Inventory policy parameters', howDecided: 'One common policy; values justified before simulation.' },
  { area: 'Statistical testing', howDecided: 'Selected after the experimental unit and repeated-measures structure are known.' },
  { area: 'Sensitivity ranges', howDecided: 'Low–medium–high across material assumptions.' },
];